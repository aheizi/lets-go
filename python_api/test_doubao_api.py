#!/usr/bin/env python3
"""
测试豆包API集成
"""

import asyncio
import json
from services.llm_service import llm_service

async def test_doubao_api():
    """测试豆包API调用"""
    print("🧪 开始测试豆包API...")
    
    try:
        # 测试目的地分析
        print("\n📍 测试目的地分析...")
        destination = "杭州"
        preferences = {
            "interests": ["自然风光", "历史文化"],
            "travel_style": "leisure",
            "budget_level": "medium"
        }
        
        analysis = await llm_service.generate_destination_analysis(destination, preferences)
        print(f"✅ 目的地分析结果: {analysis[:200]}...")
        
        # 测试每日行程生成
        print("\n📅 测试每日行程生成...")
        daily_plan = await llm_service.generate_daily_itinerary(
            destination=destination,
            day=1,
            total_days=3,
            preferences=preferences,
            budget_level="medium"
        )
        print(f"✅ 每日行程结果: {json.dumps(daily_plan, ensure_ascii=False, indent=2)}")
        
        # 测试旅行贴士
        print("\n💡 测试旅行贴士生成...")
        tips = await llm_service.generate_travel_tips(destination, preferences)
        print(f"✅ 旅行贴士结果: {tips}")
        
        print("\n🎉 所有测试通过！豆包API集成成功！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_doubao_api())