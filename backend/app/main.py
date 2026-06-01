from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import Base, engine
from app.routers import application, base_data, health

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Stock Account Business Subsystem",
    description="证券账户与资金账户业务子系统后端服务",
    version="0.1.0",
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
