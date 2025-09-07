#!/usr/bin/env python3
"""
FastAPI 主应用文件
替换原有的 Express.js 后端
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

# 导入路由
from routes.auth import router as auth_router
from routes import plans

# 加载环境变量
load_dotenv()

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Let's Go API",
    description="AI 旅行规划应用后端 API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(plans.router)

# 健康检查接口
@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "success": True,
        "message": "ok"
    }

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Server internal error"
        }
    )

# 404 处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404 处理器"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "API not found"
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )