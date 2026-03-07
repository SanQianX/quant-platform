# Quant Platform Backend - FastAPI应用
"""
量化数据平台 API 服务

功能:
- 股票列表查询
- 股票搜索
- K线数据获取
- 数据导出 (CSV/JSON)

技术栈:
- FastAPI: Web框架
- SQLAlchemy: ORM
- AkShare: 金融数据源
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.stock import router as stock_router
from api.stock_extra import router as stock_extra_router
from config import API_CONFIG, ENV
import init_data

# 创建FastAPI应用
app = FastAPI(
    title=API_CONFIG["title"],
    description=API_CONFIG["description"],
    version=API_CONFIG["version"]
)

# 配置CORS跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=API_CONFIG["cors_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stock_router)
app.include_router(stock_extra_router)

# 启动事件
@app.on_event("startup")
def startup_event():
    """应用启动时初始化数据"""
    print(f"正在启动 {API_CONFIG['title']} ...")
    print(f"当前环境: {ENV}")
    
    try:
        init_data.init_stocks()
        print("数据初始化完成!")
    except Exception as e:
        print(f"数据初始化失败: {e}")

# 根路由
@app.get("/")
def root():
    """根路径"""
    return {
        "message": API_CONFIG["title"],
        "version": API_CONFIG["version"],
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
def health():
    """健康检查"""
    return {
        "status": "ok",
        "environment": ENV
    }

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "code": -1,
            "message": f"服务器内部错误: {str(exc)}",
            "data": None
        }
    )
