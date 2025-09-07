"""Simple NeMo Agent Toolkit Wrapper for Travel Planner"""

import os
import sys
import yaml
import asyncio
from typing import Dict, Any, Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from register import register_tools


class NeMoTravelAgent:
    """Simplified NeMo Agent Toolkit wrapper for travel planning"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the NeMo Travel Agent
        
        Args:
            config_path: Path to the YAML configuration file
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "travel_agent.yml")
        
        self.config_path = config_path
        self.config = self._load_config()
        self.tools = register_tools()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_path}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if YAML loading fails"""
        return {
            "workflows": {
                "travel_planning_agent": {
                    "name": "travel_planning_agent",
                    "description": "Travel planning agent",
                    "tools": ["travel_planner", "weather_info"],
                    "max_iterations": 10,
                    "verbose": True
                }
            },
            "default_workflow": "travel_planning_agent"
        }
    
    async def plan_trip(self, destination: str, start_date: str, end_date: str, 
                        budget: float = 2000, preferences: str = "") -> dict:
        """规划旅行行程"""
        try:
            # 直接使用TravelPlannerAgent
            from agents.models import TravelRequest
            from datetime import datetime
            import logging
            
            # 创建TravelRequest对象
            logging.info(f"解析日期: start_date={start_date}, end_date={end_date}")
            
            # 修复日期解析逻辑
            try:
                if 'T' in start_date or 'Z' in start_date:
                    # ISO格式日期时间
                    start_date_obj = datetime.fromisoformat(start_date.replace('Z', '')).date()
                else:
                    # YYYY-MM-DD格式日期
                    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                    
                if 'T' in end_date or 'Z' in end_date:
                    # ISO格式日期时间
                    end_date_obj = datetime.fromisoformat(end_date.replace('Z', '')).date()
                else:
                    # YYYY-MM-DD格式日期
                    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                    
                logging.info(f"解析后的日期: start_date_obj={start_date_obj}, end_date_obj={end_date_obj}")
            except ValueError as date_error:
                logging.error(f"日期解析错误: {date_error}")
                return {"error": f"日期格式错误: {str(date_error)}"}
            
            travel_request = TravelRequest(
                destination=destination,
                start_date=start_date_obj,
                end_date=end_date_obj,
                budget_level="舒适型",
                travel_style=preferences if preferences else "休闲度假"
            )
            
            from agents.travel_planner_agent import TravelPlannerAgent
            agent = TravelPlannerAgent()
            result = await agent.generate_travel_plan(travel_request)
            return result
        except Exception as e:
            return {"error": f"行程规划失败: {str(e)}"}
    
    async def get_weather(self, location: str, date: str = None) -> Dict[str, Any]:
        """获取天气信息
        
        Args:
            location: 地点名称
            date: 日期（可选）
            
        Returns:
            包含天气信息的字典
        """
        try:
            from services.weather_service import WeatherService
            weather_service = WeatherService()
            
            if date:
                # 获取天气预报
                result = await weather_service.get_forecast(location, days=7)
            else:
                # 获取当前天气
                result = await weather_service.get_current_weather(location)
            
            return {
                "success": True,
                "data": result,
                "message": f"获取{location}天气信息成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "获取天气信息失败"
            }
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get configuration information"""
        return {
            "config_path": self.config_path,
            "workflows": list(self.config.get("workflows", {}).keys()),
            "default_workflow": self.config.get("default_workflow"),
            "available_tools": list(self.tools.keys())
        }


# Convenience function for quick usage
async def quick_plan_trip(destination: str, start_date: str, end_date: str, 
                          budget: float = 2000, preferences: str = "") -> Dict[str, Any]:
    """快速旅行规划函数
    
    Args:
        destination: 目的地城市或国家
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD
        budget: 预算（默认：2000）
        
    Returns:
        包含旅行计划结果的字典
    """
    try:
        from agents.models import TravelRequest
        from agents.travel_planner_agent import TravelPlannerAgent
        from datetime import datetime
        import logging
        
        logging.info(f"快速规划 - 解析日期: start_date={start_date}, end_date={end_date}")
        
        # 修复日期解析逻辑
        try:
            if 'T' in start_date or 'Z' in start_date:
                # ISO格式日期时间
                start_date_obj = datetime.fromisoformat(start_date.replace('Z', '')).date()
            else:
                # YYYY-MM-DD格式日期
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                
            if 'T' in end_date or 'Z' in end_date:
                # ISO格式日期时间
                end_date_obj = datetime.fromisoformat(end_date.replace('Z', '')).date()
            else:
                # YYYY-MM-DD格式日期
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                
            logging.info(f"快速规划 - 解析后的日期: start_date_obj={start_date_obj}, end_date_obj={end_date_obj}")
        except ValueError as date_error:
            logging.error(f"快速规划 - 日期解析错误: {date_error}")
            return {"error": f"日期格式错误: {str(date_error)}"}
        
        request = TravelRequest(
            user_id="quick_user",
            destination=destination,
            start_date=start_date_obj,
            end_date=end_date_obj,
            budget_level="中等" if budget < 3000 else "高端",
            group_size=1,
            travel_style=preferences if preferences else "休闲观光",
            interests=["文化探索"]
        )
        
        agent = TravelPlannerAgent()
        result = await agent.generate_travel_plan(request)
        
        # 检查结果是否成功
        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("message", "规划失败"),
                "message": "快速规划失败"
            }
        
        # 直接返回TravelPlannerAgent的结果，但修改message
        result["message"] = "快速规划完成"
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"快速规划失败: {str(e)}",
            "message": "快速规划失败"
        }


if __name__ == "__main__":
    # Example usage
    async def main():
        agent = NeMoTravelAgent()
        
        print("NeMo Travel Agent Configuration:")
        print(agent.get_config_info())
        print("\n" + "="*50 + "\n")
        
        # Test trip planning
        result = await agent.plan_trip(
            destination="Paris, France",
            start_date="2024-04-01",
            end_date="2024-04-05",
            budget=1500,
            preferences="Art museums, cafes, romantic atmosphere"
        )
        
        print("Trip Planning Result:")
        print(result)
        print("\n" + "="*50 + "\n")
        
        # Test weather info
        weather = await agent.get_weather("Paris, France", "2024-04-01")
        print("Weather Information:")
        print(weather)
    
    asyncio.run(main())