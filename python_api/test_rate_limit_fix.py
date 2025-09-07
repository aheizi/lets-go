#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试地图API频率控制和缓存机制
"""

import asyncio
import time
from services.map_service import MapService

async def test_rate_limit_and_cache():
    """测试频率控制和缓存机制"""
    print("=== 测试地图API频率控制和缓存机制 ===")
    
    map_service = MapService()
    
    # 测试1: 连续搜索同一个POI，验证缓存机制
    print("\n1. 测试缓存机制 - 连续搜索同一个POI")
    start_time = time.time()
    
    for i in range(3):
        print(f"\n第{i+1}次搜索河坊街:")
        result = await map_service.search_poi("河坊街", "杭州")
        print(f"  找到 {len(result)} 个结果")
        if result:
            print(f"  第一个结果: {result[0]['name']}")
    
    elapsed = time.time() - start_time
    print(f"\n总耗时: {elapsed:.2f}秒")
    
    # 测试2: 快速连续搜索不同POI，验证频率控制
    print("\n2. 测试频率控制 - 快速连续搜索不同POI")
    keywords = ["西湖", "雷峰塔", "断桥", "苏堤", "白堤"]
    
    start_time = time.time()
    for keyword in keywords:
        print(f"\n搜索: {keyword}")
        search_start = time.time()
        result = await map_service.search_poi(keyword, "杭州")
        search_time = time.time() - search_start
        print(f"  耗时: {search_time:.2f}秒, 找到 {len(result)} 个结果")
    
    total_elapsed = time.time() - start_time
    print(f"\n总耗时: {total_elapsed:.2f}秒")
    print(f"平均每次搜索: {total_elapsed/len(keywords):.2f}秒")
    
    # 测试3: 验证缓存命中
    print("\n3. 验证缓存命中 - 重复搜索之前的关键词")
    start_time = time.time()
    result = await map_service.search_poi("西湖", "杭州")
    elapsed = time.time() - start_time
    print(f"重复搜索西湖耗时: {elapsed:.2f}秒 (应该很快，因为有缓存)")
    print(f"找到 {len(result)} 个结果")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_rate_limit_and_cache())