# 资金流向API路由
"""
资金流向数据接口

提供主力资金流向、单日资金流向等功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import random
from models.response import success_response
from utils.logger import logger

# 创建路由
router = APIRouter(prefix="/api/flow", tags=["资金流向"])


def generate_mock_main_flow(code: str) -> dict:
    """生成模拟的主力资金流向数据"""
    # 生成基准值
    base_flow = random.uniform(-10000, 10000)  # 万元
    net_inflow = base_flow * random.uniform(0.8, 1.2)
    
    # 计算主力资金各分类
    super_net = net_inflow * random.uniform(0.4, 0.6)  # 超大单
    large_net = net_inflow * random.uniform(0.2, 0.3)  # 大单
    medium_net = net_inflow * random.uniform(0.1, 0.2)  # 中单
    small_net = net_inflow - super_net - large_net - medium_net  # 小单
    
    return {
        "code": code,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "net_inflow": round(net_inflow, 2),  # 主力净流入(万元)
        "net_inflow_rate": round(net_inflow / 10000, 4),  # 净流入率
        "super_large": {
            "net_inflow": round(super_net, 2),
            "buy": round(super_net * random.uniform(1.2, 1.5), 2),
            "sell": round(super_net * random.uniform(0.5, 0.8), 2),
            "net_rate": round(super_net / 10000, 4)
        },
        "large": {
            "net_inflow": round(large_net, 2),
            "buy": round(large_net * random.uniform(1.2, 1.5), 2),
            "sell": round(large_net * random.uniform(0.5, 0.8), 2),
            "net_rate": round(large_net / 10000, 4)
        },
        "medium": {
            "net_inflow": round(medium_net, 2),
            "buy": round(medium_net * random.uniform(1.2, 1.5), 2),
            "sell": round(medium_net * random.uniform(0.5, 0.8), 2),
            "net_rate": round(medium_net / 10000, 4)
        },
        "small": {
            "net_inflow": round(small_net, 2),
            "buy": round(abs(small_net) * random.uniform(1.2, 1.5), 2),
            "sell": round(abs(small_net) * random.uniform(0.5, 0.8), 2),
            "net_rate": round(small_net / 10000, 4)
        },
        "main_force_action": "买入" if net_inflow > 0 else "卖出",
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def generate_mock_daily_flow(code: str, days: int = 5) -> dict:
    """生成模拟的单日资金流向数据"""
    daily_data = []
    today = datetime.now()
    
    for i in range(days):
        date = (today - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        
        # 每日资金流向
        main_inflow = random.uniform(-8000, 12000)
        retail_inflow = random.uniform(-5000, 8000)
        
        # 生成每10分钟的流向数据
        minute_data = []
        for minute in range(0, 240, 10):  # 每10分钟一个点
            hour = 9 + minute // 60
            minute_in_main = main_inflow / 24 * random.uniform(0.8, 1.2)
            minute_in_retail = retail_inflow / 24 * random.uniform(0.8, 1.2)
            minute_data.append({
                "time": f"{hour:02d}:{(minute % 60):02d}:00",
                "main_inflow": round(minute_in_main, 2),
                "retail_inflow": round(minute_in_retail, 2)
            })
        
        daily_data.append({
            "date": date,
            "main_net_inflow": round(main_inflow, 2),
            "retail_net_inflow": round(retail_inflow, 2),
            "total_net_inflow": round(main_inflow + retail_inflow, 2),
            "main_inflow_rate": round(main_inflow / 10000, 4),
            "retail_inflow_rate": round(retail_inflow / 10000, 4),
            "minute_data": minute_data[:20]  # 限制返回点数
        })
    
    return {
        "code": code,
        "days": days,
        "data": daily_data,
        "summary": {
            "total_main_inflow": round(sum(d["main_net_inflow"] for d in daily_data), 2),
            "total_retail_inflow": round(sum(d["retail_net_inflow"] for d in daily_data), 2),
            "avg_main_inflow": round(sum(d["main_net_inflow"] for d in daily_data) / days, 2),
            "avg_retail_inflow": round(sum(d["retail_net_inflow"] for d in daily_data) / days, 2)
        },
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/{code}/main")
async def get_main_flow(code: str):
    """
    获取主力资金流向
    
    参数:
        code: 股票代码 (如: 000001)
    
    返回: 主力资金净流入/流出数据
    """
    logger.info(f"获取主力资金流向: {code}")
    
    # 验证股票代码格式
    if not code or len(code) < 6:
        raise HTTPException(status_code=400, detail="无效的股票代码")
    
    # 生成模拟数据
    data = generate_mock_main_flow(code)
    
    return success_response(data)


@router.get("/{code}/daily")
async def get_daily_flow(code: str, days: int = 5):
    """
    获取单日资金流向
    
    参数:
        code: 股票代码 (如: 000001)
        days: 查询天数 (默认5天，最大30天)
    
    返回: 单日资金流向数据
    """
    logger.info(f"获取单日资金流向: {code}, 天数: {days}")
    
    # 验证股票代码格式
    if not code or len(code) < 6:
        raise HTTPException(status_code=400, detail="无效的股票代码")
    
    # 限制天数范围
    if days < 1:
        days = 1
    elif days > 30:
        days = 30
    
    # 生成模拟数据
    data = generate_mock_daily_flow(code, days)
    
    return success_response(data)
