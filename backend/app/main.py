import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.request_context import (
    get_request_id,
    new_request_id,
    reset_request_id,
    set_request_id,
)
from app.db.migrations import apply_lightweight_migrations
from app.db.session import Base, engine
from app.routers import application, base_data, health
from app.routers.auth import router as auth_router
from app.routers.association import router as association_router
from app.routers.fund_account import router as fund_account_router
from app.routers.joint_account import router as joint_account_router
from app.routers.operation_log import router as operation_log_router
from app.routers.security_account import router as security_account_router
from app.routers.status_check import router as status_check_router
from app.schemas.common import ApiResponse


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    del application
    Base.metadata.create_all(bind=engine)
    apply_lightweight_migrations(engine)
    yield

app = FastAPI(
    title="Stock Account Business Subsystem",
    description="证券账户与资金账户业务子系统后端服务",
    version="0.2.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = new_request_id(request.headers.get("X-Request-Id"))
    token = set_request_id(request_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response
    finally:
        reset_request_id(token)


@app.get("/", include_in_schema=False)
def root():
    """根路径重定向到 /docs"""
    return RedirectResponse(url="/docs")


def _error_response(status_code: int, code: str, message: str, headers=None):
    payload = ApiResponse.error(code=code, message=message)
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json"),
        headers=headers,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    del request
    message = exc.detail if isinstance(exc.detail, str) else "请求处理失败"
    return _error_response(
        status_code=exc.status_code,
        code=f"HTTP_{exc.status_code}",
        message=message,
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    del request, exc
    return _error_response(
        status_code=422,
        code="VALIDATION_ERROR",
        message="请求参数校验失败",
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled request error: method=%s path=%s request_id=%s",
        request.method,
        request.url.path,
        get_request_id(),
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return _error_response(
        status_code=500,
        code="INTERNAL_ERROR",
        message="内部服务器错误",
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
app.include_router(auth_router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
app.include_router(fund_account_router, prefix=f"{settings.api_prefix}/fund-accounts", tags=["fund-account"])
app.include_router(security_account_router, prefix=f"{settings.api_prefix}/security-accounts", tags=["security-account"])
app.include_router(association_router, prefix=f"{settings.api_prefix}/associations", tags=["associations"])
app.include_router(joint_account_router, prefix=f"{settings.api_prefix}/joint-accounts", tags=["joint-accounts"])
app.include_router(operation_log_router, prefix=f"{settings.api_prefix}/operation-logs", tags=["operation-logs"])
app.include_router(status_check_router, prefix=f"{settings.api_prefix}/status", tags=["status-check"])
