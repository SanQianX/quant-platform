# Quant Platform Backend - FastAPI应用
"""
量化数据平台 API 服务

功能:
- 股票列表查询
- 股票搜索
- K线数据获取
- 数据导出 (CSV/JSON)
- 定时任务
- 缓存管理
- 监控指标

技术栈:
- FastAPI: Web框架
- SQLAlchemy: ORM
- AkShare/Tushare: 金融数据源
- APScheduler: 定时任务
- 缓存: 内存缓存
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.stock import router as stock_router
from api.stock_extra import router as stock_extra_router
from api.adj import router as adj_router
from api.health import router as health_router
from api.version import v1_router
from api.scheduler import router as scheduler_router
from api.cache import router as cache_router
from api.monitor import router as monitor_router
from api.auth import router as auth_router
from api.export import router as export_router
from api.users import router as users_router
from api.indicators import router as indicators_router
from api.signals import router as signals_router
from api.filter import router as filter_router
from api.data_quality import router as data_quality_router
from api.financial import router as financial_router
from api.quote import router as quote_router
from api.sentiment import router as sentiment_router
from api.portfolio import router as portfolio_router
from api.risk import router as risk_router
from api.market import router as market_router
from api.alert import router as alert_router
from api.trade import router as trade_router
from api.export_enhanced import router as export_enhanced_router
from api.chart import router as chart_router
from api.advanced_filter import router as advanced_filter_router
from api.settings import router as settings_router
from api.options import router as options_router
from api.flow import router as flow_router
from api.flow_history import router as flow_history_router
from api.toplist import router as toplist_router
from api.toplist_history import router as toplist_history_router
from api.etf import router as etf_router
from api.bond import router as bond_router
from api.ipo import router as ipo_router
from api.futures import router as futures_router
from api.hkstock import router as hkstock_router
from api.profile import router as profile_router
from api.industry import router as industry_router
from api.usstock import router as usstock_router
from api.margin import router as margin_router
from api.block_trade import router as block_trade_router
from api.holder_trade import router as holder_trade_router
from api.restricted_share import router as restricted_share_router
from api.broker import router as broker_router
from api.top_institution import router as top_institution_router
from api.dividend import router as dividend_router
from api.rights_issue import router as rights_issue_router
from api.suspension import router as suspension_router
from api.limit_price import router as limit_price_router
from api.order_book import router as order_book_router
from api.tick import router as tick_router
from api.queue import router as queue_router
from api.news_history import router as news_history_router
from api.announcements_history import router as announcements_history_router
from middleware.request_log import log_requests
from middleware.metrics_middleware import MetricsMiddleware
from middleware.error_handler import setup_error_handlers
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

# 添加请求日志中间件
app.middleware("http")(log_requests)

# 添加性能监控中间件
app.add_middleware(MetricsMiddleware)

# 设置错误处理器
setup_error_handlers(app)

# 注册路由
app.include_router(profile_router)
app.include_router(industry_router)
app.include_router(quote_router)
app.include_router(stock_router)
app.include_router(stock_extra_router)
app.include_router(adj_router)
app.include_router(health_router)
app.include_router(v1_router)
app.include_router(scheduler_router)
app.include_router(cache_router)
app.include_router(monitor_router)
app.include_router(auth_router)
app.include_router(export_router)
app.include_router(users_router)
app.include_router(indicators_router)
app.include_router(signals_router)
app.include_router(filter_router)
app.include_router(data_quality_router)
app.include_router(financial_router)
app.include_router(quote_router)
app.include_router(sentiment_router)
app.include_router(portfolio_router)
app.include_router(risk_router)
app.include_router(market_router)
app.include_router(alert_router)
app.include_router(trade_router)
app.include_router(export_enhanced_router)
app.include_router(chart_router)
app.include_router(advanced_filter_router)
app.include_router(settings_router)
app.include_router(options_router)
app.include_router(flow_router)
app.include_router(flow_history_router, prefix="/api/flow")
app.include_router(toplist_router)
app.include_router(toplist_history_router)
app.include_router(etf_router)
app.include_router(bond_router)
app.include_router(ipo_router)
app.include_router(futures_router)
app.include_router(hkstock_router)
app.include_router(usstock_router)
app.include_router(margin_router)
app.include_router(block_trade_router)
app.include_router(holder_trade_router)
app.include_router(restricted_share_router)
app.include_router(broker_router)
app.include_router(top_institution_router)
app.include_router(dividend_router)
app.include_router(rights_issue_router)
app.include_router(suspension_router)
app.include_router(limit_price_router)
app.include_router(order_book_router)
app.include_router(tick_router)
app.include_router(queue_router)
app.include_router(news_history_router)
app.include_router(announcements_history_router)

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
