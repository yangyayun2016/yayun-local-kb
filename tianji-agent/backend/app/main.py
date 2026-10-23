"""
天机智能体 (TianJi AI Agent) - 主应用入口
跨境电商 AI 智能体平台
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from core.config import settings
from routers import auth, chat, skills, knowledge_base, agents, points, connectors, schedules, projects
from services.database import init_db
from services.scheduler_service import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    await init_db()
    await start_scheduler()
    print("🚀 天机智能体服务启动成功!")
    yield
    # 关闭时
    await stop_scheduler()
    print("👋 天机智能体服务已关闭")


app = FastAPI(
    title="天机智能体 API",
    description="跨境电商 AI 智能体平台",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["智能对话"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["技能中心"])
app.include_router(knowledge_base.router, prefix="/api/v1/knowledge", tags=["知识库"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["智能体编排"])
app.include_router(points.router, prefix="/api/v1/points", tags=["积分系统"])
app.include_router(connectors.router, prefix="/api/v1/connectors", tags=["连接器"])
app.include_router(schedules.router, prefix="/api/v1/schedules", tags=["定时任务"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["项目管理"])


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "name": "天机智能体 TianJi AI Agent"
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "天机智能体 API 服务运行中",
        "docs": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
