# NeMo Agent Toolkit Integration for Travel Planner

这是一个将现有的旅行规划智能体集成到NeMo Agent Toolkit中的简单实现。

## 文件结构

```
nat_configs/
├── __init__.py              # 包初始化文件
├── travel_agent.yml         # NeMo Agent Toolkit配置文件
├── register.py              # 工具注册文件
├── nemo_wrapper.py          # 简化的包装器
└── README.md               # 本文档
```

## 快速开始

### 1. 基本使用

```python
import asyncio
from nat_configs.nemo_wrapper import NeMoTravelAgent

async def main():
    # 初始化智能体
    agent = NeMoTravelAgent()
    
    # 规划旅行
    result = await agent.plan_trip(
        destination="东京, 日本",
        start_date="2024-04-01",
        end_date="2024-04-05",
        budget=2000,
        preferences="文化景点, 当地美食, 中等预算住宿"
    )
    
    print(result)

asyncio.run(main())
```

### 2. 快速规划函数

```python
import asyncio
from nat_configs.nemo_wrapper import quick_plan_trip

async def main():
    result = await quick_plan_trip(
        "巴黎, 法国", 
        "2024-04-01", 
        "2024-04-05", 
        1500, 
        "艺术博物馆, 咖啡厅, 浪漫氛围"
    )
    print(result)

asyncio.run(main())
```

### 3. 获取天气信息

```python
import asyncio
from nat_configs.nemo_wrapper import NeMoTravelAgent

async def main():
    agent = NeMoTravelAgent()
    
    weather = await agent.get_weather("东京, 日本", "2024-04-01")
    print(weather)

asyncio.run(main())
```

### 4. 直接使用工具

```python
import asyncio
from nat_configs.register import register_tools

async def main():
    tools = register_tools()
    
    # 使用旅行规划工具
    result = await tools["travel_planner"](
        destination="京都, 日本",
        start_date="2024-04-01",
        end_date="2024-04-03",
        budget=1000,
        preferences="传统文化, 寺庙, 和食"
    )
    
    print(result)

asyncio.run(main())
```

## 配置说明

### travel_agent.yml

这是NeMo Agent Toolkit的主配置文件，定义了：

- **工具 (tools)**: `travel_planner` 和 `weather_info`
- **LLM配置**: OpenAI GPT-4 配置
- **工作流 (workflows)**: 旅行规划智能体工作流
- **系统提示**: 智能体的行为指导

### 主要组件

1. **TravelPlannerTool**: 包装现有的旅行规划智能体
2. **NeMoTravelAgent**: 简化的接口类
3. **register_tools()**: 工具注册函数
4. **quick_plan_trip()**: 快速使用函数

## 测试

运行测试脚本来验证集成：

```bash
cd python_api
python test_nemo_integration.py
```

测试包括：
- 基本功能测试
- 错误处理测试
- 工具注册验证
- 配置加载测试

## 特性

- ✅ **简单集成**: 无需重构现有代码
- ✅ **配置驱动**: 通过YAML文件配置
- ✅ **异步支持**: 完全异步操作
- ✅ **错误处理**: 完善的错误处理机制
- ✅ **易于使用**: 提供多种使用方式
- ✅ **向后兼容**: 不影响现有功能

## 依赖要求

- Python 3.7+
- PyYAML
- 现有的旅行规划智能体模块
- 天气服务模块

## 注意事项

1. 确保所有依赖模块都在Python路径中
2. 配置文件路径正确
3. API密钥等环境变量已设置
4. 异步函数需要在异步上下文中运行

## 扩展

要添加新的工具或功能：

1. 在 `register.py` 中添加新的工具函数
2. 在 `travel_agent.yml` 中配置新工具
3. 在 `nemo_wrapper.py` 中添加便捷方法
4. 更新测试脚本

## 支持

如有问题或需要帮助，请检查：

1. 错误日志和异常信息
2. 配置文件格式
3. 依赖模块是否正确导入
4. 运行测试脚本进行诊断