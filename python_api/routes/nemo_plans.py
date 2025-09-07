"""NeMo Agent Toolkit 集成的旅行规划API路由"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import uuid

from agents.models import (
    TravelRequest, 
    TravelPlan, 
    PlanGenerationResponse,
    TravelStyle,
    BudgetLevel
)
from nat_configs.nemo_wrapper import NeMoTravelAgent, quick_plan_trip
# 导入普通计划的存储变量，实现统一存储
from .plans import active_plans, plan_results

router = APIRouter(prefix="/api/nemo-plans", tags=["NeMo旅行规划"])

# 存储活跃的NeMo规划任务（生产环境应使用数据库）
active_nemo_plans: Dict[str, Dict[str, Any]] = {}

async def generate_nemo_plan_async(plan_id: str, request: TravelRequest, agent: NeMoTravelAgent):
    """异步生成NeMo旅行计划"""
    try:
        # 更新NeMo任务状态
        active_nemo_plans[plan_id]["status"] = "processing"
        active_nemo_plans[plan_id]["progress"] = 10
        active_nemo_plans[plan_id]["message"] = "正在使用NeMo Agent生成旅行计划..."
        
        # 同时更新统一的计划状态
        if plan_id in active_plans:
            active_plans[plan_id]["status"] = "processing"
            active_plans[plan_id]["progress"] = 10
            active_plans[plan_id]["message"] = "正在使用NeMo Agent生成旅行计划..."
        
        # 使用NeMo Agent生成计划
        plan = await agent.plan_trip(
            destination=request.destination,
            start_date=request.start_date.strftime("%Y-%m-%d"),
            end_date=request.end_date.strftime("%Y-%m-%d"),
            preferences=request.preferences
        )
        
        # 更新进度
        active_nemo_plans[plan_id]["progress"] = 100
        active_nemo_plans[plan_id]["status"] = "completed"
        active_nemo_plans[plan_id]["message"] = "NeMo旅行计划生成完成"
        
        # 同时更新统一的计划状态
        if plan_id in active_plans:
            active_plans[plan_id]["progress"] = 100
            active_plans[plan_id]["status"] = "completed"
            active_plans[plan_id]["message"] = "NeMo旅行计划生成完成"
        
        # 存储结果到统一的plan_results中
        plan_results[plan_id] = plan
        
    except Exception as e:
        active_nemo_plans[plan_id]["status"] = "error"
        active_nemo_plans[plan_id]["message"] = f"生成失败: {str(e)}"
        # 同时更新统一的计划状态
        if plan_id in active_plans:
            active_plans[plan_id]["status"] = "error"
            active_plans[plan_id]["message"] = f"生成失败: {str(e)}"
        print(f"NeMo计划生成错误: {e}")

@router.post("/create", response_model=PlanGenerationResponse)
async def create_nemo_travel_plan(request: TravelRequest):
    """使用NeMo Agent创建旅行计划"""
    try:
        # 打印接收到的请求数据用于调试
        print(f"🔍 NeMo接收到的请求数据: {request.dict()}")
        
        # 生成唯一的计划ID
        plan_id = str(uuid.uuid4())
        
        # 验证请求数据
        if not request.destination:
            raise HTTPException(status_code=400, detail="目的地不能为空")
        
        if not request.start_date or not request.end_date:
            raise HTTPException(status_code=400, detail="出发和返回日期不能为空")
        
        if request.start_date >= request.end_date:
            raise HTTPException(status_code=400, detail="返回日期必须晚于出发日期")
        
        # 创建NeMo智能体实例
        agent = NeMoTravelAgent()
        
        # 记录任务状态
        active_nemo_plans[plan_id] = {
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "request": request.dict(),
            "progress": 0
        }
        
        # 异步生成旅行计划
        asyncio.create_task(generate_nemo_plan_async(plan_id, request, agent))
        
        return PlanGenerationResponse(
            success=True,
            plan_id=plan_id,
            plan=None,
            message="NeMo旅行计划正在生成中，请稍后查询结果",
            processing_time=None,
            agent_steps=["NeMo Agent初始化", "开始生成"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建NeMo旅行计划失败: {str(e)}")

@router.get("/status/{plan_id}")
async def get_nemo_plan_status(plan_id: str):
    """获取NeMo计划生成状态"""
    if plan_id not in active_nemo_plans:
        raise HTTPException(status_code=404, detail="计划不存在")
    
    plan_info = active_nemo_plans[plan_id]
    
    # 检查是否已完成
    if plan_id in plan_results:
        return {
            "plan_id": plan_id,
            "status": "completed",
            "progress": 100,
            "result": plan_results[plan_id].dict()
        }
    
    return {
        "plan_id": plan_id,
        "status": plan_info["status"],
        "progress": plan_info.get("progress", 0),
        "message": plan_info.get("message", "处理中...")
    }

@router.get("/result/{plan_id}", response_model=TravelPlan)
async def get_nemo_plan_result(plan_id: str):
    """获取NeMo旅行计划结果（从统一的plan_results中获取）"""
    if plan_id not in plan_results:
        if plan_id in active_nemo_plans:
            raise HTTPException(status_code=202, detail="计划仍在生成中，请稍后再试")
        else:
            raise HTTPException(status_code=404, detail="计划不存在")
    
    return plan_results[plan_id]

@router.post("/quick-plan")
async def nemo_quick_plan(request: Dict[str, Any]):
    """NeMo快速规划接口"""
    try:
        destination = request.get("destination")
        start_date = request.get("startDate") or request.get("start_date")
        end_date = request.get("endDate") or request.get("end_date")
        preferences = request.get("preferences", "")
        
        if not destination:
            raise HTTPException(status_code=400, detail="目的地不能为空")
        
        if not start_date or not end_date:
            raise HTTPException(status_code=400, detail="日期不能为空")
        
        # 生成计划ID（与普通计划保持一致的格式）
        plan_id = f"plan_{int(datetime.now().timestamp() * 1000)}"
        
        # 使用快速规划函数
        result = await quick_plan_trip(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            preferences=preferences
        )
        
        # 调试：打印result内容
        print(f"🔍 quick_plan_trip返回结果: {result}")
        
        # 检查结果并提取TravelPlan对象
        if not result.get("success"):
            error_msg = result.get('error', result.get('message', '未知错误'))
            print(f"❌ 计划生成失败，错误信息: {error_msg}")
            raise HTTPException(status_code=500, detail=f"计划生成失败: {error_msg}")
        
        if not result.get("plan"):
            raise HTTPException(status_code=500, detail="计划生成失败: 未返回计划数据")
        
        # 存储TravelPlan对象到统一的plan_results中
        plan_results[plan_id] = result["plan"]
        
        # 返回的result也需要是TravelPlan对象
        travel_plan = result["plan"]
        
        return {
            "success": True,
            "plan_id": plan_id,
            "result": travel_plan.dict() if hasattr(travel_plan, 'dict') else travel_plan,
            "message": "NeMo快速规划完成"
        }
        
    except Exception as e:
        import traceback
        error_detail = str(e)
        error_traceback = traceback.format_exc()
        print(f"❌ NeMo快速规划异常: {error_detail}")
        print(f"📍 错误堆栈: {error_traceback}")
        raise HTTPException(status_code=500, detail=f"NeMo快速规划失败: {error_detail}")