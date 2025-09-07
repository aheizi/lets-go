#!/usr/bin/env python3
"""测试旅行规划智能体的地图功能集成"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from agents.travel_planner_agent import TravelPlannerAgent
from agents.models import TravelRequest
from datetime import date, timedelta

async def test_travel_agent_map_integration():
    """测试旅行规划智能体的地图功能集成"""
    print("=== 测试旅行规划智能体地图功能集成 ===")
    
    # 创建测试请求
    travel_request = TravelRequest(
        destination="北京",
        start_date=date.today() + timedelta(days=7),
        end_date=date.today() + timedelta(days=10),
        group_size=2,
        budget_level="舒适型",
        travel_style="文化探索",
        interests=["历史文化", "美食"]
    )
    
    # 创建智能体实例
    agent = TravelPlannerAgent()
    
    print(f"\n目的地: {travel_request.destination}")
    print(f"出行日期: {travel_request.start_date} 到 {travel_request.end_date}")
    print(f"人数: {travel_request.group_size}")
    print(f"预算: {travel_request.budget_level}")
    print(f"兴趣: {', '.join(travel_request.interests)}")
    
    try:
        print("\n开始生成旅行计划...")
        result = await agent.generate_travel_plan(travel_request)
        
        if result and result.get('success'):
            plan = result['plan']
            print(f"\n✅ 旅行计划生成成功!")
            print(f"计划ID: {plan.id}")
            print(f"目的地: {plan.destination}")
            print(f"总天数: {len(plan.daily_itineraries)}天")
            
            # 检查每日行程中的地理位置信息
            for i, day in enumerate(plan.daily_itineraries, 1):
                print(f"\n第{i}天 ({day.date}):")
                print(f"  活动数量: {len(day.activities)}")
                
                for j, activity in enumerate(day.activities, 1):
                    print(f"  {j}. {activity.name}")
                    if hasattr(activity, 'location') and activity.location:
                        print(f"     位置: {activity.location}")
                    if hasattr(activity, 'coordinates') and activity.coordinates:
                        print(f"     坐标: {activity.coordinates}")
                    if hasattr(activity, 'address') and activity.address:
                        print(f"     地址: {activity.address}")
            
            print(f"\n旅行贴士数量: {len(plan.travel_tips)}")
            
        else:
            error_msg = result.get('error', '未知错误') if result else '生成失败'
            print(f"❌ 旅行计划生成失败: {error_msg}")
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 旅行规划智能体地图功能集成测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_travel_agent_map_integration())