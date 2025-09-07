"""旅行规划数据模型"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum

class TravelStyle(str, Enum):
    """旅行风格枚举"""
    LEISURE = "休闲度假"
    CULTURE = "文化探索"
    FOOD = "美食之旅"
    ADVENTURE = "冒险刺激"
    SHOPPING = "购物血拼"
    PHOTOGRAPHY = "摄影打卡"
    FAMILY = "亲子游"
    ROMANTIC = "情侣游"

class BudgetLevel(str, Enum):
    """预算等级"""
    LOW = "经济型"
    MEDIUM = "舒适型"
    HIGH = "豪华型"
    UNLIMITED = "不限预算"

class TravelRequest(BaseModel):
    """旅行请求模型"""
    destination: str = Field(..., description="目的地")
    start_date: date = Field(..., description="出发日期")
    end_date: date = Field(..., description="返回日期")
    group_size: int = Field(default=1, ge=1, description="参与人数")
    budget_level: str = Field(..., description="预算等级")
    travel_style: str = Field(..., description="旅行风格")
    interests: List[str] = Field(default=[], description="兴趣爱好")
    special_requirements: Optional[str] = Field(None, description="特殊要求")
    user_id: Optional[str] = Field(None, description="用户ID")

class ActivityItem(BaseModel):
    """活动项目模型"""
    time: str = Field(..., description="时间")
    activity: str = Field(..., description="活动名称")
    location: str = Field(..., description="地点")
    cost: Optional[float] = Field(None, description="费用")
    duration: Optional[str] = Field(None, description="持续时间")
    description: Optional[str] = Field(None, description="活动描述")
    tips: Optional[str] = Field(None, description="小贴士")

class ItineraryItem(BaseModel):
    """行程项目模型"""
    day: int = Field(..., description="第几天")
    date: str = Field(..., description="日期")
    theme: Optional[str] = Field(None, description="当日主题")
    activities: List[ActivityItem] = Field(default=[], description="活动列表")
    total_cost: Optional[float] = Field(None, description="当日总费用")
    notes: Optional[str] = Field(None, description="备注")

class TravelPlan(BaseModel):
    """旅行计划模型"""
    plan_id: str = Field(..., description="计划ID")
    title: str = Field(..., description="计划标题")
    destination: str = Field(..., description="目的地")
    start_date: date = Field(..., description="出发日期")
    end_date: date = Field(..., description="返回日期")
    group_size: int = Field(..., description="参与人数")
    budget_estimate: Optional[float] = Field(None, description="预算估算")
    itinerary: List[ItineraryItem] = Field(default=[], description="行程安排")
    recommendations: List[str] = Field(default=[], description="推荐建议")
    weather_info: Optional[Dict[str, Any]] = Field(None, description="天气信息")
    cultural_tips: List[str] = Field(default=[], description="文化小贴士")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class AgentState(BaseModel):
    """智能体状态模型"""
    request: TravelRequest
    destination_info: Optional[Dict[str, Any]] = None
    weather_data: Optional[Dict[str, Any]] = None
    cultural_info: Optional[Dict[str, Any]] = None
    budget_analysis: Optional[Dict[str, Any]] = None
    itinerary_draft: Optional[List[ItineraryItem]] = None
    recommendations: List[str] = Field(default=[])
    current_step: str = Field(default="start")
    errors: List[str] = Field(default=[])
    metadata: Dict[str, Any] = Field(default={})

class PlanGenerationResponse(BaseModel):
    """计划生成响应模型"""
    success: bool = Field(..., description="是否成功")
    plan_id: Optional[str] = Field(None, description="计划ID")
    plan: Optional[TravelPlan] = Field(None, description="生成的旅行计划")
    message: str = Field(..., description="响应消息")
    processing_time: Optional[float] = Field(None, description="处理时间（秒）")
    agent_steps: List[str] = Field(default=[], description="智能体执行步骤")