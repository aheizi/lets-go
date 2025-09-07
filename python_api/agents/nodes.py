"""LangGraph智能体节点实现"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from .models import AgentState, TravelRequest, ActivityItem, ItineraryItem

class BaseNode:
    """节点基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    async def process(self, state: AgentState) -> AgentState:
        """处理节点逻辑"""
        raise NotImplementedError
    
    def log(self, message: str, level: str = "info"):
        """日志记录"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }.get(level, "ℹ️")
        print(f"[{timestamp}] {prefix} {self.name}: {message}")

class InformationCollectorNode(BaseNode):
    """信息收集节点"""
    
    def __init__(self):
        super().__init__("信息收集器")
    
    async def process(self, state: AgentState) -> AgentState:
        """收集和验证用户输入的旅行信息"""
        try:
            self.log("开始收集旅行信息")
            
            request = state.request
            
            # 验证必要字段
            if not request.destination:
                raise ValueError("目的地不能为空")
            
            if not request.start_date or not request.end_date:
                raise ValueError("出发和返回日期不能为空")
            
            if request.start_date >= request.end_date:
                raise ValueError("返回日期必须晚于出发日期")
            
            if request.participants <= 0:
                raise ValueError("参与人数必须大于0")
            
            # 计算旅行天数
            travel_days = (request.end_date - request.start_date).days + 1
            
            # 处理目的地信息
            destination_clean = request.destination.strip().title()
            
            # 分析旅行风格
            travel_styles = [style.value for style in request.travel_styles]
            
            # 更新状态元数据
            state.metadata.update({
                "travel_days": travel_days,
                "destination_processed": destination_clean,
                "budget_level": request.budget.value,
                "participant_count": request.participants,
                "travel_styles": travel_styles,
                "interests": request.interests,
                "collection_timestamp": datetime.now().isoformat(),
                "validation_passed": True
            })
            
            self.log(f"信息收集完成: {destination_clean}, {travel_days}天, {request.participants}人", "success")
            
        except Exception as e:
            error_msg = f"信息收集失败: {str(e)}"
            state.errors.append(error_msg)
            self.log(error_msg, "error")
            state.metadata["validation_passed"] = False
        
        return state

class DestinationAnalyzerNode(BaseNode):
    """目的地分析节点"""
    
    def __init__(self):
        super().__init__("目的地分析器")
        # 模拟的目的地数据库
        self.destination_db = self._init_destination_db()
    
    def _init_destination_db(self) -> Dict[str, Dict[str, Any]]:
        """初始化目的地数据库（模拟数据）"""
        return {
            "北京": {
                "country": "中国",
                "timezone": "Asia/Shanghai",
                "currency": "CNY",
                "language": "中文",
                "best_season": "春秋季",
                "famous_attractions": ["故宫", "长城", "天坛", "颐和园", "鸟巢"],
                "local_cuisine": ["北京烤鸭", "炸酱面", "豆汁", "驴打滚"],
                "transportation": {
                    "airport": "首都国际机场",
                    "public_transport": "地铁、公交、出租车",
                    "recommended": "地铁出行"
                },
                "climate": "温带季风气候",
                "population": "2100万"
            },
            "上海": {
                "country": "中国",
                "timezone": "Asia/Shanghai",
                "currency": "CNY",
                "language": "中文",
                "best_season": "春秋季",
                "famous_attractions": ["外滩", "东方明珠", "豫园", "南京路", "迪士尼"],
                "local_cuisine": ["小笼包", "生煎包", "白切鸡", "糖醋排骨"],
                "transportation": {
                    "airport": "浦东国际机场",
                    "public_transport": "地铁、公交、出租车",
                    "recommended": "地铁出行"
                },
                "climate": "亚热带季风气候",
                "population": "2400万"
            },
            "杭州": {
                "country": "中国",
                "timezone": "Asia/Shanghai",
                "currency": "CNY",
                "language": "中文",
                "best_season": "春秋季",
                "famous_attractions": ["西湖", "灵隐寺", "千岛湖", "宋城", "雷峰塔"],
                "local_cuisine": ["西湖醋鱼", "东坡肉", "龙井虾仁", "叫化鸡"],
                "transportation": {
                    "airport": "萧山国际机场",
                    "public_transport": "地铁、公交、出租车",
                    "recommended": "地铁+公交"
                },
                "climate": "亚热带季风气候",
                "population": "1200万"
            }
        }
    
    async def process(self, state: AgentState) -> AgentState:
        """分析目的地信息"""
        try:
            self.log("开始分析目的地")
            
            destination = state.metadata.get("destination_processed")
            
            # 从数据库获取目的地信息
            destination_info = self.destination_db.get(destination)
            
            if not destination_info:
                # 如果数据库中没有，生成通用信息
                destination_info = self._generate_generic_info(destination)
                self.log(f"使用通用模板生成 {destination} 信息", "warning")
            
            # 生成天气信息
            weather_data = self._generate_weather_info(destination)
            
            # 生成文化信息
            cultural_info = self._generate_cultural_info(destination)
            
            # 更新状态
            state.destination_info = destination_info
            state.weather_data = weather_data
            state.cultural_info = cultural_info
            
            self.log(f"目的地分析完成: {destination}", "success")
            
        except Exception as e:
            error_msg = f"目的地分析失败: {str(e)}"
            state.errors.append(error_msg)
            self.log(error_msg, "error")
        
        return state
    
    def _generate_generic_info(self, destination: str) -> Dict[str, Any]:
        """生成通用目的地信息"""
        return {
            "name": destination,
            "country": "中国",
            "timezone": "Asia/Shanghai",
            "currency": "CNY",
            "language": "中文",
            "best_season": "春秋季",
            "famous_attractions": [
                f"{destination}著名景点1",
                f"{destination}著名景点2",
                f"{destination}著名景点3"
            ],
            "local_cuisine": [
                f"{destination}特色美食1",
                f"{destination}特色美食2"
            ],
            "transportation": {
                "airport": f"{destination}机场",
                "public_transport": "地铁、公交、出租车",
                "recommended": "公共交通"
            }
        }
    
    def _generate_weather_info(self, destination: str) -> Dict[str, Any]:
        """生成天气信息"""
        # 模拟天气数据
        current_month = datetime.now().month
        
        if current_month in [3, 4, 5]:  # 春季
            season = "春季"
            temp_range = "15-25°C"
            condition = "温和宜人"
            rainfall = "适中"
            clothing = "轻薄外套，舒适鞋子"
        elif current_month in [6, 7, 8]:  # 夏季
            season = "夏季"
            temp_range = "25-35°C"
            condition = "炎热"
            rainfall = "较多"
            clothing = "轻薄透气衣物，防晒用品"
        elif current_month in [9, 10, 11]:  # 秋季
            season = "秋季"
            temp_range = "10-20°C"
            condition = "凉爽干燥"
            rainfall = "较少"
            clothing = "长袖衣物，薄外套"
        else:  # 冬季
            season = "冬季"
            temp_range = "0-10°C"
            condition = "寒冷"
            rainfall = "较少"
            clothing = "厚外套，保暖衣物"
        
        return {
            "current_season": season,
            "temperature_range": temp_range,
            "weather_condition": condition,
            "rainfall_probability": rainfall,
            "clothing_suggestion": clothing,
            "forecast_days": 7,
            "last_updated": datetime.now().isoformat()
        }
    
    def _generate_cultural_info(self, destination: str) -> Dict[str, Any]:
        """生成文化信息"""
        return {
            "local_customs": [
                "尊重当地文化传统",
                "注意文明礼貌",
                "保持环境整洁"
            ],
            "taboos": [
                "不要大声喧哗",
                "不要随意拍照他人",
                "遵守景区规定"
            ],
            "tips": [
                "提前预订热门景点门票",
                "准备现金和移动支付",
                "下载当地地图应用",
                "学习基本当地用语"
            ],
            "emergency_contacts": {
                "police": "110",
                "fire": "119",
                "medical": "120",
                "tourist_hotline": "12301"
            }
        }

class ItineraryPlannerNode(BaseNode):
    """行程规划节点"""
    
    def __init__(self):
        super().__init__("行程规划器")
    
    async def process(self, state: AgentState) -> AgentState:
        """规划详细行程"""
        try:
            self.log("开始规划行程")
            
            travel_days = state.metadata.get("travel_days", 1)
            destination = state.metadata.get("destination_processed")
            travel_styles = state.metadata.get("travel_styles", [])
            interests = state.metadata.get("interests", [])
            
            itinerary = []
            
            for day in range(1, travel_days + 1):
                self.log(f"规划第{day}天行程")
                
                # 生成当日活动
                activities = await self._generate_daily_activities(
                    day, travel_styles, interests, destination, state
                )
                
                # 计算当日费用
                total_cost = sum(activity.cost or 0 for activity in activities)
                
                # 生成当日主题
                theme = self._get_day_theme(day, travel_styles, travel_days)
                
                itinerary_item = ItineraryItem(
                    day=day,
                    date=(state.request.start_date + timedelta(days=day-1)).strftime("%Y-%m-%d"),
                    theme=theme,
                    activities=activities,
                    total_cost=total_cost,
                    notes=self._generate_day_notes(day, travel_styles)
                )
                
                itinerary.append(itinerary_item)
            
            state.itinerary_draft = itinerary
            
            self.log(f"行程规划完成: {travel_days}天完整行程", "success")
            
        except Exception as e:
            error_msg = f"行程规划失败: {str(e)}"
            state.errors.append(error_msg)
            self.log(error_msg, "error")
        
        return state
    
    async def _generate_daily_activities(self, day: int, travel_styles: List[str], 
                                       interests: List[str], destination: str, 
                                       state: AgentState) -> List[ActivityItem]:
        """生成每日活动安排"""
        activities = []
        
        if day == 1:
            # 第一天：抵达和适应
            activities = [
                ActivityItem(
                    time="09:00",
                    activity="抵达目的地",
                    location=f"{destination}交通枢纽",
                    cost=0,
                    duration="1小时",
                    description="抵达并前往住宿地点，办理入住手续"
                ),
                ActivityItem(
                    time="11:00",
                    activity="住宿安排",
                    location="酒店/民宿",
                    cost=self._get_accommodation_cost(state.metadata.get("budget_level")),
                    duration="30分钟",
                    description="办理入住，稍作休息调整"
                ),
                ActivityItem(
                    time="14:00",
                    activity="欢迎午餐",
                    location="当地特色餐厅",
                    cost=self._get_meal_cost("lunch", state.metadata.get("budget_level")),
                    duration="1.5小时",
                    description="品尝当地特色美食，初步体验当地文化"
                ),
                ActivityItem(
                    time="16:00",
                    activity="城市初探",
                    location="市中心区域",
                    cost=50,
                    duration="3小时",
                    description="熟悉周边环境，轻松游览，适应当地节奏"
                )
            ]
        elif day == travel_days:
            # 最后一天：总结和离开
            activities = [
                ActivityItem(
                    time="08:00",
                    activity="告别早餐",
                    location="酒店或特色早餐店",
                    cost=self._get_meal_cost("breakfast", state.metadata.get("budget_level")),
                    duration="1小时",
                    description="享用最后一顿当地早餐"
                ),
                ActivityItem(
                    time="10:00",
                    activity="纪念品采购",
                    location="当地特产店",
                    cost=200,
                    duration="2小时",
                    description="购买纪念品和当地特产"
                ),
                ActivityItem(
                    time="13:00",
                    activity="退房整理",
                    location="酒店",
                    cost=0,
                    duration="1小时",
                    description="整理行李，办理退房手续"
                ),
                ActivityItem(
                    time="15:00",
                    activity="返程准备",
                    location="交通枢纽",
                    cost=0,
                    duration="2小时",
                    description="前往机场/车站，准备返程"
                )
            ]
        else:
            # 中间天数：完整游览
            activities = await self._generate_full_day_activities(
                day, travel_styles, interests, destination, state
            )
        
        return activities
    
    async def _generate_full_day_activities(self, day: int, travel_styles: List[str],
                                          interests: List[str], destination: str,
                                          state: AgentState) -> List[ActivityItem]:
        """生成完整一天的活动"""
        budget_level = state.metadata.get("budget_level")
        
        activities = [
            ActivityItem(
                time="08:00",
                activity="营养早餐",
                location="酒店或当地早餐店",
                cost=self._get_meal_cost("breakfast", budget_level),
                duration="1小时",
                description="享用丰盛早餐，为一天的行程储备能量"
            ),
            ActivityItem(
                time="09:30",
                activity=self._get_morning_activity(travel_styles, interests, destination),
                location=self._get_morning_location(travel_styles, destination),
                cost=self._get_activity_cost("morning", budget_level),
                duration="3小时",
                description="上午主要活动，深度体验当地特色"
            ),
            ActivityItem(
                time="12:30",
                activity="特色午餐",
                location=self._get_lunch_location(travel_styles, destination),
                cost=self._get_meal_cost("lunch", budget_level),
                duration="1小时",
                description="品尝当地特色午餐，补充体力"
            ),
            ActivityItem(
                time="15:00",
                activity=self._get_afternoon_activity(travel_styles, interests, destination),
                location=self._get_afternoon_location(travel_styles, destination),
                cost=self._get_activity_cost("afternoon", budget_level),
                duration="3小时",
                description="下午休闲活动，深入了解当地文化"
            ),
            ActivityItem(
                time="19:00",
                activity="精致晚餐",
                location=self._get_dinner_location(travel_styles, destination),
                cost=self._get_meal_cost("dinner", budget_level),
                duration="1.5小时",
                description="享用当地特色晚餐，回味一天的精彩"
            )
        ]
        
        # 根据旅行风格添加晚间活动
        if "夜生活" in travel_styles or "文化探索" in travel_styles:
            activities.append(
                ActivityItem(
                    time="21:00",
                    activity=self._get_evening_activity(travel_styles, destination),
                    location=self._get_evening_location(travel_styles, destination),
                    cost=self._get_activity_cost("evening", budget_level),
                    duration="2小时",
                    description="体验当地夜间文化，感受不同的城市魅力"
                )
            )
        
        return activities
    
    def _get_day_theme(self, day: int, travel_styles: List[str], total_days: int) -> str:
        """获取当日主题"""
        if day == 1:
            return "抵达适应日"
        elif day == total_days:
            return "告别纪念日"
        elif "文化探索" in travel_styles:
            return f"文化体验日 - 第{day-1}站"
        elif "美食之旅" in travel_styles:
            return f"美食探索日 - 第{day-1}站"
        elif "休闲度假" in travel_styles:
            return f"休闲放松日 - 第{day-1}站"
        elif "冒险刺激" in travel_styles:
            return f"探险体验日 - 第{day-1}站"
        else:
            return f"精彩游览日 - 第{day-1}站"
    
    def _generate_day_notes(self, day: int, travel_styles: List[str]) -> str:
        """生成当日注意事项"""
        base_notes = f"第{day}天行程安排，注意合理安排时间和体力。"
        
        if "冒险刺激" in travel_styles:
            base_notes += " 户外活动请注意安全，准备必要的防护用品。"
        
        if "美食之旅" in travel_styles:
            base_notes += " 建议预留足够时间品尝当地美食。"
        
        if "摄影打卡" in travel_styles:
            base_notes += " 记得充电和备用存储设备。"
        
        return base_notes
    
    def _get_accommodation_cost(self, budget_level: str) -> float:
        """获取住宿费用"""
        costs = {
            "经济型": 200,
            "舒适型": 500,
            "豪华型": 1000,
            "不限预算": 2000
        }
        return costs.get(budget_level, 500)
    
    def _get_meal_cost(self, meal_type: str, budget_level: str) -> float:
        """获取餐饮费用"""
        base_costs = {
            "breakfast": {"经济型": 30, "舒适型": 60, "豪华型": 120, "不限预算": 200},
            "lunch": {"经济型": 50, "舒适型": 100, "豪华型": 200, "不限预算": 400},
            "dinner": {"经济型": 80, "舒适型": 150, "豪华型": 300, "不限预算": 600}
        }
        return base_costs.get(meal_type, {}).get(budget_level, 100)
    
    def _get_activity_cost(self, time_period: str, budget_level: str) -> float:
        """获取活动费用"""
        base_costs = {
            "morning": {"经济型": 100, "舒适型": 200, "豪华型": 400, "不限预算": 800},
            "afternoon": {"经济型": 80, "舒适型": 150, "豪华型": 300, "不限预算": 600},
            "evening": {"经济型": 60, "舒适型": 120, "豪华型": 250, "不限预算": 500}
        }
        return base_costs.get(time_period, {}).get(budget_level, 150)
    
    def _get_morning_activity(self, travel_styles: List[str], interests: List[str], destination: str) -> str:
        """获取上午活动"""
        if "文化探索" in travel_styles:
            return f"{destination}博物馆深度游"
        elif "美食之旅" in travel_styles:
            return f"{destination}传统市场探索"
        elif "冒险刺激" in travel_styles:
            return f"{destination}户外探险体验"
        elif "摄影打卡" in travel_styles:
            return f"{destination}网红景点拍摄"
        else:
            return f"{destination}著名景点游览"
    
    def _get_afternoon_activity(self, travel_styles: List[str], interests: List[str], destination: str) -> str:
        """获取下午活动"""
        if "购物血拼" in travel_styles:
            return f"{destination}特色购物区"
        elif "休闲度假" in travel_styles:
            return f"{destination}公园休闲漫步"
        elif "文化探索" in travel_styles:
            return f"{destination}历史文化街区"
        else:
            return f"{destination}特色景点探索"
    
    def _get_evening_activity(self, travel_styles: List[str], destination: str) -> str:
        """获取晚间活动"""
        if "夜生活" in travel_styles:
            return f"{destination}夜市体验"
        elif "文化探索" in travel_styles:
            return f"{destination}夜间文化演出"
        else:
            return f"{destination}夜景观赏"
    
    def _get_morning_location(self, travel_styles: List[str], destination: str) -> str:
        """获取上午活动地点"""
        if "文化探索" in travel_styles:
            return f"{destination}博物馆区"
        elif "美食之旅" in travel_styles:
            return f"{destination}传统市场"
        else:
            return f"{destination}核心景区"
    
    def _get_afternoon_location(self, travel_styles: List[str], destination: str) -> str:
        """获取下午活动地点"""
        if "购物血拼" in travel_styles:
            return f"{destination}商业中心"
        elif "休闲度假" in travel_styles:
            return f"{destination}休闲公园"
        else:
            return f"{destination}文化区"
    
    def _get_lunch_location(self, travel_styles: List[str], destination: str) -> str:
        """获取午餐地点"""
        if "美食之旅" in travel_styles:
            return f"{destination}美食街"
        else:
            return f"{destination}特色餐厅"
    
    def _get_dinner_location(self, travel_styles: List[str], destination: str) -> str:
        """获取晚餐地点"""
        if "美食之旅" in travel_styles:
            return f"{destination}高档餐厅"
        else:
            return f"{destination}当地特色餐厅"
    
    def _get_evening_location(self, travel_styles: List[str], destination: str) -> str:
        """获取晚间活动地点"""
        if "夜生活" in travel_styles:
            return f"{destination}夜市区"
        else:
            return f"{destination}夜景观赏点"

class BudgetOptimizerNode(BaseNode):
    """预算优化节点"""
    
    def __init__(self):
        super().__init__("预算优化器")
    
    async def process(self, state: AgentState) -> AgentState:
        """优化预算分配"""
        try:
            self.log("开始预算优化")
            
            budget_level = state.metadata.get("budget_level")
            itinerary = state.itinerary_draft or []
            participant_count = state.metadata.get("participant_count", 1)
            
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
            per_person_cost = optimized_cost / participant_count
            
            # 详细预算分析
            budget_analysis = {
                "original_cost": total_cost,
                "optimized_cost": optimized_cost,
                "per_person_cost": per_person_cost,
                "budget_level": budget_level,
                "participant_count": participant_count,
                "cost_breakdown": {
                    "accommodation": optimized_cost * 0.35,
                    "food": optimized_cost * 0.30,
                    "activities": optimized_cost * 0.25,
                    "transportation": optimized_cost * 0.10
                },
                "daily_average": optimized_cost / len(itinerary) if itinerary else 0,
                "saving_tips": self._generate_saving_tips(budget_level),
                "budget_alerts": self._generate_budget_alerts(optimized_cost, budget_level)
            }
            
            state.budget_analysis = budget_analysis
            
            self.log(f"预算优化完成: 总预算 {optimized_cost:.0f} 元，人均 {per_person_cost:.0f} 元", "success")
            
        except Exception as e:
            error_msg = f"预算优化失败: {str(e)}"
            state.errors.append(error_msg)
            self.log(error_msg, "error")
        
        return state
    
    def _generate_saving_tips(self, budget_level: str) -> List[str]:
        """生成省钱建议"""
        base_tips = [
            "提前预订可享受早鸟优惠",
            "选择当地公共交通出行",
            "尝试当地平价美食",
            "关注景点免费开放日",
            "购买城市旅游通票"
        ]
        
        if budget_level == "经济型":
            base_tips.extend([
                "选择青年旅社或民宿",
                "自备水和小食",
                "利用免费WiFi避免漫游费",
                "参加免费的城市徒步游"
            ])
        
        return base_tips
    
    def _generate_budget_alerts(self, total_cost: float, budget_level: str) -> List[str]:
        """生成预算提醒"""
        alerts = []
        
        if budget_level == "经济型" and total_cost > 3000:
            alerts.append("当前预算较高，建议调整住宿和餐饮标准")
        
        if budget_level == "豪华型" and total_cost < 5000:
            alerts.append("可以考虑升级住宿或增加特色体验项目")
        
        alerts.append("建议预留10-20%的应急资金")
        alerts.append("部分费用可能因季节和实际情况有所变动")
        
        return alerts

class PersonalizationNode(BaseNode):
    """个性化推荐节点"""
    
    def __init__(self):
        super().__init__("个性化推荐器")
    
    async def process(self, state: AgentState) -> AgentState:
        """生成个性化推荐"""
        try:
            self.log("开始个性化推荐")
            
            travel_styles = state.metadata.get("travel_styles", [])
            interests = state.metadata.get("interests", [])
            destination_info = state.destination_info or {}
            participant_count = state.metadata.get("participant_count", 1)
            
            recommendations = []
            
            # 基于旅行风格的推荐
            recommendations.extend(self._get_style_recommendations(travel_styles))
            
            # 基于兴趣的推荐
            recommendations.extend(self._get_interest_recommendations(interests))
            
            # 基于人数的推荐
            recommendations.extend(self._get_group_recommendations(participant_count))
            
            # 基于目的地的推荐
            recommendations.extend(self._get_destination_recommendations(destination_info))
            
            # 通用实用建议
            recommendations.extend(self._get_general_recommendations())
            
            # 去重并限制数量
            unique_recommendations = list(dict.fromkeys(recommendations))[:15]
            
            state.recommendations = unique_recommendations
            
            self.log(f"个性化推荐完成: {len(unique_recommendations)}条建议", "success")
            
        except Exception as e:
            error_msg = f"个性化推荐失败: {str(e)}"
            state.errors.append(error_msg)
            self.log(error_msg, "error")
        
        return state
    
    def _get_style_recommendations(self, travel_styles: List[str]) -> List[str]:
        """基于旅行风格的推荐"""
        recommendations = []
        
        style_mapping = {
            "美食之旅": [
                "推荐尝试当地特色小吃街和夜市",
                "预约知名餐厅需提前1-2天订位",
                "可以参加当地烹饪课程体验",
                "准备肠胃药以防水土不服"
            ],
            "文化探索": [
                "建议购买博物馆和景点通票",
                "可以预约当地文化导览服务",
                "关注当地节庆活动和文化演出",
                "准备舒适的步行鞋"
            ],
            "摄影打卡": [
                "推荐最佳拍照时间：日出和日落",
                "准备充电宝和备用存储卡",
                "了解当地拍照礼仪和禁忌",
                "下载修图和滤镜应用"
            ],
            "购物血拼": [
                "了解当地退税政策和流程",
                "准备足够的行李空间",
                "关注当地购物节和折扣信息",
                "学习基本的砍价技巧"
            ],
            "休闲度假": [
                "选择交通便利的住宿地点",
                "安排充足的休息时间",
                "准备休闲娱乐用品",
                "关注当地SPA和按摩服务"
            ],
            "冒险刺激": [
                "购买旅行保险和意外险",
                "准备必要的防护装备",
                "了解当地安全注意事项",
                "确认身体状况适合参与活动"
            ]
        }
        
        for style in travel_styles:
            recommendations.extend(style_mapping.get(style, []))
        
        return recommendations
    
    def _get_interest_recommendations(self, interests: List[str]) -> List[str]:
        """基于兴趣的推荐"""
        recommendations = []
        
        for interest in interests:
            if "历史" in interest:
                recommendations.extend([
                    "推荐参观历史遗迹和古建筑",
                    "可以聘请专业历史导游"
                ])
            elif "自然" in interest:
                recommendations.extend([
                    "安排户外自然景观游览",
                    "准备防晒和防虫用品"
                ])
            elif "艺术" in interest:
                recommendations.extend([
                    "参观当地艺术馆和画廊",
                    "关注当地艺术家工作室开放日"
                ])
            elif "科技" in interest:
                recommendations.extend([
                    "参观科技馆和创新中心",
                    "体验当地高科技项目"
                ])
        
        return recommendations
    
    def _get_group_recommendations(self, participant_count: int) -> List[str]:
        """基于人数的推荐"""
        recommendations = []
        
        if participant_count == 1:
            recommendations.extend([
                "单人旅行注意安全，保持与家人联系",
                "可以参加当地旅行团结识朋友",
                "选择安全性较高的住宿区域"
            ])
        elif participant_count == 2:
            recommendations.extend([
                "情侣/朋友出行可以选择浪漫/有趣的活动",
                "预订双人间或情侣套餐",
                "安排一些私密的体验项目"
            ])
        elif participant_count >= 3:
            recommendations.extend([
                "团体出行建议创建群聊方便沟通",
                "提前确认每个人的兴趣偏好",
                "安排集合时间和地点",
                "考虑不同的预算需求",
                "可以预订团体票享受优惠"
            ])
        
        return recommendations
    
    def _get_destination_recommendations(self, destination_info: Dict[str, Any]) -> List[str]:
        """基于目的地的推荐"""
        recommendations = []
        
        if destination_info:
            # 基于当地交通
            transport = destination_info.get("transportation", {})
            if transport.get("recommended"):
                recommendations.append(f"推荐使用{transport['recommended']}出行")
            
            # 基于当地美食
            cuisine = destination_info.get("local_cuisine", [])
            if cuisine:
                recommendations.append(f"必尝当地特色：{', '.join(cuisine[:2])}")
            
            # 基于著名景点
            attractions = destination_info.get("famous_attractions", [])
            if attractions:
                recommendations.append(f"热门景点推荐：{', '.join(attractions[:3])}")
        
        return recommendations
    
    def _get_general_recommendations(self) -> List[str]:
        """通用实用建议"""
        return [
            "建议下载当地地图和翻译APP",
            "准备常用药品和个人护理用品",
            "了解当地紧急联系方式",
            "保持手机电量充足，准备充电宝",
            "购买旅行保险保障安全",
            "准备现金和确认银行卡境外使用",
            "提前了解当地天气准备合适衣物",
            "备份重要证件和联系方式"
        ]

class CollaborationNode(BaseNode):
    """协作处理节点"""
    
    def __init__(self):
        super().__init__("协作处理器")
    
    async def process(self, state: AgentState) -> AgentState:
        """处理多人旅行协作"""
        try:
            self.log("开始协作处理")
            
            participants = state.metadata.get("participant_count", 1)
            
            if participants > 1:
                # 多人旅行的协调建议
                collaboration_tips = self._generate_collaboration_tips(participants)
                
                # 添加到推荐列表
                if not state.recommendations:
                    state.recommendations = []
                
                state.recommendations.extend(collaboration_tips)
                
                # 生成协作计划
                collaboration_plan = self._generate_collaboration_plan(participants)
                state.metadata["collaboration_plan"] = collaboration_plan
                
                self.log(f"协作处理完成: {participants}人旅行协调方案", "success")
            else:
                self.log("单人旅行，无需协作处理", "info")
            
        except Exception as e:
            error_msg = f"协作处理失败: {str(e)}"
            state.errors.append(error_msg)
            self.log(error_msg, "error")
        
        return state
    
    def _generate_collaboration_tips(self, participants: int) -> List[str]:
        """生成协作建议"""
        tips = [
            "建议创建旅行群聊方便实时沟通",
            "提前确认每个人的兴趣偏好和预算",
            "安排明确的集合时间和地点",
            "准备所有人的应急联系方式",
            "轮流负责不同环节的决策避免分歧"
        ]
        
        if participants >= 4:
            tips.extend([
                "大团体建议指定1-2名协调员",
                "制定详细的时间表和集合规则",
                "考虑分组活动满足不同需求"
            ])
        
        if participants >= 6:
            tips.extend([
                "预订团体票和包车服务",
                "安排专门的行李和物品管理",
                "制定紧急情况应对预案"
            ])
        
        return tips
    
    def _generate_collaboration_plan(self, participants: int) -> Dict[str, Any]:
        """生成协作计划"""
        return {
            "participant_count": participants,
            "communication_tools": ["微信群", "共享日历", "位置共享"],
            "decision_making": "轮流决策" if participants <= 4 else "指定协调员",
            "emergency_plan": {
                "contact_method": "群聊 + 电话",
                "meeting_points": ["酒店大堂", "主要景点入口"],
                "backup_plan": "分组行动，晚上酒店汇合"
            },
            "budget_management": "AA制" if participants <= 4 else "指定财务管理员",
            "schedule_flexibility": "高" if participants <= 3 else "中等"
        }