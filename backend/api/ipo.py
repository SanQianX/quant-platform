# 新股/次新股API路由
"""
新股/次新股数据接口

提供新股日历、新股列表查询等功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Optional
import random

# 创建路由
router = APIRouter(prefix="/api/ipo", tags=["新股数据"])


# 模拟新股数据列表
IPO_LIST = [
    {"code": "688567", "name": "芯联集成", "date": "2025-03-06", "price": 6.30, "change_pct": 268.75, "market": "科创板", "industry": "半导体"},
    {"code": "688538", "name": "华羿汽车", "date": "2025-03-04", "price": 28.50, "change_pct": 753.12, "market": "科创板", "industry": "汽车零部件"},
    {"code": "301608", "name": "利尔化学", "date": "2025-03-03", "price": 15.80, "change_pct": 256.52, "market": "创业板", "industry": "农药兽药"},
    {"code": "688596", "name": "正帆科技", "date": "2025-03-03", "price": 22.40, "change_pct": 325.68, "market": "科创板", "industry": "专用设备"},
    {"code": "301598", "name": "博科测试", "date": "2025-02-28", "price": 35.60, "change_pct": 189.43, "market": "创业板", "industry": "检测服务"},
    {"code": "603121", "name": "华凌钢铁", "date": "2025-02-27", "price": 8.90, "change_pct": 145.23, "market": "主板", "industry": "钢铁行业"},
    {"code": "688599", "name": "天合光能", "date": "2025-02-26", "price": 18.75, "change_pct": 412.56, "market": "科创板", "industry": "光伏设备"},
    {"code": "301599", "name": "睿智创新", "date": "2025-02-25", "price": 42.30, "change_pct": 523.18, "market": "创业板", "industry": "软件开发"},
    {"code": "688601", "name": "索道智能", "date": "2025-02-24", "price": 16.85, "change_pct": 287.65, "market": "科创板", "industry": "人工智能"},
    {"code": "603125", "name": "龙源电力", "date": "2025-02-21", "price": 12.40, "change_pct": 156.78, "market": "主板", "industry": "电力行业"},
]

# 即将上市的新股（新股日历）
UPCOMING_IPO = [
    {"code": "688610", "name": "智源芯片", "expected_date": "2025-03-15", "price_range": "12.50-15.00", "market": "科创板", "industry": "半导体", "shares": 5000, "pe": 45.2},
    {"code": "301605", "name": "云原生科技", "expected_date": "2025-03-18", "price_range": "28.00-35.00", "market": "创业板", "industry": "云计算", "shares": 3000, "pe": 62.5},
    {"code": "688615", "name": "氢能动力", "expected_date": "2025-03-20", "price_range": "18.00-22.00", "market": "科创板", "industry": "新能源", "shares": 4500, "pe": 38.6},
    {"code": "603130", "name": "东鹏特饮", "expected_date": "2025-03-22", "price_range": "15.80-18.50", "market": "主板", "industry": "饮料制造", "shares": 6000, "pe": 28.4},
    {"code": "301612", "name": "数字政通", "expected_date": "2025-03-25", "price_range": "22.00-26.00", "market": "创业板", "industry": "智慧城市", "shares": 3500, "pe": 52.1},
]


@router.get("/calendar")
def get_ipo_calendar():
    """
    获取新股日历
    
    返回即将上市的新股信息
    
    Returns:
        dict: 统一响应格式，包含即将上市的新股列表
    """
    return {
        "code": 0,
        "message": "success",
        "data": UPCOMING_IPO
    }


@router.get("/list")
def get_ipo_list(limit: Optional[int] = 10):
    """
    获取新股列表
    
    返回最近上市的新股列表（支持分页）
    
    Args:
        limit: 返回数量限制，默认10条
        
    Returns:
        dict: 统一响应格式，包含新股列表
    """
    # 限制返回数量
    result = IPO_LIST[:limit] if limit else IPO_LIST
    
    return {
        "code": 0,
        "message": "success",
        "data": result,
        "total": len(IPO_LIST)
    }


@router.get("/{code}")
def get_ipo_detail(code: str):
    """
    获取新股详情
    
    获取指定新股代码的详细信息
    
    Args:
        code: 新股代码
        
    Returns:
        dict: 统一响应格式，包含新股详情
    """
    # 先在已上市列表中查找
    for ipo in IPO_LIST:
        if ipo["code"] == code:
            return {
                "code": 0,
                "message": "success",
                "data": ipo
            }
    
    # 再在即将上市列表中查找
    for ipo in UPCOMING_IPO:
        if ipo["code"] == code:
            return {
                "code": 0,
                "message": "success",
                "data": {**ipo, "status": "即将上市"}
            }
    
    raise HTTPException(status_code=404, detail=f"新股代码 {code} 不存在")
