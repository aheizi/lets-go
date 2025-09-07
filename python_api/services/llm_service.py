import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class DoubaoLLMService:
    """豆包大模型服务类"""
    
    def __init__(self):
        self.api_key = os.getenv('DOUBAO_API_KEY')
        self.base_url = os.getenv('DOUBAO_BASE_URL')
        self.model = os.getenv('DOUBAO_MODEL')
        
        if not all([self.api_key, self.base_url, self.model]):
            raise ValueError("豆包API配置不完整，请检查环境变量")
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """发送请求到豆包API"""
        start_time = time.time()
        request_id = f"req_{int(time.time() * 1000)}"
        
        payload = {
            'model': self.model,
            'messages': messages,
            **kwargs
        }
        
        # 记录请求开始日志
        logger.info(f"[{request_id}] 开始调用豆包API")
        logger.debug(f"[{request_id}] 请求参数: model={self.model}, messages_count={len(messages)}, kwargs={kwargs}")
        
        # 记录消息内容（仅在debug模式下）
        for i, msg in enumerate(messages):
            logger.debug(f"[{request_id}] Message {i}: role={msg.get('role')}, content_length={len(msg.get('content', ''))}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                response_data = response.json()
                
                # 计算响应时间
                response_time = time.time() - start_time
                
                # 提取token使用信息
                usage = response_data.get('usage', {})
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                total_tokens = usage.get('total_tokens', 0)
                
                # 记录成功响应日志
                logger.info(f"[{request_id}] API调用成功 - 响应时间: {response_time:.2f}s")
                logger.info(f"[{request_id}] Token使用情况 - 输入: {prompt_tokens}, 输出: {completion_tokens}, 总计: {total_tokens}")
                
                # 记录响应内容长度
                if 'choices' in response_data and response_data['choices']:
                    content_length = len(response_data['choices'][0].get('message', {}).get('content', ''))
                    logger.debug(f"[{request_id}] 响应内容长度: {content_length} 字符")
                
                return response_data
                
            except httpx.HTTPStatusError as e:
                response_time = time.time() - start_time
                logger.error(f"[{request_id}] 豆包API请求失败 - 状态码: {e.response.status_code}, 响应时间: {response_time:.2f}s")
                logger.error(f"[{request_id}] 错误详情: {e.response.text}")
                raise
            except httpx.RequestError as e:
                response_time = time.time() - start_time
                logger.error(f"[{request_id}] 豆包API网络请求错误 - 响应时间: {response_time:.2f}s, 错误: {str(e)}")
                raise
            except Exception as e:
                response_time = time.time() - start_time
                logger.error(f"[{request_id}] 豆包API未知错误 - 响应时间: {response_time:.2f}s, 错误: {str(e)}")
                raise
    
    async def generate_destination_analysis(self, destination: str, preferences: Dict[str, Any]) -> str:
        """生成目的地分析"""
        system_prompt = """你是一个专业的旅行顾问。请根据用户提供的目的地和偏好，生成详细的目的地分析报告。
        报告应包括：
        1. 目的地概况
        2. 最佳旅行时间
        3. 主要景点和活动
        4. 当地文化和特色
        5. 交通和住宿建议
        6. 预算参考
        
        请用中文回答，内容要详实且实用。"""
        
        user_prompt = f"""目的地：{destination}
        用户偏好：{json.dumps(preferences, ensure_ascii=False, indent=2)}
        
        请为这个目的地生成详细的分析报告。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._make_request(messages, temperature=0.7, max_tokens=2000)
            return response['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"生成目的地分析失败: {str(e)}")
            return f"目的地 {destination} 是一个值得探索的地方，具有丰富的文化和自然景观。"
    
    async def generate_daily_itinerary(self, destination: str, day: int, total_days: int, 
                                     preferences: Dict[str, Any], budget_level: str) -> Dict[str, Any]:
        """生成每日行程"""
        system_prompt = """你是一个专业的旅行规划师。请根据提供的信息生成详细的每日行程安排。
        
        请直接返回以下JSON格式的数据，不要添加任何其他文字说明：
        
        {
          "day": 1,
          "breakfast": {
            "name": "[具体餐厅名称]",
            "activity": "在[餐厅名称]用餐",
            "location": "[具体餐厅名称]",
            "address": "[详细地址]",
            "duration": "1小时",
            "cost": 50,
            "description": "[餐厅简介和推荐理由]",
            "specialties": "[推荐菜品和特色美食]",
            "features": "[餐厅特色亮点]",
            "tips": "[用餐贴心提示]",
            "openTime": "[营业时间]",
            "ticketPrice": "免费"
          },
          "morning": {
            "name": "[具体景点名称]",
            "activity": "游览[景点名称]",
            "location": "[具体景点名称]",
            "address": "[详细地址]",
            "duration": "3小时",
            "cost": 80,
            "description": "[景点简介和游览价值]",
            "features": "[景点特色亮点和必看景观]",
            "tips": "[游览贴心提示和注意事项]",
            "openTime": "[开放时间]",
            "ticketPrice": "[门票价格信息]"
          },
          "lunch": {
            "name": "[具体餐厅名称]",
            "activity": "在[餐厅名称]用餐",
            "location": "[具体餐厅名称]",
            "address": "[详细地址]",
            "duration": "1.5小时",
            "cost": 80,
            "description": "[餐厅简介和推荐理由]",
            "specialties": "[推荐菜品和特色美食]",
            "features": "[餐厅特色亮点]",
            "tips": "[用餐贴心提示]",
            "openTime": "[营业时间]",
            "ticketPrice": "免费"
          },
          "afternoon": {
            "name": "[具体景点名称]",
            "activity": "游览[景点名称]",
            "location": "[具体景点名称]",
            "address": "[详细地址]",
            "duration": "3.5小时",
            "cost": 100,
            "description": "[景点简介和游览价值]",
            "features": "[景点特色亮点和必看景观]",
            "tips": "[游览贴心提示和注意事项]",
            "openTime": "[开放时间]",
            "ticketPrice": "[门票价格信息]"
          },
          "dinner": {
            "name": "[具体餐厅名称]",
            "activity": "在[餐厅名称]用餐",
            "location": "[具体餐厅名称]",
            "address": "[详细地址]",
            "duration": "1.5小时",
            "cost": 120,
            "description": "[餐厅简介和推荐理由]",
            "specialties": "[推荐菜品和特色美食]",
            "features": "[餐厅特色亮点]",
            "tips": "[用餐贴心提示]",
            "openTime": "[营业时间]",
            "ticketPrice": "免费"
          },
          "evening": {
            "name": "[具体活动或地点名称]",
            "activity": "[具体活动名称]",
            "location": "[具体地点名称]",
            "address": "[详细地址]",
            "duration": "2小时",
            "cost": 60,
            "description": "[活动简介和体验价值]",
            "features": "[活动特色亮点和体验内容]",
            "tips": "[参与贴心提示和注意事项]",
            "openTime": "[开放时间]",
            "ticketPrice": "[门票或消费价格]"
          },
          "transportation": "[主要交通方式]",
          "estimated_cost": "[全天预估费用]"
        }
        
        重要要求：
        1. 所有cost字段必须是数字，不要包含货币符号
        2. 必须包含name、openTime、ticketPrice、specialties、features、tips等详细字段
        3. 确保所有推荐都是真实存在的，提供准确的地址和价格信息
        4. 只返回JSON数据，不要添加任何解释文字
        """
        
        user_prompt = f"""请为以下旅行安排生成第{day}天的详细行程：
        
        目的地：{destination}
        总行程天数：{total_days}天
        当前是第{day}天
        用户偏好：{json.dumps(preferences, ensure_ascii=False, indent=2)}
        预算水平：{budget_level}
        
        请生成具体的行程安排，包括真实的景点名称、地址和活动建议。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._make_request(messages, temperature=0.8, max_tokens=1500)
            content = response['choices'][0]['message']['content']
            
            # 解析生成的内容并结构化
            return self._parse_daily_itinerary(content, day)
        except Exception as e:
            logger.error(f"生成第{day}天行程失败: {str(e)}")
            return self._get_fallback_itinerary(destination, day)
    
    def _parse_cost_from_string(self, cost_str: str) -> float:
        """从字符串中解析费用数字"""
        import re
        
        if not cost_str or not isinstance(cost_str, str):
            return 0.0
        
        # 移除所有非数字和小数点的字符，提取数字
        numbers = re.findall(r'\d+(?:\.\d+)?', cost_str)
        
        if numbers:
            try:
                # 取第一个找到的数字
                return float(numbers[0])
            except (ValueError, IndexError):
                return 0.0
        
        return 0.0
    
    def _clean_markdown_format(self, text: str) -> str:
        """清理Markdown格式标记"""
        import re
        
        # 清理粗体标记 **text**
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # 清理斜体标记 *text*
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # 清理列表标记 - text 或 * text
        text = re.sub(r'^[\s]*[-\*]\s+', '', text, flags=re.MULTILINE)
        
        # 清理标题标记 # text
        text = re.sub(r'^[\s]*#+\s+', '', text, flags=re.MULTILINE)
        
        # 清理数字列表标记 1. text
        text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # 清理多余的空格和换行
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _parse_daily_itinerary(self, content: str, day: int) -> Dict[str, Any]:
        """解析生成的行程内容"""
        import json
        import re
        
        # 尝试直接解析JSON
        try:
            # 清理可能的markdown格式
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*$', '', content)
            content = content.strip()
            
            # 解析JSON
            itinerary = json.loads(content)
            
            # 确保包含所有必要字段
            default_structure = {
                'day': day,
                'breakfast': {
                    'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '1小时', 
                    'cost': 0, 'description': '', 'specialties': '', 'features': '', 
                    'tips': '', 'openTime': '', 'ticketPrice': '免费'
                },
                'morning': {
                    'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '3小时', 
                    'cost': 0, 'description': '', 'features': '', 'tips': '', 
                    'openTime': '', 'ticketPrice': ''
                },
                'lunch': {
                    'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '1.5小时', 
                    'cost': 0, 'description': '', 'specialties': '', 'features': '', 
                    'tips': '', 'openTime': '', 'ticketPrice': '免费'
                },
                'afternoon': {
                    'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '3.5小时', 
                    'cost': 0, 'description': '', 'features': '', 'tips': '', 
                    'openTime': '', 'ticketPrice': ''
                },
                'dinner': {
                    'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '1.5小时', 
                    'cost': 0, 'description': '', 'specialties': '', 'features': '', 
                    'tips': '', 'openTime': '', 'ticketPrice': '免费'
                },
                'evening': {
                    'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '2小时', 
                    'cost': 0, 'description': '', 'features': '', 'tips': '', 
                    'openTime': '', 'ticketPrice': ''
                },
                'transportation': '公共交通/步行',
                'estimated_cost': '200-500元'
            }
            
            # 合并默认结构和解析结果，并处理费用字段
            for period in ['breakfast', 'morning', 'lunch', 'afternoon', 'dinner', 'evening']:
                if period in itinerary:
                    for key in default_structure[period]:
                        if key not in itinerary[period]:
                            itinerary[period][key] = default_structure[period][key]
                    
                    # 处理cost字段，确保是数字类型
                    if 'cost' in itinerary[period]:
                        cost_value = itinerary[period]['cost']
                        if isinstance(cost_value, str):
                            itinerary[period]['cost'] = self._parse_cost_from_string(cost_value)
                        elif not isinstance(cost_value, (int, float)):
                            itinerary[period]['cost'] = 0.0
                else:
                    itinerary[period] = default_structure[period]
            
            # 设置基本信息
            itinerary['day'] = day
            if 'transportation' not in itinerary:
                itinerary['transportation'] = default_structure['transportation']
            if 'estimated_cost' not in itinerary:
                itinerary['estimated_cost'] = default_structure['estimated_cost']
                
            return itinerary
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"JSON解析失败，使用备用解析方法: {e}")
            # 如果JSON解析失败，使用备用解析方法
            return self._fallback_parse_itinerary(content, day)
    
    def _fallback_parse_itinerary(self, content: str, day: int) -> Dict[str, Any]:
        """备用解析方法"""
        import re
        
        itinerary = {
            'day': day,
            'breakfast': {
                'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '1小时', 
                'cost': 0, 'description': '', 'specialties': '', 'features': '', 
                'tips': '', 'openTime': '', 'ticketPrice': '免费'
            },
            'morning': {
                'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '3小时', 
                'cost': 0, 'description': '', 'features': '', 'tips': '', 
                'openTime': '', 'ticketPrice': ''
            },
            'lunch': {
                'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '1.5小时', 
                'cost': 0, 'description': '', 'specialties': '', 'features': '', 
                'tips': '', 'openTime': '', 'ticketPrice': '免费'
            },
            'afternoon': {
                'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '3.5小时', 
                'cost': 0, 'description': '', 'features': '', 'tips': '', 
                'openTime': '', 'ticketPrice': ''
            },
            'dinner': {
                'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '1.5小时', 
                'cost': 0, 'description': '', 'specialties': '', 'features': '', 
                'tips': '', 'openTime': '', 'ticketPrice': '免费'
            },
            'evening': {
                'name': '', 'activity': '', 'location': '', 'address': '', 'duration': '2小时', 
                'cost': 0, 'description': '', 'features': '', 'tips': '', 
                'openTime': '', 'ticketPrice': ''
            },
            'transportation': '公共交通/步行',
            'estimated_cost': '200-500元'
        }
        
        # 按时间段分割内容
        sections = {
            'morning': [],
            'afternoon': [],
            'evening': []
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 识别时间段
            if re.search(r'(上午|早上|morning)', line, re.IGNORECASE):
                current_section = 'morning'
                # 同时将这一行的内容也加入到对应时间段
                sections[current_section].append(line)
                continue
            elif re.search(r'(中午|午餐|lunch)', line, re.IGNORECASE):
                current_section = 'afternoon'  # 中午的内容归到下午
                sections[current_section].append(line)
                continue
            elif re.search(r'(下午|afternoon)', line, re.IGNORECASE):
                current_section = 'afternoon'
                sections[current_section].append(line)
                continue
            elif re.search(r'(晚上|傍晚|晚餐|evening)', line, re.IGNORECASE):
                current_section = 'evening'
                sections[current_section].append(line)
                continue
            
            if current_section and line:
                sections[current_section].append(line)
        
        # 解析每个时间段的内容
        for section_name, section_lines in sections.items():
            if not section_lines:
                continue
                
            # 对于每个时间段，只处理第一行（最相关的内容）
            line = section_lines[0] if section_lines else ''
            if not line:
                continue
                
            # 提取活动和位置信息
            activity_text = ''
            location_text = ''
            
            # 尝试提取具体的景点名称、餐厅名称等
            # 匹配常见的景点、餐厅、地址模式
            location_patterns = [
                r'([\u4e00-\u9fa5]+(?:博物馆|公园|寺|庙|塔|楼|山|湖|河|街|路|广场|中心|景区|风景区))',
                r'([\u4e00-\u9fa5]+(?:餐厅|酒店|饭店|茶楼|咖啡厅|小吃店|美食城))',
                r'([\u4e00-\u9fa5]+(?:大学|学院|图书馆|剧院|影院|商场|市场))',
                r'地址[：:](.*?)(?:[，,。]|$)',
                r'位置[：:](.*?)(?:[，,。]|$)',
                r'在(.*?)(?:[，,。]|$)'
            ]
            
            # 提取位置信息
            for pattern in location_patterns:
                matches = re.findall(pattern, line)
                if matches:
                    location_candidate = matches[0].strip()
                    if location_candidate and len(location_candidate) > 1:
                        location_text = location_candidate
                        break
            
            # 提取活动描述（移除时间段标识后的内容）
            # 清理时间段标识
            clean_line = re.sub(r'^(上午|下午|中午|晚上|早上|傍晚)[：:]?\s*', '', line)
            # 清理时间、价格等信息，保留主要活动描述
            clean_line = re.sub(r'\d+[：:]\d+', '', clean_line)  # 移除时间
            clean_line = re.sub(r'\d+元', '', clean_line)  # 移除价格
            clean_line = re.sub(r'[（(].*?[）)]', '', clean_line)  # 移除括号内容
            clean_line = clean_line.strip('，,。. ')
            if clean_line:
                activity_text = clean_line
            
            # 设置解析结果
            if activity_text:
                itinerary[section_name]['activity'] = activity_text
            if location_text:
                itinerary[section_name]['location'] = location_text
            
            # 如果没有找到具体位置，根据活动类型设置默认位置
            if not itinerary[section_name]['location'] and itinerary[section_name]['activity']:
                activity = itinerary[section_name]['activity']
                if '餐' in activity or '吃' in activity or '美食' in activity:
                    itinerary[section_name]['location'] = f"当地特色餐厅"
                elif '博物馆' in activity:
                    itinerary[section_name]['location'] = f"博物馆"
                elif '公园' in activity or '漫步' in activity:
                    itinerary[section_name]['location'] = f"城市公园"
                elif '购物' in activity or '商场' in activity:
                    itinerary[section_name]['location'] = f"购物中心"
                else:
                    itinerary[section_name]['location'] = f"市区景点"
        
        return itinerary
    
    def _extract_meal_info(self, text: str, meal_info: Dict[str, str]):
        """提取餐厅信息"""
        import re
        
        # 提取餐厅名称
        restaurant_patterns = [
            r'餐厅名称[：:]\s*([^\n]+)',
            r'([^，。！？\n]+(?:餐厅|酒楼|饭店|小吃|美食|茶楼|咖啡|酒吧|食堂))'
        ]
        
        for pattern in restaurant_patterns:
            match = re.search(pattern, text)
            if match:
                meal_info['location'] = match.group(1).strip()
                meal_info['activity'] = f"在{match.group(1).strip()}用餐"
                break
        
        # 提取地址
        address_match = re.search(r'地址[：:]\s*([^\n]+)', text)
        if address_match:
            meal_info['description'] = address_match.group(1).strip()
        
        # 提取推荐菜品
        dishes_match = re.search(r'推荐菜品[：:]\s*([^\n]+)', text)
        if dishes_match:
            meal_info['dishes'] = dishes_match.group(1).strip()
        
        # 提取人均消费
        cost_match = re.search(r'人均消费[：:]\s*([^\n]+)', text)
        if cost_match:
            meal_info['cost'] = cost_match.group(1).strip()
        
        # 提取特色介绍
        features_match = re.search(r'特色介绍[：:]\s*([^\n]+)', text)
        if features_match:
            meal_info['features'] = features_match.group(1).strip()
    
    def _extract_activity_info(self, text: str, activity_info: Dict[str, str]):
        """提取活动信息"""
        import re
        
        # 提取景点名称
        location_patterns = [
            r'景点名称[：:]\s*([^\n]+)',
            r'活动名称[：:]\s*([^\n]+)',
            r'([^，。！？\n]+(?:景区|公园|寺|庙|塔|楼|馆|院|山|湖|桥|街|路|广场|中心))'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                activity_info['location'] = match.group(1).strip()
                activity_info['activity'] = f"游览{match.group(1).strip()}"
                break
        
        # 提取地址
        address_match = re.search(r'地址[：:]\s*([^\n]+)', text)
        if address_match:
            activity_info['description'] = address_match.group(1).strip()
        
        # 提取开放时间
        hours_match = re.search(r'开放时间[：:]\s*([^\n]+)', text)
        if hours_match:
            activity_info['opening_hours'] = hours_match.group(1).strip()
        
        # 提取门票价格
        price_match = re.search(r'门票价格[：:]\s*([^\n]+)', text)
        if price_match:
            activity_info['cost'] = price_match.group(1).strip()
        
        # 提取游览重点或活动内容
        highlights_patterns = [
            r'游览重点[：:]\s*([^\n]+)',
            r'活动内容[：:]\s*([^\n]+)'
        ]
        
        for pattern in highlights_patterns:
            match = re.search(pattern, text)
            if match:
                if 'highlights' in activity_info:
                    activity_info['highlights'] = match.group(1).strip()
                else:
                    activity_info['content'] = match.group(1).strip()
                break
        
        # 提取交通方式
        transport_match = re.search(r'交通方式[：:]\s*([^\n]+)', text)
        if transport_match:
            activity_info['transportation'] = transport_match.group(1).strip()
        
        # 提取注意事项
        notes_match = re.search(r'注意事项[：:]\s*([^\n]+)', text)
        if notes_match:
            activity_info['notes'] = notes_match.group(1).strip()

    def _get_fallback_itinerary(self, destination: str, day: int) -> Dict[str, Any]:
        """获取备用行程"""
        return {
            'day': day,
            'morning': {
                'activity': f'{destination}市区观光',
                'location': f'{destination}市中心',
                'duration': '2-3小时'
            },
            'afternoon': {
                'activity': f'{destination}特色景点游览',
                'location': f'{destination}主要景区',
                'duration': '3-4小时'
            },
            'evening': {
                'activity': f'{destination}当地美食体验',
                'location': f'{destination}美食街',
                'duration': '2-3小时'
            },
            'transportation': '公共交通/步行',
            'estimated_cost': '200-500元'
        }
    
    async def generate_travel_tips(self, destination: str, preferences: Dict[str, Any]) -> List[str]:
        """生成旅行贴士"""
        system_prompt = """你是一个经验丰富的旅行顾问。请根据目的地和用户偏好，生成实用的旅行贴士。
        
        贴士应该包括：
        1. 当地文化注意事项
        2. 安全提醒
        3. 实用建议
        4. 省钱技巧
        5. 特色体验推荐
        
        每个贴士要简洁明了，用中文回答。"""
        
        user_prompt = f"""目的地：{destination}
        用户偏好：{json.dumps(preferences, ensure_ascii=False, indent=2)}
        
        请生成5-8个实用的旅行贴士。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._make_request(messages, temperature=0.6, max_tokens=800)
            content = response['choices'][0]['message']['content']
            
            # 解析贴士
            tips = []
            for line in content.split('\n'):
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or line.startswith('*') or line[0].isdigit()):
                    # 清理格式符号
                    tip = line.lstrip('•-*0123456789. ').strip()
                    if tip:
                        # 清理Markdown格式
                        tip = self._clean_markdown_format(tip)
                        tips.append(tip)
            
            return tips[:8] if tips else [f"在{destination}旅行时，建议提前了解当地文化和习俗。"]
        except Exception as e:
            logger.error(f"生成旅行贴士失败: {str(e)}")
            return [f"在{destination}旅行时，建议提前了解当地文化和习俗。"]

# 创建全局实例
llm_service = DoubaoLLMService()