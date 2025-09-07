#!/usr/bin/env python3
"""Test script for NeMo Agent Toolkit integration"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add nat_configs to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'nat_configs'))

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.travel_planner_agent import TravelPlannerAgent
from services.weather_service import WeatherService

try:
    from nat_configs.nemo_wrapper import NeMoTravelAgent, quick_plan_trip
    from nat_configs.register import register_tools
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed and paths are correct.")
    sys.exit(1)


async def test_basic_functionality():
    """Test basic NeMo Agent Toolkit integration functionality"""
    print("🚀 Testing NeMo Agent Toolkit Integration")
    print("=" * 50)
    
    try:
        # Test 1: Initialize agent
        print("\n1. Initializing NeMo Travel Agent...")
        agent = NeMoTravelAgent()
        config_info = agent.get_config_info()
        print(f"✅ Agent initialized successfully")
        print(f"   Config path: {config_info['config_path']}")
        print(f"   Available workflows: {config_info['workflows']}")
        print(f"   Available tools: {config_info['available_tools']}")
        
        # Test 2: Test tool registration
        print("\n2. Testing tool registration...")
        tools = register_tools()
        print(f"✅ Tools registered: {list(tools.keys())}")
        
        # Test 3: Test quick trip planning function
        print("\n3. Testing quick trip planning...")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        day_after_tomorrow = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        result = await quick_plan_trip(
            destination="宜昌",
            start_date=tomorrow,
            end_date=day_after_tomorrow,
            budget=2000
        )
        
        if result.get("success"):
            print("✅ Quick trip planning successful")
            print(f"   Message: {result.get('message')}")
            if 'data' in result:
                print(f"   Data keys: {list(result['data'].keys()) if isinstance(result['data'], dict) else 'Non-dict data'}")
        else:
            print(f"❌ Quick trip planning failed: {result.get('error', 'Unknown error')}")
        
        # Test 4: Test weather information
        print("\n4. Testing weather information...")
        weather_result = await agent.get_weather("宜昌", tomorrow)
        
        if weather_result.get("success"):
            print("✅ Weather information retrieval successful")
            print(f"   Message: {weather_result.get('message')}")
        else:
            print(f"❌ Weather information failed: {weather_result.get('error', 'Unknown error')}")
        
        # Test 5: Test full agent trip planning
        print("\n5. Testing full agent trip planning...")
        full_result = await agent.plan_trip(
            destination="宜昌",
            start_date=tomorrow,
            end_date=day_after_tomorrow,
            budget=1800,
            preferences="三峡大坝, 清江画廊, 当地美食"
        )
        
        if full_result.get("success"):
            print("✅ Full agent trip planning successful")
            print(f"   Message: {full_result.get('message')}")
        else:
            print(f"❌ Full agent trip planning failed: {full_result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 50)
        print("🎉 NeMo Agent Toolkit integration test completed!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """Test error handling scenarios"""
    print("\n🔧 Testing Error Handling")
    print("=" * 30)
    
    try:
        agent = NeMoTravelAgent()
        
        # Test invalid date format
        print("\n1. Testing invalid date format...")
        result = await agent.plan_trip(
            destination="London, UK",
            start_date="invalid-date",
            end_date="2024-12-31",
            budget=1000
        )
        
        if not result.get("success"):
            print("✅ Invalid date handling works correctly")
            print(f"   Error: {result.get('error')}")
        else:
            print("⚠️  Invalid date was not caught")
        
        # Test missing destination
        print("\n2. Testing empty destination...")
        result = await agent.plan_trip(
            destination="",
            start_date="2024-12-01",
            end_date="2024-12-05"
        )
        
        if not result.get("success"):
            print("✅ Empty destination handling works correctly")
            print(f"   Error: {result.get('error')}")
        else:
            print("⚠️  Empty destination was not caught")
        
        print("\n" + "=" * 30)
        print("✅ Error handling test completed")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")


def print_usage_instructions():
    """Print usage instructions for the NeMo integration"""
    print("\n📖 Usage Instructions")
    print("=" * 50)
    print("""
1. Basic Usage:
   from nat_configs.nemo_wrapper import NeMoTravelAgent
   
   agent = NeMoTravelAgent()
   result = await agent.plan_trip(
       destination="Tokyo, Japan",
       start_date="2024-04-01",
       end_date="2024-04-05",
       budget=2000,
       preferences="Cultural sites, local food"
   )

2. Quick Usage:
   from nat_configs.nemo_wrapper import quick_plan_trip
   
   result = await quick_plan_trip(
       "Paris, France", "2024-04-01", "2024-04-05", 1500
   )

3. Weather Information:
   weather = await agent.get_weather("Tokyo, Japan", "2024-04-01")

4. Configuration:
   config_info = agent.get_config_info()
   
5. Direct Tool Access:
   from nat_configs.register import register_tools
   tools = register_tools()
   result = await tools["travel_planner"](...)
""")
    print("=" * 50)


async def main():
    """Main test function"""
    print("🧪 NeMo Agent Toolkit Integration Test Suite")
    print("=" * 60)
    
    # Run basic functionality tests
    basic_success = await test_basic_functionality()
    
    # Run error handling tests
    await test_error_handling()
    
    # Print usage instructions
    print_usage_instructions()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    if basic_success:
        print("✅ Basic functionality: PASSED")
        print("✅ Integration: SUCCESSFUL")
        print("\n🎯 The NeMo Agent Toolkit integration is ready to use!")
    else:
        print("❌ Basic functionality: FAILED")
        print("❌ Integration: NEEDS ATTENTION")
        print("\n⚠️  Please check the error messages above and fix any issues.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("nat_configs"):
        print("❌ Error: nat_configs directory not found.")
        print("Please run this script from the python_api directory.")
        sys.exit(1)
    
    # Run the tests
    asyncio.run(main())