"""API路由汇总"""

from fastapi import APIRouter
from app.api.v1 import auth, fund, security, association, application

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(fund.router)
api_router.include_router(security.router)
api_router.include_router(association.router)
api_router.include_router(application.router)

__all__ = ["api_router"]
