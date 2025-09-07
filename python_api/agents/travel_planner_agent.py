"""LangGraph旅行规划智能体"""

import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .models import AgentState, TravelRequest, TravelPlan, ItineraryItem, ActivityItem
from .nodes import (
    InformationCollectorNode,
    DestinationAnalyzerNode,
    ItineraryPlannerNode,
    BudgetOptimizerNode,
    PersonalizationNode,
    CollaborationNode
)
from services.llm_service import llm_service
from services.weather_service import weather_service
from services.map_service import map_service

class TravelPlannerAgent:
    """旅行规划智能体主类"""
    
    def __init__(self):
        """初始化智能体"""
        self.memory = MemorySaver()
        self.graph = self._build_graph()
        
        # 初始化各个节点
        self.info_collector = InformationCollectorNode()
        self.destination_analyzer = DestinationAnalyzerNode()
        self.itinerary_planner = ItineraryPlannerNode()
        self.budget_optimizer = BudgetOptimizerNode()
        self.personalizer = PersonalizationNode()
        self.collaborator = CollaborationNode()
    
    def _build_graph(self) -> StateGraph:
        """构建LangGraph工作流"""
        # 创建状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("collect_info", self._collect_information)
        workflow.add_node("analyze_destination", self._analyze_destination)
        workflow.add_node("plan_itinerary", self._plan_itinerary)
        workflow.add_node("optimize_budget", self._optimize_budget)
        workflow.add_node("personalize", self._personalize_recommendations)
        workflow.add_node("handle_collaboration", self._handle_collaboration)
        workflow.add_node("finalize_plan", self._finalize_plan)
        
        # 设置入口点
        workflow.set_entry_point("collect_info")
        
        # 定义节点间的连接
        workflow.add_edge("collect_info", "analyze_destination")
        workflow.add_edge("analyze_destination", "plan_itinerary")
        workflow.add_edge("plan_itinerary", "optimize_budget")
        workflow.add_edge("optimize_budget", "personalize")
        workflow.add_edge("personalize", "handle_collaboration")
        workflow.add_edge("handle_collaboration", "finalize_plan")
        workflow.add_edge("finalize_plan", END)
        
        # 编译图
        return workflow.compile(checkpointer=self.memory)
    
    async def _collect_information(self, state: AgentState) -> AgentState:
        """信息收集节点"""
        try:
            state.current_step = "collecting_information"
            
            # 验证和处理用户输入
            request = state.request
            
            # 计算旅行天数
            days = (request.end_date - request.start_date).days + 1
            
            # 存储基础信息到metadata
            state.metadata.update({
                "travel_days": days,
                "destination_processed": request.destination.strip().title(),
                "budget_level": request.budget_level,
                "group_size": request.group_size,
                "travel_style": request.travel_style,
                "interests": request.interests
            })
            
            print(f"✅ 信息收集完成: {request.destination}, {days}天行程")
            
        except Exception as e:
            state.errors.append(f"信息收集失败: {str(e)}")
            print(f"❌ 信息收集错误: {e}")
        
        return state
    
    async def _analyze_destination(self, state: AgentState) -> AgentState:
        """目的地分析节点"""
        try:
            state.current_step = "analyzing_destination"
            
            destination = state.metadata.get("destination_processed")
            preferences = {
                "travel_style": state.metadata.get("travel_style"),
                "interests": state.metadata.get("interests"),
                "budget_level": state.metadata.get("budget_level"),
                "group_size": state.metadata.get("group_size")
            }
            
            # 使用豆包API生成目的地分析
            analysis_content = await llm_service.generate_destination_analysis(destination, preferences)
            
            # 解析分析内容并结构化存储
            destination_info = {
                "name": destination,
                "analysis": analysis_content,
                "country": "中国",  # 可以从分析中提取
                "timezone": "Asia/Shanghai",
                "currency": "CNY",
                "language": "中文"
            }
            
            # 生成旅行贴士
            tips = await llm_service.generate_travel_tips(destination, preferences)
            
            # 获取天气信息
            try:
                # 先获取目的地坐标
                location_info = await map_service.geocode(destination)
                if location_info:
                    longitude = location_info['longitude']
                    latitude = location_info['latitude']
                    
                    # 获取当前天气
                    current_weather = await weather_service.get_current_weather(destination)
                    
                    # 获取天气预报
                    forecast = await weather_service.get_forecast(destination, days=7)
                    
                    # 获取旅行天气分析
                    travel_weather = await weather_service.get_weather_for_travel(
                        destination,
                        state.request.start_date.isoformat(), 
                        state.request.end_date.isoformat()
                    )
                    
                    weather_data = {
                        "location": {
                            "longitude": longitude,
                            "latitude": latitude,
                            "address": location_info.get('address', destination)
                        },
                        "current": current_weather,
                        "forecast": forecast,
                        "travel_analysis": travel_weather
                    }
                    
                    print(f"✅ 天气信息获取成功: {destination}")
                else:
                    raise Exception("无法获取目的地坐标")
                    
            except Exception as e:
                print(f"⚠️ 天气信息获取失败，使用备用数据: {str(e)}")
                weather_data = {
                    "current_season": "春季",
                    "temperature_range": "15-25°C",
                    "weather_condition": "晴朗",
                    "rainfall_probability": "20%",
                    "clothing_suggestion": "轻薄外套，舒适鞋子",
                    "note": "天气数据获取失败，显示为示例数据"
                }
            
            cultural_info = {
                "tips": tips
            }
            
            state.destination_info = destination_info
            state.weather_data = weather_data
            state.cultural_info = cultural_info
            
            print(f"✅ 目的地分析完成: {destination}")
            
        except Exception as e:
            state.errors.append(f"目的地分析失败: {str(e)}")
            print(f"❌ 目的地分析错误: {e}")
            # 使用备用方案
            destination = state.metadata.get("destination_processed")
            state.destination_info = {"name": destination, "analysis": f"{destination}是一个值得探索的目的地"}
            state.weather_data = {"current_season": "春季"}
            state.cultural_info = {"tips": ["注意当地文化习俗"]}
        
        return state
    
    async def _plan_itinerary(self, state: AgentState) -> AgentState:
        """行程规划节点"""
        try:
            state.current_step = "planning_itinerary"
            
            travel_days = state.metadata.get("travel_days", 1)
            destination = state.metadata.get("destination_processed")
            travel_style = state.metadata.get("travel_style", "")
            interests = state.metadata.get("interests", [])
            budget_level = state.metadata.get("budget_level", "舒适型")
            
            preferences = {
                "travel_style": travel_style,
                "interests": interests,
                "budget_level": budget_level,
                "group_size": state.metadata.get("group_size")
            }
            
            itinerary = []
            
            for day in range(1, travel_days + 1):
                # 获取当日天气信息
                day_date = state.request.start_date + timedelta(days=day-1)
                weather_note = self._get_weather_note_for_day(state.weather_data, day_date)
                
                # 根据天气调整偏好设置
                weather_adjusted_preferences = preferences.copy()
                weather_adjusted_preferences['weather_info'] = weather_note
                
                # 使用豆包API生成每日行程
                daily_plan = await llm_service.generate_daily_itinerary(
                    destination, day, travel_days, weather_adjusted_preferences, budget_level
                )
                
                # 将AI生成的行程转换为ActivityItem格式
                activities = await self._convert_ai_plan_to_activities(daily_plan, destination)
                
                # 根据天气调整活动建议
                activities = self._adjust_activities_for_weather(activities, weather_note)
                
                # 计算当日费用
                total_cost = sum(activity.cost or 0 for activity in activities)
                
                # 生成包含天气信息的备注
                day_notes = f"第{day}天行程安排，注意合理安排时间"
                if weather_note:
                    day_notes += f"\n天气提醒: {weather_note}"
                
                itinerary_item = ItineraryItem(
                    day=day,
                    date=day_date.strftime("%Y-%m-%d"),
                    theme=f"第{day}天 - {self._get_day_theme(day, travel_style)}",
                    activities=activities,
                    total_cost=total_cost,
                    notes=day_notes
                )
                
                itinerary.append(itinerary_item)
            
            state.itinerary_draft = itinerary
            
            print(f"✅ 行程规划完成: {travel_days}天行程")
            
        except Exception as e:
            state.errors.append(f"行程规划失败: {str(e)}")
            print(f"❌ 行程规划错误: {e}")
            # 使用备用方案
            travel_days = state.metadata.get("travel_days", 1)
            destination = state.metadata.get("destination_processed")
            travel_style = state.metadata.get("travel_style", "")
            interests = state.metadata.get("interests", [])
            
            itinerary = []
            for day in range(1, travel_days + 1):
                activities = self._generate_daily_activities(day, travel_style, interests, destination)
                total_cost = sum(activity.cost or 0 for activity in activities)
                
                itinerary_item = ItineraryItem(
                    day=day,
                    date=(state.request.start_date + timedelta(days=day-1)).strftime("%Y-%m-%d"),
                    theme=f"第{day}天 - {self._get_day_theme(day, travel_style)}",
                    activities=activities,
                    total_cost=total_cost,
                    notes=f"第{day}天行程安排，注意合理安排时间"
                )
                itinerary.append(itinerary_item)
            
            state.itinerary_draft = itinerary
        
        return state
    
    def _generate_daily_activities(self, day: int, travel_style: str, interests: List[str], destination: str) -> List[ActivityItem]:
        """生成每日活动安排"""
        activities = []
        
        if day == 1:
            # 第一天：抵达和适应
            activities = [
                ActivityItem(
                    time="09:00",
                    activity="抵达目的地",
                    location=f"{destination}机场/车站",
                    cost=0,
                    duration="1小时",
                    description="抵达并前往住宿地点"
                ),
                ActivityItem(
                    time="11:00",
                    activity="酒店入住",
                    location="市中心酒店",
                    cost=500,
                    duration="30分钟",
                    description="办理入住手续，稍作休息"
                ),
                ActivityItem(
                    time="14:00",
                    activity="午餐体验",
                    location="当地特色餐厅",
                    cost=150,
                    duration="1.5小时",
                    description="品尝当地特色美食"
                ),
                ActivityItem(
                    time="16:00",
                    activity="城市初探",
                    location="市中心商业区",
                    cost=100,
                    duration="3小时",
                    description="熟悉周边环境，轻松游览"
                )
            ]
        else:
            # 其他天数：根据兴趣和风格安排
            base_activities = [
                ActivityItem(
                    time="08:00",
                    activity="早餐",
                    location="酒店或附近餐厅",
                    cost=80,
                    duration="1小时",
                    description="享用丰盛早餐"
                ),
                ActivityItem(
                    time="09:30",
                    activity=self._get_morning_activity(travel_style, interests, destination),
                    location=f"{destination}热门景点",
                    cost=200,
                    duration="3小时",
                    description="上午主要活动"
                ),
                ActivityItem(
                    time="12:30",
                    activity="午餐",
                    location="景区餐厅",
                    cost=120,
                    duration="1小时",
                    description="中式或当地特色午餐"
                ),
                ActivityItem(
                    time="15:00",
                    activity=self._get_afternoon_activity(travel_style, interests, destination),
                    location=f"{destination}文化区",
                    cost=150,
                    duration="3小时",
                    description="下午休闲活动"
                ),
                ActivityItem(
                    time="19:00",
                    activity="晚餐",
                    location="特色餐厅",
                    cost=200,
                    duration="1.5小时",
                    description="品尝当地晚餐"
                )
            ]
            activities = base_activities
        
        return activities
    
    async def _get_location_info(self, location_name: str, destination: str) -> Dict[str, Any]:
        """获取地理位置信息"""
        import re
        
        try:
            # 验证和清理搜索关键词
            original_location = location_name
            
            if not location_name or location_name.strip() == '' or location_name == '待定':
                # 如果location_name无效，使用默认关键词
                search_keyword = f"{destination}景点"
                print(f"位置名称无效，使用默认关键词: {search_keyword}")
            else:
                # 清理和优化搜索关键词
                search_keyword = location_name.strip()
                
                # 检查是否为通用词汇，如果是则尝试优化
                generic_terms = ['景点', '餐厅', '饭店', '酒店', '商场', '公园', '博物馆', '寺庙', '市场']
                
                # 如果是纯通用词汇，添加目的地前缀
                if search_keyword in generic_terms:
                    search_keyword = f"{destination}{search_keyword}"
                    print(f"通用词汇优化: {original_location} -> {search_keyword}")
                
                # 如果包含通用词汇但不是纯通用词汇，尝试提取具体名称
                elif any(term in search_keyword for term in generic_terms):
                    # 尝试提取具体的地点名称
                    specific_patterns = [
                        r'([\u4e00-\u9fa5]+)(?:景点|餐厅|饭店|酒店|商场|公园|博物馆|寺庙|市场)',
                        r'([\u4e00-\u9fa5]{2,})(?:的|附近)',
                        r'在([\u4e00-\u9fa5]{2,})(?:游览|参观|用餐|购物)'
                    ]
                    
                    for pattern in specific_patterns:
                        matches = re.findall(pattern, search_keyword)
                        if matches:
                            specific_name = matches[0].strip()
                            if len(specific_name) >= 2:  # 确保提取的名称有意义
                                search_keyword = specific_name
                                print(f"提取具体名称: {original_location} -> {search_keyword}")
                                break
                
                # 如果搜索关键词太短或太通用，添加目的地信息
                if len(search_keyword) < 2 or search_keyword in ['当地', '附近', '周边']:
                    search_keyword = f"{destination}著名景点"
                    print(f"关键词太短，使用默认: {original_location} -> {search_keyword}")
            
            # 使用地图服务搜索POI
            poi_results = await map_service.search_poi(search_keyword, destination)
            
            if poi_results and len(poi_results) > 0:
                poi = poi_results[0]
                return {
                    'formatted_address': poi.get('formatted_address', search_keyword),
                    'poi_info': f"地址: {poi.get('formatted_address', '')}\n评分: {poi.get('rating', 'N/A')}\n类型: {poi.get('type', '')}",
                    'coordinates': poi.get('coordinates', poi.get('location', {}))
                }
            else:
                # 如果搜索失败，尝试使用更通用的关键词重新搜索
                fallback_keyword = f"{destination}热门景点"
                print(f"原搜索失败，尝试备用关键词: {fallback_keyword}")
                
                fallback_results = await map_service.search_poi(fallback_keyword, destination)
                if fallback_results and len(fallback_results) > 0:
                    poi = fallback_results[0]
                    return {
                        'formatted_address': poi.get('formatted_address', search_keyword),
                        'poi_info': f"地址: {poi.get('formatted_address', '')}\n评分: {poi.get('rating', 'N/A')}\n类型: {poi.get('type', '')}",
                        'coordinates': poi.get('coordinates', poi.get('location', {}))
                    }
                
                # 最终备用方案：返回目的地相关的合理默认值
                return self._get_destination_fallback_location(destination, search_keyword)
                
        except Exception as e:
            print(f"获取位置信息失败: {e}")
            # 异常情况下也返回合理的默认值
            return self._get_destination_fallback_location(destination, original_location or '未知位置')
    
    def _get_destination_fallback_location(self, destination: str, location_name: str) -> Dict[str, Any]:
        """获取目的地相关的备用位置信息"""
        # 根据目的地提供更合理的默认坐标和信息
        destination_defaults = {
            '北京': {'lat': 39.9042, 'lng': 116.4074, 'area': '北京市中心'},
            '上海': {'lat': 31.2304, 'lng': 121.4737, 'area': '上海市中心'},
            '广州': {'lat': 23.1291, 'lng': 113.2644, 'area': '广州市中心'},
            '深圳': {'lat': 22.5431, 'lng': 114.0579, 'area': '深圳市中心'},
            '杭州': {'lat': 30.2741, 'lng': 120.1551, 'area': '杭州市中心'},
            '成都': {'lat': 30.5728, 'lng': 104.0668, 'area': '成都市中心'},
            '西安': {'lat': 34.3416, 'lng': 108.9398, 'area': '西安市中心'},
            '南京': {'lat': 32.0603, 'lng': 118.7969, 'area': '南京市中心'},
            '重庆': {'lat': 29.5647, 'lng': 106.5507, 'area': '重庆市中心'},
            '天津': {'lat': 39.3434, 'lng': 117.3616, 'area': '天津市中心'}
        }
        
        # 查找匹配的目的地
        for city, coords in destination_defaults.items():
            if city in destination:
                return {
                    'formatted_address': f"{coords['area']}附近",
                    'poi_info': f"位置: {coords['area']}\n类型: 城市中心区域\n说明: 备用位置信息",
                    'coordinates': {'lat': coords['lat'], 'lng': coords['lng']}
                }
        
        # 如果没有匹配的城市，返回通用默认值
        return {
            'formatted_address': f"{destination}市中心",
            'poi_info': f"位置: {destination}市中心\n类型: 城市中心区域\n说明: 备用位置信息",
            'coordinates': {'lat': 39.9042, 'lng': 116.4074}  # 默认北京坐标
        }
    
    def _get_weather_note_for_day(self, weather_data: dict, target_date) -> str:
        """获取指定日期的天气提醒"""
        try:
            if not weather_data or 'forecast' not in weather_data:
                return ""
            
            # 查找目标日期的天气预报
            target_date_str = target_date.strftime("%Y-%m-%d")
            for forecast in weather_data['forecast']:
                if forecast.get('date') == target_date_str:
                    weather = forecast.get('weather', '')
                    temp_max = forecast.get('temp_max')
                    temp_min = forecast.get('temp_min')
                    
                    note = f"{weather}"
                    if temp_max and temp_min:
                        note += f"，{temp_min}°C - {temp_max}°C"
                    
                    # 添加天气建议
                    if '雨' in weather or '雪' in weather:
                        note += "，建议携带雨具"
                    elif '晴' in weather:
                        note += "，适合户外活动"
                    elif '阴' in weather or '云' in weather:
                        note += "，适合室内外活动"
                    
                    return note
        except Exception as e:
            print(f"获取天气提醒失败: {e}")
        
        return ""
    
    def _adjust_activities_for_weather(self, activities: List[ActivityItem], weather_note: str) -> List[ActivityItem]:
        """根据天气调整活动建议"""
        if not weather_note:
            return activities
        
        try:
            # 如果是雨雪天气，在描述中添加提醒
            if '雨' in weather_note or '雪' in weather_note:
                for activity in activities:
                    if '户外' in activity.description:
                        activity.description += "\n⚠️ 雨雪天气，建议准备雨具或考虑室内替代活动"
            
            # 如果是极端温度，添加提醒
            if '高温' in weather_note or '低温' in weather_note:
                for activity in activities:
                    activity.description += "\n🌡️ 注意防暑降温/保暖措施"
        
        except Exception as e:
            print(f"调整活动建议失败: {e}")
        
        return activities
    
    def _parse_cost_from_string(self, cost_str: Any) -> float:
        """从字符串中解析费用数字"""
        import re
        
        if cost_str is None:
            return 0.0
        
        if isinstance(cost_str, (int, float)):
            return float(cost_str)
        
        if not isinstance(cost_str, str):
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
    
    async def _convert_ai_plan_to_activities(self, daily_plan: Dict[str, Any], destination: str) -> List[ActivityItem]:
        """将AI生成的行程转换为ActivityItem格式，并添加地理位置信息"""
        activities = []
        
        # 早餐
        if daily_plan.get('breakfast'):
            breakfast = daily_plan['breakfast']
            location_name = breakfast.get('restaurant', breakfast.get('location', '酒店餐厅'))
            
            location_info = await self._get_location_info(location_name, destination)
            
            activities.append(ActivityItem(
                time="08:00",
                activity=f"早餐 - {breakfast.get('restaurant', '酒店餐厅')}",
                location=location_info.get('formatted_address', location_name),
                cost=self._parse_cost_from_string(breakfast.get('cost', 50)),
                duration=breakfast.get('duration', '1小时'),
                description=f"{breakfast.get('description', '享用早餐')}\n推荐菜品: {breakfast.get('recommended_dishes', '当地特色')}\n{location_info.get('poi_info', '')}"
            ))
        
        # 上午活动
        if daily_plan.get('morning'):
            morning = daily_plan['morning']
            location_name = morning.get('location', '待定')
            
            location_info = await self._get_location_info(location_name, destination)
            
            activities.append(ActivityItem(
                time="09:30",
                activity=morning.get('activity', '上午活动'),
                location=location_info.get('formatted_address', location_name),
                cost=self._parse_cost_from_string(morning.get('cost', 100)),
                duration=morning.get('duration', '2-3小时'),
                description=f"{morning.get('description', '上午活动安排')}\n开放时间: {morning.get('opening_hours', '全天')}\n门票: {morning.get('ticket_price', '待查询')}\n{location_info.get('poi_info', '')}"
            ))
        
        # 午餐
        if daily_plan.get('lunch'):
            lunch = daily_plan['lunch']
            location_name = lunch.get('restaurant', lunch.get('location', '当地餐厅'))
            
            location_info = await self._get_location_info(location_name, destination)
            
            activities.append(ActivityItem(
                time="12:00",
                activity=f"午餐 - {lunch.get('restaurant', '当地餐厅')}",
                location=location_info.get('formatted_address', location_name),
                cost=self._parse_cost_from_string(lunch.get('cost', 80)),
                duration=lunch.get('duration', '1小时'),
                description=f"{lunch.get('description', '享用午餐')}\n推荐菜品: {lunch.get('recommended_dishes', '当地特色')}\n人均消费: {lunch.get('average_cost', '80元')}\n{location_info.get('poi_info', '')}"
            ))
        
        # 下午活动
        if daily_plan.get('afternoon'):
            afternoon = daily_plan['afternoon']
            location_name = afternoon.get('location', '待定')
            
            location_info = await self._get_location_info(location_name, destination)
            
            activities.append(ActivityItem(
                time="14:00",
                activity=afternoon.get('activity', '下午活动'),
                location=location_info.get('formatted_address', location_name),
                cost=self._parse_cost_from_string(afternoon.get('cost', 150)),
                duration=afternoon.get('duration', '3-4小时'),
                description=f"{afternoon.get('description', '下午活动安排')}\n开放时间: {afternoon.get('opening_hours', '全天')}\n门票: {afternoon.get('ticket_price', '待查询')}\n特色: {afternoon.get('features', '精彩体验')}\n{location_info.get('poi_info', '')}"
            ))
        
        # 晚餐
        if daily_plan.get('dinner'):
            dinner = daily_plan['dinner']
            location_name = dinner.get('restaurant', dinner.get('location', '当地餐厅'))
            
            location_info = await self._get_location_info(location_name, destination)
            
            activities.append(ActivityItem(
                time="18:00",
                activity=f"晚餐 - {dinner.get('restaurant', '当地餐厅')}",
                location=location_info.get('formatted_address', location_name),
                cost=self._parse_cost_from_string(dinner.get('cost', 120)),
                duration=dinner.get('duration', '1.5小时'),
                description=f"{dinner.get('description', '享用晚餐')}\n推荐菜品: {dinner.get('recommended_dishes', '当地特色')}\n人均消费: {dinner.get('average_cost', '120元')}\n{location_info.get('poi_info', '')}"
            ))
        
        # 晚上活动
        if daily_plan.get('evening'):
            evening = daily_plan['evening']
            location_name = evening.get('location', '酒店附近')
            
            location_info = await self._get_location_info(location_name, destination)
            
            activities.append(ActivityItem(
                time="20:00",
                activity=evening.get('activity', '晚上活动'),
                location=location_info.get('formatted_address', location_name),
                cost=self._parse_cost_from_string(evening.get('cost', 80)),
                duration=evening.get('duration', '2小时'),
                description=f"{evening.get('description', '晚上活动安排')}\n开放时间: {evening.get('opening_hours', '夜间')}\n费用: {evening.get('cost', 80)}元\n{location_info.get('poi_info', '')}"
            ))
        
        return activities
    
    def _get_day_theme(self, day: int, travel_style: str) -> str:
        """获取当日主题"""
        if day == 1:
            return "抵达适应"
        elif "文化探索" == travel_style:
            return "文化体验"
        elif "美食之旅" == travel_style:
            return "美食探索"
        elif "休闲度假" == travel_style:
            return "休闲放松"
        else:
            return "精彩游览"
    
    def _get_morning_activity(self, travel_style: str, interests: List[str], destination: str) -> str:
        """获取上午活动"""
        if "文化探索" == travel_style:
            return f"{destination}博物馆参观"
        elif "美食之旅" == travel_style:
            return f"{destination}传统市场探索"
        elif "冒险刺激" == travel_style:
            return f"{destination}户外探险"
        else:
            return f"{destination}著名景点游览"
    
    def _get_afternoon_activity(self, travel_style: str, interests: List[str], destination: str) -> str:
        """获取下午活动"""
        if "购物血拼" == travel_style:
            return f"{destination}购物中心"
        elif "摄影打卡" == travel_style:
            return f"{destination}网红打卡地"
        elif "休闲度假" == travel_style:
            return f"{destination}公园漫步"
        else:
            return f"{destination}文化街区"
    
    async def _optimize_budget(self, state: AgentState) -> AgentState:
        """预算优化节点"""
        try:
            state.current_step = "optimizing_budget"
            
            budget_level = state.metadata.get("budget_level")
            itinerary = state.itinerary_draft or []
            
            # 计算总预算
            total_cost = sum(
                sum(activity.cost or 0 for activity in day.activities)
                for day in itinerary
            )
            
            # 根据预算等级调整
            budget_multiplier = {
                "经济型": 0.8,
                "舒适型": 1.0,
                "豪华型": 1.5,
                "不限预算": 2.0
            }.get(budget_level, 1.0)
            
            optimized_cost = total_cost * budget_multiplier
            
            # 预算分析
            budget_analysis = {
                "original_cost": total_cost,
                "optimized_cost": optimized_cost,
                "budget_level": budget_level,
                "cost_breakdown": {
                    "accommodation": optimized_cost * 0.4,
                    "food": optimized_cost * 0.3,
                    "activities": optimized_cost * 0.2,
                    "transportation": optimized_cost * 0.1
                },
                "saving_tips": [
                    "提前预订可享受折扣",
                    "选择当地交通工具",
                    "尝试当地平价美食"
                ]
            }
            
            state.budget_analysis = budget_analysis
            
            print(f"✅ 预算优化完成: 预估费用 {optimized_cost:.0f} 元")
            
        except Exception as e:
            state.errors.append(f"预算优化失败: {str(e)}")
            print(f"❌ 预算优化错误: {e}")
        
        return state
    
    async def _personalize_recommendations(self, state: AgentState) -> AgentState:
        """个性化推荐节点"""
        try:
            state.current_step = "personalizing"
            
            travel_styles = state.metadata.get("travel_styles", [])
            interests = state.metadata.get("interests", [])
            destination_info = state.destination_info or {}
            
            recommendations = []
            
            # 基于旅行风格的推荐
            if "美食之旅" in travel_styles:
                recommendations.extend([
                    "推荐尝试当地特色小吃街",
                    "预约知名餐厅需提前订位",
                    "可以参加当地烹饪课程"
                ])
            
            if "文化探索" in travel_styles:
                recommendations.extend([
                    "建议购买博物馆通票",
                    "可以预约当地文化导览",
                    "关注当地节庆活动"
                ])
            
            if "摄影打卡" in travel_styles:
                recommendations.extend([
                    "推荐最佳拍照时间：日出日落",
                    "准备充电宝和备用存储卡",
                    "了解当地拍照礼仪"
                ])
            
            # 基于兴趣的推荐
            for interest in interests:
                if "历史" in interest:
                    recommendations.append("推荐参观历史遗迹和古建筑")
                elif "自然" in interest:
                    recommendations.append("安排户外自然景观游览")
                elif "艺术" in interest:
                    recommendations.append("参观当地艺术馆和画廊")
            
            # 通用推荐
            recommendations.extend([
                "建议下载当地地图和翻译APP",
                "准备常用药品和防晒用品",
                "了解当地紧急联系方式",
                "保持手机电量充足"
            ])
            
            state.recommendations = recommendations
            
            print(f"✅ 个性化推荐完成: {len(recommendations)}条建议")
            
        except Exception as e:
            state.errors.append(f"个性化推荐失败: {str(e)}")
            print(f"❌ 个性化推荐错误: {e}")
        
        return state
    
    async def _handle_collaboration(self, state: AgentState) -> AgentState:
        """协作处理节点"""
        try:
            state.current_step = "handling_collaboration"
            
            participants = state.metadata.get("group_size", 1)
            
            if participants > 1:
                # 多人旅行的协调建议
                collaboration_tips = [
                    "建议创建群聊方便沟通",
                    "提前确认每个人的兴趣偏好",
                    "安排集合时间和地点",
                    "准备应急联系方式",
                    "考虑不同的预算需求",
                    "安排轮流决策避免分歧"
                ]
                
                state.recommendations.extend(collaboration_tips)
                
                print(f"✅ 协作处理完成: {participants}人旅行协调")
            else:
                print(f"✅ 协作处理完成: 单人旅行")
            
        except Exception as e:
            state.errors.append(f"协作处理失败: {str(e)}")
            print(f"❌ 协作处理错误: {e}")
        
        return state
    
    async def _finalize_plan(self, state: AgentState) -> AgentState:
        """最终化计划节点"""
        try:
            state.current_step = "finalizing"
            
            # 确保所有必需字段都有有效值
            destination = state.metadata.get("destination_processed") or state.request.destination
            user_id = state.request.user_id or "anonymous"
            
            # 生成最终的旅行计划
            plan = TravelPlan(
                plan_id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}",
                title=f"{destination}之旅",
                destination=destination,
                start_date=state.request.start_date,
                end_date=state.request.end_date,
                group_size=state.request.group_size,
                budget_estimate=state.budget_analysis.get("optimized_cost") if state.budget_analysis else None,
                itinerary=state.itinerary_draft or [],
                recommendations=state.recommendations or [],
                weather_info=state.weather_data,
                cultural_tips=state.cultural_info.get("tips", []) if state.cultural_info else []
            )
            
            # 将计划存储到状态中
            state.metadata["final_plan"] = plan
            
            print(f"✅ 计划最终化完成: {plan.title}")
            
        except Exception as e:
            state.errors.append(f"计划最终化失败: {str(e)}")
            print(f"❌ 计划最终化错误: {e}")
        
        return state
    
    async def generate_travel_plan(self, request: TravelRequest) -> Dict[str, Any]:
        """生成旅行计划的主入口方法"""
        start_time = datetime.now()
        
        try:
            # 创建初始状态
            initial_state = AgentState(
                request=request,
                current_step="start"
            )
            
            # 执行工作流
            config = {"configurable": {"thread_id": f"travel_plan_{request.user_id}"}}
            
            print(f"🚀 开始生成旅行计划: {request.destination}")
            
            # 运行图
            final_state = await self.graph.ainvoke(initial_state, config)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 检查是否有错误
            errors = getattr(final_state, 'errors', [])
            if errors:
                return {
                    "success": False,
                    "message": f"生成过程中出现错误: {'; '.join(errors)}",
                    "processing_time": processing_time,
                    "errors": errors
                }
            
            # 获取最终计划 - final_state是AddableValuesDict，直接访问字段
            metadata = final_state.get('metadata', {})
            final_plan = metadata.get("final_plan")
            
            if not final_plan:
                return {
                    "success": False,
                    "message": "未能生成有效的旅行计划",
                    "processing_time": processing_time
                }
            
            print(f"✅ 旅行计划生成完成，耗时 {processing_time:.2f} 秒")
            
            return {
                "success": True,
                "plan": final_plan,
                "message": "旅行计划生成成功",
                "processing_time": processing_time,
                "agent_steps": [
                    "信息收集", "目的地分析", "行程规划", 
                    "预算优化", "个性化推荐", "协作处理", "计划最终化"
                ]
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"生成旅行计划时发生错误: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                "success": False,
                "message": error_msg,
                "processing_time": processing_time,
                "error": str(e)
            }