"""NeMo Agent Toolkit - Travel Planner Tools Registration"""

import sys
import os
from typing import Dict, Any
import asyncio
from datetime import datetime

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.travel_planner_agent import TravelPlannerAgent
from services.weather_service import WeatherService


class TravelPlannerTool:
    """Travel Planner Tool for NeMo Agent Toolkit"""
    
    def __init__(self):
        self.agent = TravelPlannerAgent()
        self.weather_service = WeatherService()
    
    async def travel_planner(self, destination: str, start_date: str, end_date: str, 
                             budget: float = 2000, preferences: str = "") -> dict:
        """旅行规划工具"""
        try:
            # 创建旅行请求
            from agents.models import TravelRequest
            from datetime import datetime
            
            request = TravelRequest(
                user_id="nemo_user",
                destination=destination,
                start_date=datetime.fromisoformat(start_date.replace('Z', '')),
                end_date=datetime.fromisoformat(end_date.replace('Z', '')),
                budget_level="中等" if budget < 3000 else "高端",
                group_size=1,
                travel_style=["休闲观光"],
                interests=[preferences] if preferences else ["文化探索"]
            )
            
            # 使用智能体生成计划
            result = await self.agent.generate_travel_plan(request)
            return result
            
        except Exception as e:
            return {"error": f"旅行规划失败: {str(e)}"}
    
    async def weather_info(self, location: str, date: str = None) -> Dict[str, Any]:
        """获取天气信息工具"""
        try:
            if date:
                # 获取特定日期的天气预报
                forecast = await self.weather_service.get_forecast(location, days=7)
                return {
                    "success": True,
                    "data": forecast,
                    "message": f"获取{location}天气预报成功"
                }
            else:
                # 获取当前天气
                current_weather = await self.weather_service.get_current_weather(location)
                return {
                    "success": True,
                    "data": current_weather,
                    "message": f"获取{location}当前天气成功"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "获取天气信息失败"
            }


# Tool registration for NeMo Agent Toolkit
def register_tools():
    """Register travel planning tools with NeMo Agent Toolkit"""
    tool_instance = TravelPlannerTool()
    
    return {
        "travel_planner": tool_instance.travel_planner,
        "weather_info": tool_instance.weather_info
    }


# For direct usage
if __name__ == "__main__":
    # Example usage
    async def test_tools():
        tools = register_tools()
        
        # Test travel planner
        result = await tools["travel_planner"](
            destination="Tokyo, Japan",
            start_date="2024-03-15",
            end_date="2024-03-20",
            budget=2000,
            preferences="Cultural sites, local food, moderate budget accommodation"
        )
        print("Travel Planner Result:", result)
        
        # Test weather info
        weather_result = await tools["weather_info"](
            location="Tokyo, Japan",
            date="2024-03-15"
        )
        print("Weather Info Result:", weather_result)
    
    asyncio.run(test_tools())