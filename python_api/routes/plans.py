"""旅行规划相关的API路由"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import uuid

from agents import TravelPlannerAgent
from agents.models import (
    TravelRequest, 
    TravelPlan, 
    PlanGenerationResponse,
    TravelStyle,
    BudgetLevel
)

router = APIRouter(prefix="/api/plans", tags=["旅行规划"])

# 存储活跃的规划任务（生产环境应使用数据库）
active_plans: Dict[str, Dict[str, Any]] = {}
plan_results: Dict[str, TravelPlan] = {}

@router.post("/create", response_model=PlanGenerationResponse)
async def create_travel_plan(request: TravelRequest):
    """创建旅行计划"""
    try:
        # 打印接收到的请求数据用于调试
        print(f"🔍 接收到的请求数据: {request.dict()}")
        print(f"📅 日期类型检查 - start_date: {type(request.start_date)}, end_date: {type(request.end_date)}")
        print(f"👥 参与人数: {request.group_size} (类型: {type(request.group_size)})")
        print(f"💰 预算等级: '{request.budget_level}' (类型: {type(request.budget_level)})")
        print(f"🎯 旅行风格: '{request.travel_style}' (类型: {type(request.travel_style)})")
        
        # 生成唯一的计划ID
        plan_id = str(uuid.uuid4())
        
        # 验证请求数据
        if not request.destination:
            raise HTTPException(status_code=400, detail="目的地不能为空")
        
        if not request.start_date or not request.end_date:
            raise HTTPException(status_code=400, detail="出发和返回日期不能为空")
        
        if request.start_date >= request.end_date:
            raise HTTPException(status_code=400, detail="返回日期必须晚于出发日期")
        
        if request.group_size <= 0:
            raise HTTPException(status_code=400, detail="参与人数必须大于0")
        
        # 创建智能体实例
        agent = TravelPlannerAgent()
        
        # 记录任务状态
        active_plans[plan_id] = {
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "request": request.dict(),
            "progress": 0
        }
        
        # 异步生成旅行计划
        asyncio.create_task(generate_plan_async(plan_id, request, agent))
        
        return PlanGenerationResponse(
            success=True,
            plan_id=plan_id,
            plan=None,
            message="旅行计划正在生成中，请稍后查询结果",
            processing_time=None,
            agent_steps=["信息收集", "开始生成"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建旅行计划失败: {str(e)}")

@router.post("/generate/{plan_id}")
async def generate_plan(plan_id: str):
    """触发指定计划的行程生成"""
    try:
        # 检查计划是否存在
        if plan_id not in active_plans:
            raise HTTPException(status_code=404, detail="计划不存在")
        
        plan_info = active_plans[plan_id]
        
        # 检查计划状态
        if plan_info["status"] == "processing":
            return {
                "success": True,
                "message": "计划已在生成中",
                "plan_id": plan_id,
                "status": "processing"
            }
        
        if plan_id in plan_results:
            return {
                "success": True,
                "message": "计划已生成完成",
                "plan_id": plan_id,
                "status": "completed"
            }
        
        # 获取原始请求数据
        request_data = plan_info["request"]
        request = TravelRequest(**request_data)
        
        # 创建智能体实例
        agent = TravelPlannerAgent()
        
        # 重置计划状态为处理中
        active_plans[plan_id]["status"] = "processing"
        active_plans[plan_id]["progress"] = 0
        active_plans[plan_id]["message"] = "开始生成行程..."
        
        # 异步生成旅行计划
        asyncio.create_task(generate_plan_async(plan_id, request, agent))
        
        return {
            "success": True,
            "message": "行程生成已启动",
            "plan_id": plan_id,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动行程生成失败: {str(e)}")

@router.get("/status/{plan_id}")
async def get_plan_status(plan_id: str):
    """获取计划生成状态"""
    if plan_id not in active_plans:
        raise HTTPException(status_code=404, detail="计划不存在")
    
    plan_info = active_plans[plan_id]
    
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

@router.get("/result/{plan_id}")
async def get_plan_result(plan_id: str):
    """获取完整的旅行计划结果"""
    if plan_id not in plan_results:
        if plan_id in active_plans:
            raise HTTPException(status_code=202, detail="计划仍在生成中，请稍后再试")
        else:
            raise HTTPException(status_code=404, detail="计划不存在")
    
    plan = plan_results[plan_id]
    
    # 如果是TravelPlan对象，转换为字典
    if hasattr(plan, 'dict'):
        return plan.dict()
    # 如果已经是字典，直接返回
    elif isinstance(plan, dict):
        return plan
    else:
        # 兜底处理，尝试转换为字典
        try:
            return plan.__dict__
        except:
            return {"error": "无法序列化计划数据"}
    
    return plan

@router.post("/optimize/{plan_id}")
async def optimize_plan(plan_id: str, optimization_request: Dict[str, Any]):
    """优化现有旅行计划"""
    if plan_id not in plan_results:
        raise HTTPException(status_code=404, detail="计划不存在或尚未完成")
    
    try:
        # 获取原始计划
        original_plan = plan_results[plan_id]
        
        # 创建智能体实例
        agent = TravelPlannerAgent()
        
        # 执行优化（这里可以根据optimization_request的内容进行不同的优化）
        optimization_type = optimization_request.get("type", "budget")
        
        if optimization_type == "budget":
            # 预算优化
            new_budget = optimization_request.get("budget_level")
            if new_budget:
                # 重新生成计划（简化版，实际可以只优化特定部分）
                original_request = TravelRequest(**active_plans[plan_id]["request"])
                original_request.budget_level = new_budget
                
                optimized_plan = await agent.generate_travel_plan(original_request)
                plan_results[plan_id] = optimized_plan
                
                return {
                    "message": "预算优化完成",
                    "optimized_plan": optimized_plan.dict()
                }
        
        elif optimization_type == "style":
            # 旅行风格优化
            new_styles = optimization_request.get("travel_styles", [])
            if new_styles:
                original_request = TravelRequest(**active_plans[plan_id]["request"])
                original_request.travel_style = new_styles[0] if new_styles else original_request.travel_style
                
                optimized_plan = await agent.generate_travel_plan(original_request)
                plan_results[plan_id] = optimized_plan
                
                return {
                    "message": "旅行风格优化完成",
                    "optimized_plan": optimized_plan.dict()
                }
        
        return {"message": "优化类型不支持"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")

@router.post("/collaborate/{plan_id}")
async def collaborate_plan(plan_id: str, collaboration_request: Dict[str, Any]):
    """处理多人旅行协作"""
    try:
        # 获取用户ID、状态和反馈
        user_id = collaboration_request.get("userId")
        status = collaboration_request.get("status")
        feedback = collaboration_request.get("feedback", "")
        
        if not user_id or not status:
            raise HTTPException(status_code=400, detail="缺少必要参数: userId 和 status")
        
        # 验证状态值
        valid_statuses = ["pending", "confirmed", "declined", "maybe"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"无效的状态值，必须是: {valid_statuses}")
        
        # 模拟存储参与者状态（实际项目中应该存储到数据库）
        # 这里简单返回成功响应
        return {
            "success": True,
            "message": "参与者状态更新成功",
            "data": {
                "planId": plan_id,
                "userId": user_id,
                "status": status,
                "feedback": feedback,
                "updatedAt": "2024-01-20T10:00:00Z"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"协作处理失败: {str(e)}")

@router.put("/update/{plan_id}")
async def update_plan(plan_id: str, update_request: Dict[str, Any]):
    """更新旅行计划"""
    try:
        # 检查计划是否存在
        plan_exists = plan_id in plan_results or plan_id in active_plans
        if not plan_exists:
            raise HTTPException(status_code=404, detail="计划不存在")
        
        # 获取当前计划数据
        current_plan = None
        if plan_id in plan_results:
            current_plan = plan_results[plan_id]
        elif plan_id in active_plans:
            # 如果计划还在处理中，不允许更新
            if active_plans[plan_id]["status"] == "processing":
                raise HTTPException(status_code=400, detail="计划正在生成中，无法更新")
        
        # 从details字段中提取更新数据
        details = update_request.get("details", {})
        updated_fields = []
        
        # 更新目的地
        if "destination" in details:
            if current_plan:
                if isinstance(current_plan, dict):
                    current_plan["destination"] = details["destination"]
                else:
                    current_plan.destination = details["destination"]
            if plan_id in active_plans:
                active_plans[plan_id]["request"]["destination"] = details["destination"]
            updated_fields.append("destination")
        
        # 更新日期
        if "startDate" in details:
            if current_plan:
                if isinstance(current_plan, dict):
                    current_plan["start_date"] = details["startDate"]
                else:
                    current_plan.start_date = details["startDate"]
            if plan_id in active_plans:
                active_plans[plan_id]["request"]["start_date"] = details["startDate"]
            updated_fields.append("startDate")
        
        if "endDate" in details:
            if current_plan:
                if isinstance(current_plan, dict):
                    current_plan["end_date"] = details["endDate"]
                else:
                    current_plan.end_date = details["endDate"]
            if plan_id in active_plans:
                active_plans[plan_id]["request"]["end_date"] = details["endDate"]
            updated_fields.append("endDate")
        
        # 更新参与人数
        if "participants" in details:
            if current_plan:
                if isinstance(current_plan, dict):
                    current_plan["group_size"] = details["participants"]
                else:
                    current_plan.group_size = details["participants"]
            if plan_id in active_plans:
                active_plans[plan_id]["request"]["group_size"] = details["participants"]
            updated_fields.append("participants")
        
        # 更新预算等级
        if "budget" in details:
            if current_plan:
                if isinstance(current_plan, dict):
                    current_plan["budget_level"] = details["budget"]
                else:
                    current_plan.budget_level = details["budget"]
            if plan_id in active_plans:
                active_plans[plan_id]["request"]["budget_level"] = details["budget"]
            updated_fields.append("budget")
        
        # 更新旅行风格
        if "travelStyle" in details:
            if current_plan:
                if isinstance(current_plan, dict):
                    current_plan["travel_style"] = details["travelStyle"]
                else:
                    current_plan.travel_style = details["travelStyle"]
            if plan_id in active_plans:
                active_plans[plan_id]["request"]["travel_style"] = details["travelStyle"]
            updated_fields.append("travelStyle")
        
        # 更新兴趣偏好
        if "interests" in details:
            if current_plan:
                if isinstance(current_plan, dict):
                    current_plan["interests"] = details["interests"]
                else:
                    current_plan.interests = details["interests"]
            if plan_id in active_plans:
                active_plans[plan_id]["request"]["interests"] = details["interests"]
            updated_fields.append("interests")
        
        # 更新特殊要求
        if "specialRequests" in details:
            if current_plan:
                if isinstance(current_plan, dict):
                    current_plan["special_requests"] = details["specialRequests"]
                else:
                    # 如果计划对象有special_requests属性，则更新
                    if hasattr(current_plan, 'special_requests'):
                        current_plan.special_requests = details["specialRequests"]
            if plan_id in active_plans:
                active_plans[plan_id]["request"]["special_requests"] = details["specialRequests"]
            updated_fields.append("specialRequests")
        
        # 更新修改时间
        if current_plan:
            if isinstance(current_plan, dict):
                current_plan["updated_at"] = datetime.now().isoformat()
            else:
                current_plan.updated_at = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "计划更新成功",
            "plan_id": plan_id,
            "updated_fields": updated_fields,
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新计划失败: {str(e)}")

@router.delete("/delete/{plan_id}")
async def delete_plan(plan_id: str):
    """删除旅行计划"""
    deleted = False
    
    if plan_id in active_plans:
        del active_plans[plan_id]
        deleted = True
    
    if plan_id in plan_results:
        del plan_results[plan_id]
        deleted = True
    
    if not deleted:
        raise HTTPException(status_code=404, detail="计划不存在")
    
    return {"message": "计划已删除"}

@router.get("/list")
async def list_plans():
    """获取所有计划列表"""
    active_plans_list = []
    completed_plans_list = []
    
    # 活跃的计划
    for plan_id, plan_info in active_plans.items():
        plan_data = {
            "plan_id": plan_id,
            "status": plan_info["status"],
            "created_at": plan_info["created_at"],
            "destination": plan_info["request"].get("destination"),
            "start_date": plan_info["request"].get("start_date"),
            "end_date": plan_info["request"].get("end_date"),
            "participants": plan_info["request"].get("group_size"),
            "budget": plan_info["request"].get("budget_level"),
            "travel_style": plan_info["request"].get("travel_style"),
            "interests": plan_info["request"].get("interests", []),
            "progress": plan_info.get("progress", 0)
        }
        
        if plan_info["status"] == "completed":
            completed_plans_list.append(plan_data)
        else:
            active_plans_list.append(plan_data)
    
    # 完成的计划
    for plan_id, plan in plan_results.items():
        if plan_id not in active_plans:  # 避免重复
            # 处理字典和对象两种情况
            if isinstance(plan, dict):
                # 如果是字典格式（从NeMo API返回）
                plan_data = {
                    "plan_id": plan_id,
                    "status": "completed",
                    "created_at": plan.get('created_at', datetime.now().isoformat()),
                    "updated_at": plan.get('updated_at', plan.get('created_at', datetime.now().isoformat())),
                    "destination": plan.get('destination'),
                    "start_date": plan.get('start_date'),
                    "end_date": plan.get('end_date'),
                    "participants": plan.get('group_size'),
                    "budget": plan.get('budget_level'),
                    "travel_style": plan.get('travel_style'),
                    "interests": plan.get('interests', []),
                    "progress": 100,
                    "itinerary": plan.get('itinerary')
                }
            else:
                # 如果是TravelPlan对象
                plan_data = {
                    "plan_id": plan_id,
                    "status": "completed",
                    "created_at": getattr(plan, 'created_at', datetime.now().isoformat()),
                    "updated_at": getattr(plan, 'updated_at', getattr(plan, 'created_at', datetime.now().isoformat())),
                    "destination": plan.destination,
                    "start_date": plan.start_date.isoformat() if hasattr(plan.start_date, 'isoformat') else str(plan.start_date),
                    "end_date": plan.end_date.isoformat() if hasattr(plan.end_date, 'isoformat') else str(plan.end_date),
                    "participants": plan.group_size,
                    "budget": getattr(plan, 'budget_level', None),
                    "travel_style": getattr(plan, 'travel_style', None),
                    "interests": getattr(plan, 'interests', []),
                    "progress": 100,
                    "itinerary": getattr(plan, 'itinerary', None)
                }
            completed_plans_list.append(plan_data)
    
    return {
        "active_plans": active_plans_list,
        "completed_plans": completed_plans_list
    }

async def generate_plan_async(plan_id: str, request: TravelRequest, agent: TravelPlannerAgent):
    """异步生成旅行计划"""
    try:
        # 更新进度
        active_plans[plan_id]["progress"] = 10
        active_plans[plan_id]["message"] = "开始分析旅行需求..."
        
        # 生成旅行计划
        result = await agent.generate_travel_plan(request)
        
        # 检查生成结果
        if result.get("success") and result.get("plan"):
            # 存储成功生成的计划
            plan_results[plan_id] = result["plan"]
            
            # 更新进度
            active_plans[plan_id]["progress"] = 100
            active_plans[plan_id]["status"] = "completed"
            active_plans[plan_id]["message"] = "旅行计划生成完成"
        else:
            # 生成失败
            active_plans[plan_id]["status"] = "failed"
            active_plans[plan_id]["message"] = result.get("message", "生成失败")
            print(f"❌ 计划生成失败: {result.get('message')}")
        
    except Exception as e:
        # 错误处理
        active_plans[plan_id]["status"] = "failed"
        active_plans[plan_id]["message"] = f"生成失败: {str(e)}"
        active_plans[plan_id]["error"] = str(e)

# 健康检查端点
@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "travel_planner",
        "timestamp": datetime.now().isoformat(),
        "active_plans": len(active_plans),
        "completed_plans": len(plan_results)
    }