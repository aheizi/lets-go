#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的地图服务与智能体集成
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.map_service import MapService
from agents.travel_planner_agent import TravelPlannerAgent
from agents.models import TravelRequest

async def test_map_service_fix():
    """测试修复后的地图服务"""
    print("=== 测试修复后的地图服务 ===")
    
    # 初始化地图服务
    map_service = MapService()
    
    # 测试POI搜索的数据结构
    print("\n1. 测试POI搜索数据结构...")
    pois = await map_service.search_poi("故宫", "北京")
    
    if pois:
        poi = pois[0]
        print(f"POI名称: {poi.get('name')}")
        print(f"地址: {poi.get('address')}")
        print(f"格式化地址: {poi.get('formatted_address')}")
        print(f"坐标: {poi.get('coordinates')}")
        print(f"位置字符串: {poi.get('location')}")
        
        # 检查必要字段
        required_fields = ['name', 'formatted_address', 'coordinates']
        missing_fields = [field for field in required_fields if field not in poi or poi[field] is None]
        
        if missing_fields:
            print(f"❌ 缺少必要字段: {missing_fields}")
        else:
            print("✅ POI数据结构正确")
    else:
        print("❌ POI搜索失败")
    
    # 测试与智能体的集成
    print("\n2. 测试与旅行规划智能体的集成...")
    try:
        # 创建旅行请求
        travel_request = TravelRequest(
            destination="北京",
            start_date="2024-03-01",
            end_date="2024-03-03",
            budget_level="舒适型",
            travel_style="文化探索",
            group_size=2
        )
        
        # 初始化智能体
        agent = TravelPlannerAgent()
        
        # 测试_get_location_info方法
        if hasattr(agent, '_get_location_info') and pois:
            location_info = await agent._get_location_info("故宫", "北京")
            print(f"位置信息获取结果: {location_info}")
            
            if location_info and 'formatted_address' in location_info:
                print("✅ 智能体能正确获取位置信息")
            else:
                print("❌ 智能体获取位置信息失败")
        else:
            print("⚠️  无法测试_get_location_info方法")
            
    except Exception as e:
        print(f"❌ 智能体集成测试失败: {str(e)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_map_service_fix())