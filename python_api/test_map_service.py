#!/usr/bin/env python3
"""测试地图服务功能"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from services.map_service import map_service

async def test_map_service():
    """测试地图服务的各项功能"""
    print("=== 开始测试地图服务功能 ===")
    
    # 测试1: 地理编码
    print("\n1. 测试地理编码功能")
    try:
        result = await map_service.geocode("天安门", "北京")
        if result:
            print(f"✅ 地理编码成功: {result['address']}")
            print(f"   坐标: ({result['longitude']}, {result['latitude']})")
        else:
            print("❌ 地理编码失败")
    except Exception as e:
        print(f"❌ 地理编码异常: {str(e)}")
    
    # 测试2: POI搜索
    print("\n2. 测试POI搜索功能")
    test_keywords = ["故宫", "餐厅", "酒店", "景点"]
    
    for keyword in test_keywords:
        try:
            print(f"\n搜索关键词: {keyword}")
            pois = await map_service.search_poi(keyword, "北京")
            if pois and len(pois) > 0:
                print(f"✅ POI搜索成功，找到 {len(pois)} 个结果")
                for i, poi in enumerate(pois[:3]):  # 只显示前3个结果
                    print(f"   {i+1}. {poi['name']} - {poi['address']}")
            else:
                print(f"❌ POI搜索失败: {keyword}")
        except Exception as e:
            print(f"❌ POI搜索异常 ({keyword}): {str(e)}")
    
    # 测试3: 逆地理编码
    print("\n3. 测试逆地理编码功能")
    try:
        result = await map_service.reverse_geocode(116.3974, 39.9093)  # 天安门坐标
        if result:
            print(f"✅ 逆地理编码成功: {result['formatted_address']}")
        else:
            print("❌ 逆地理编码失败")
    except Exception as e:
        print(f"❌ 逆地理编码异常: {str(e)}")
    
    # 测试4: 路线规划
    print("\n4. 测试路线规划功能")
    try:
        origin = (116.3974, 39.9093)  # 天安门
        destination = (116.3972, 39.9180)  # 故宫
        result = await map_service.get_route(origin, destination)
        if result:
            print(f"✅ 路线规划成功")
            print(f"   距离: {result['formatted_distance']}")
            print(f"   时间: {result['formatted_duration']}")
        else:
            print("❌ 路线规划失败")
    except Exception as e:
        print(f"❌ 路线规划异常: {str(e)}")
    
    print("\n=== 地图服务测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_map_service())