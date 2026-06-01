"""FastAPI应用入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.routers import api_router
from app.models import (
    InvestorUser,
    OperationLog,
    FundAccount,
    FundFreeze,
    FundSettlement,
    SecurityAccount,
    SecurityPosition,
    PositionFreeze,
    PositionSettlement,
    AccountAssociation,
    AccountApplication,
    ApprovalHistory,
)

# 创建所有表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_TITLE,
    description="股票交易系统 - 账户业务子系统（ACCOUNT）API",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": settings.SERVICE_NAME}


@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "欢迎使用股票交易系统 - 账户业务子系统",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
