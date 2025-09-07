#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试位置信息解析修复功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.travel_planner_agent import TravelPlannerAgent
from services.llm_service import DoubaoLLMService

async def test_location_parsing():
    """测试位置信息解析功能"""
    print("=== 测试位置信息解析修复功能 ===")
    
    # 初始化服务
    agent = TravelPlannerAgent()
    llm_service = DoubaoLLMService()
    
    # 测试用例：各种可能出现问题的位置名称
    test_cases = [
        {
            "location": "景点",
            "destination": "杭州",
            "description": "纯通用词汇"
        },
        {
            "location": "西湖景点",
            "destination": "杭州",
            "description": "包含具体地名的通用词汇"
        },
        {
            "location": "餐厅",
            "destination": "杭州",
            "description": "餐厅通用词汇"
        },
        {
            "location": "",
            "destination": "杭州",
            "description": "空字符串"
        },
        {
            "location": "待定",
            "destination": "杭州",
            "description": "待定状态"
        },
        {
            "location": "当地",
            "destination": "杭州",
            "description": "太短的关键词"
        }
    ]
    
    print("\n开始测试位置信息解析...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {test_case['description']} ---")
        print(f"输入位置: '{test_case['location']}'")
        print(f"目的地: {test_case['destination']}")
        
        try:
            # 测试位置信息获取
            result = await agent._get_location_info(
                test_case['location'], 
                test_case['destination']
            )
            
            print(f"✅ 解析成功:")
            print(f"  - 格式化地址: {result.get('formatted_address', 'N/A')}")
            print(f"  - 坐标: {result.get('coordinates', {})}")
            print(f"  - POI信息: {result.get('poi_info', 'N/A')[:50]}...")
            
        except Exception as e:
            print(f"❌ 解析失败: {e}")
    
    print("\n=== 测试LLM服务的行程解析功能 ===")
    
    # 测试AI生成内容的解析
    test_ai_content = """
    上午：参观西湖风景区，欣赏湖光山色
    中午：在楼外楼餐厅享用正宗杭帮菜
    下午：游览灵隐寺，感受佛教文化
    晚上：漫步河坊街，品尝当地小吃
    """
    
    print(f"\n测试AI内容解析:")
    print(f"输入内容: {test_ai_content.strip()}")
    
    try:
        parsed_result = llm_service._parse_daily_itinerary(test_ai_content, 1)
        print(f"✅ 解析成功:")
        for period, activity in parsed_result.items():
            print(f"  - {period}: {activity}")
        
        # 调试信息：显示解析的详细过程
        print("\n调试信息:")
        lines = test_ai_content.split('\n')
        print(f"输入行数: {len(lines)}")
        for i, line in enumerate(lines):
            print(f"  行{i}: '{line.strip()}'")
            
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_location_parsing())