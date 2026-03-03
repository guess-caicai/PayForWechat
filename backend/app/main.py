from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import developer, pay, wallet, withdraw
from .core.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PayForWechat - 支付管理平台",
    description="开发者支付管理平台API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API路由
app.include_router(developer.router, prefix="/api/developer", tags=["开发者"])
app.include_router(pay.router, prefix="/api/pay", tags=["支付"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["钱包"])
app.include_router(withdraw.router, prefix="/api/withdraw", tags=["提现"])

# 管理员路由（简化版）
app.include_router(withdraw.router, prefix="/admin/withdraw", tags=["管理员"])


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
