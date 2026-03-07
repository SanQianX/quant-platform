# 配置常量
"""
配置常量模块
包含所有可配置的参数
"""

import os
import re

# 环境配置
ENV = os.getenv("ENV", "development")

# 数据库配置
DATABASE_CONFIG = {
    "development": {
        "type": "sqlite",
        "path": "data/quant.db"
    },
    "production": {
        "type": "postgresql",
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "user": os.getenv("DB_USER", "quant_user"),
        "password": os.getenv("DB_PASSWORD", "quant_pass"),
        "database": os.getenv("DB_NAME", "quant_platform")
    }
}

# API配置
API_CONFIG = {
    "title": "量化数据平台API",
    "version": "0.1.0",
    "description": "股票数据查询服务",
    "cors_origins": ["*"]
}

# 数据源配置
AKSHARE_CONFIG = {
    "start_date": "20240101",
    "adjust": "qfq"  # 前复权
}

# 模拟数据配置（网络不可用时使用）
MOCK_DATA_CONFIG = {
    "enabled": True,
    "days": 90  # 生成90天数据
}

# 股票列表配置
STOCK_LIST = [
    # 热门股票
    {"code": "000001", "name": "平安银行", "market": "sz", "stock_type": "stock"},
    {"code": "600519", "name": "贵州茅台", "market": "sh", "stock_type": "stock"},
    {"code": "300750", "name": "宁德时代", "market": "sz", "stock_type": "stock"},
    {"code": "600036", "name": "招商银行", "market": "sh", "stock_type": "stock"},
    {"code": "601318", "name": "中国平安", "market": "sh", "stock_type": "stock"},
    {"code": "000858", "name": "五粮液", "market": "sz", "stock_type": "stock"},
    {"code": "002594", "name": "比亚迪", "market": "sz", "stock_type": "stock"},
    {"code": "600900", "name": "长江电力", "market": "sh", "stock_type": "stock"},
    {"code": "601888", "name": "中国中免", "market": "sh", "stock_type": "stock"},
    {"code": "300059", "name": "东方财富", "market": "sz", "stock_type": "stock"},
    # 三大指数
    {"code": "000001_sh", "name": "上证指数", "market": "sh", "stock_type": "index"},
    {"code": "399001", "name": "深证成指", "market": "sz", "stock_type": "index"},
    {"code": "399006", "name": "创业板指", "market": "sz", "stock_type": "index"},
]

# 股票代码验证正则
STOCK_CODE_REGEX = re.compile(r"^\d{6}(_sh)?$")

# 性能配置
PERFORMANCE_CONFIG = {
    "cache_enabled": True,
    "cache_ttl": 300,  # 缓存5分钟
    "max_results": 500,  # 最大返回结果数
    "request_timeout": 30,  # 请求超时秒数
}

# 分页配置
PAGINATION_CONFIG = {
    "default_page_size": 100,
    "max_page_size": 1000,
}

# 基础价格映射（模拟数据用）
BASE_PRICES = {
    "600519": 1800,  # 茅台
    "000001": 12,    # 平安银行
    "300750": 200,   # 宁德时代
    "600036": 35,    # 招商银行
    "601318": 45,    # 中国平安
    "000858": 150,   # 五粮液
    "002594": 250,   # 比亚迪
    "600900": 22,    # 长江电力
    "601888": 70,    # 中国中免
    "300059": 20,    # 东方财富
    "000001_sh": 3200,  # 上证指数
    "399001": 11000,    # 深证成指
    "399006": 2200,     # 创业板指
}
