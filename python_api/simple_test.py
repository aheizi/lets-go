#!/usr/bin/env python3
"""简化的NeMo Agent Toolkit集成测试"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nat_configs.nemo_wrapper import NeMoTravelAgent
from nat_configs.register import register_tools
from agents.travel_planner_agent import TravelPlannerAgent
from services.weather_service import WeatherService
from agents.models import TravelRequest
from datetime import datetime, date

def test_imports():
    """测试所有导入是否正常"""
    print("🔧 Testing Imports")
    print("=" * 30)
    
    try:
        # 测试NeMo包装器导入
        agent = NeMoTravelAgent()
        print("✅ NeMoTravelAgent imported successfully")
        
        # 测试工具注册
        tools = register_tools()
        print(f"✅ Tools registered: {list(tools.keys())}")
        
        # 测试原始组件导入
        travel_agent = TravelPlannerAgent()
        weather_service = WeatherService()
        print("✅ Original components imported successfully")
        
        # 测试模型创建
        request = TravelRequest(
            destination="宜昌",
            start_date=date.today(),
            end_date=date.today(),
            budget_level="舒适型",
            travel_style="休闲度假"
        )
        print("✅ TravelRequest model created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_configuration():
    """测试配置信息"""
    print("\n🔧 Testing Configuration")
    print("=" * 30)
    
    try:
        agent = NeMoTravelAgent()
        config = agent.get_config_