from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import wallet
from .api.developer_core import router as developer_router
from .api.pay_gateway import router as pay_router
from .api.withdraw_gateway import admin_router as withdraw_admin_router
from .api.withdraw_gateway import router as withdraw_router
from .core.database import engine, Base
from .core.schema_upgrade import apply_schema_upgrades
from .core.settings import settings

# 创建数据库表
Base.metadata.create_all(bind=engine)
apply_schema_upgrades(engine)

app = FastAPI(
    title="PayForWechat - 支付管理平台",
    description="开发者支付管理平台API",
    version="1.0.0"
)

# 本地开发默认允许 localhost/127.0.0.1 任意端口，避免前端端口变化导致预检失败
local_origin_regex = r"https?://(localhost|127\.0\.0\.1)(:\d+)?$"

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=local_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API路由
app.include_router(developer_router, prefix="/api/developer", tags=["开发者"])
app.include_router(pay_router, prefix="/api/pay", tags=["支付"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["钱包"])
app.include_router(withdraw_router, prefix="/api/withdraw", tags=["提现"])

app.include_router(withdraw_admin_router, prefix="/api/admin/withdraw", tags=["管理员"])


@app.get("/")
async def root():
    return {
        "message": "PayForWechat API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
