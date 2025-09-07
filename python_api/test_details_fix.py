#!/usr/bin/env python3
"""测试详细行程展开功能修复"""

import asyncio
import json
from services.llm_service import DoubaoLLMService

async def test_details_structure():
    """测试生成的行程数据是否包含详细信息字段"""
    print("=== 测试详细行程数据结构 ===")
    
    llm_service = DoubaoLLMService()
    
    # 测试生成行程
    try:
        result = await llm_service.generate_daily_itinerary(
            destination="北京",
            day=1,
            total_days=1,
            preferences={"interests": ["历史文化", "美食"]},
            budget_level="舒适型"
        )
        
        print("\n生成的行程数据:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 检查数据结构
        if 'daily_plans' in result:
            for day_key, day_data in result['daily_plans'].items():
                print(f"\n检查 {day_key} 的数据结构:")
                
                # 检查各个时段
                time_slots = ['breakfast', 'morning', 'lunch', 'afternoon', 'dinner', 'evening']
                for slot in time_slots:
                    if slot in day_data:
                        slot_data = day_data[slot]
                        print(f"\n{slot} 字段:")
                        
                        # 检查必需的详细字段
                        required_fields = ['name', 'address', 'openTime', 'ticketPrice', 'specialties', 'features', 'tips', 'cost']
                        missing_fields = []
                        
                        for field in required_fields:
                            if field in slot_data:
                                print(f"  ✅ {field}: {slot_data[field]}")
                            else:
                                missing_fields.append(field)
                                print(f"  ❌ 缺少字段: {field}")
                        
                        if not missing_fields:
                            print(f"  🎉 {slot} 包含所有必需字段!")
                        else:
                            print(f"  ⚠️  {slot} 缺少字段: {missing_fields}")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_details_structure())