# Quant Platform Backend - FastAPI应用
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.stock import router as stock_router
import init_data

# 创建应用
app = FastAPI(
    title="量化数据平台API",
    description="股票数据查询服务",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stock_router)

# 启动时初始化数据
@app.on_event("startup")
def startup_event():
    print("初始化股票数据...")
    init_data.init_stocks()
    print("初始化完成!")

@app.get("/")
def root():
    return {"message": "量化数据平台API", "version": "0.1.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
