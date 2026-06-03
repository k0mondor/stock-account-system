from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.config import settings
from app.db.session import Base, engine
from app.routers import application, base_data, health
from app.routers.association import router as association_router
from app.routers.fund_account import router as fund_account_router
from app.routers.operation_log import router as operation_log_router
from app.routers.status_check import router as status_check_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Stock Account Business Subsystem",
    description="证券账户与资金账户业务子系统后端服务",
    version="0.2.0",
)


@app.get("/", include_in_schema=False)
def root():
    """根路径重定向到 /docs"""
    return RedirectResponse(url="/docs")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "code": "INTERNAL_ERROR",
            "message": "内部服务器错误",
            "data": None,
            "request_id": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(base_data.router, prefix=settings.api_prefix, tags=["base-data"])
app.include_router(application.router, prefix=settings.api_prefix, tags=["applications"])
app.include_router(fund_account_router, prefix=f"{settings.api_prefix}/fund-accounts", tags=["fund-account"])
app.include_router(association_router, prefix=f"{settings.api_prefix}/associations", tags=["associations"])
app.include_router(operation_log_router, prefix=f"{settings.api_prefix}/operation-logs", tags=["operation-logs"])
app.include_router(status_check_router, prefix=f"{settings.api_prefix}/status", tags=["status-check"])
