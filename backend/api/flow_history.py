# 资金流向历史数据API路由
"""
资金流向历史数据接口

提供股票历史资金流向数据查询
使用模拟数据
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional
import random
from models.response import success_response
from utils.logger import logger

# 创建路由 - 不使用前缀，由main.py统一挂载
router = APIRouter(tags=["资金流向历史"])


def generate_mock_flow_history(code: str, days: int = 30) -> dict:
    """生成模拟的历史资金流向数据"""
    history_data = []
    today = datetime.now()
    
    for i in range(days):
        date = (today - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        
        # 主力资金净流入 (万元)
        main_net_inflow = random.uniform(-10000, 15000)
        
        # 超大单净流入
        super_net = main_net_inflow * random.uniform(0.35, 0.55)
        
        # 大单净流入
        large_net = main_net_inflow * random.uniform(0.2, 0.35)
        
        # 中单净流入
        medium_net = main_net_inflow * random.uniform(0.1, 0.2)
        
        # 小单净流入
        small_net = main_net_inflow - super_net - large_net - medium_net
        
        # 成交额 (万元)
        turnover = random.uniform(50000, 500000)
        
        # 涨跌幅
        change_pct = random.uniform(-5, 5)
        
        history_data.append({
            "date": date,
            "main_net_inflow": round(main_net_inflow, 2),
            "main_net_inflow_rate": round(main_net_inflow / turnover * 100, 2) if turnover > 0 else 0,
            "super_large_net_inflow": round(super_net, 2),
            "large_net_inflow": round(large_net, 2),
            "medium_net_inflow": round(medium_net, 2),
            "small_net_inflow": round(small_net, 2),
            "super_large_ratio": round(super_net / main_net_inflow * 100, 2) if main_net_inflow != 0 else 0,
            "large_ratio": round(large_net / main_net_inflow * 100, 2) if main_net_inflow != 0 else 0,
            "medium_ratio": round(medium_net / main_net_inflow * 100, 2) if main_net_inflow != 0 else 0,
            "small_ratio": round(small_net / main_net_inflow * 100, 2) if main_net_inflow != 0 else 0,
            "turnover": round(turnover, 2),
            "change_pct": round(change_pct, 2),
            "price": round(random.uniform(10, 100), 2),
            "volume": round(turnover * 10000 / random.uniform(10, 100), 0)
        })
    
    # 计算统计信息
    total_main_inflow = sum(d["main_net_inflow"] for d in history_data)
    positive_days = len([d for d in history_data if d["main_net_inflow"] > 0])
    negative_days = len([d for d in history_data if d["main_net_inflow"] < 0])
    
    return {
        "code": code,
        "days": days,
        "data": history_data,
        "statistics": {
            "total_main_inflow": round(total_main_inflow, 2),
            "avg_main_inflow": round(total_main_inflow / days, 2),
            "max_inflow": round(max(d["main_net_inflow"] for d in history_data), 2),
            "min_inflow": round(min(d["main_net_inflow"] for d in history_data), 2),
            "positive_days": positive_days,
            "negative_days": negative_days,
            "neutral_days": days - positive_days - negative_days,
            "positive_rate": round(positive_days / days * 100, 2)
        },
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/{code}/history")
async def get_flow_history(
    code: str,
    days: int = Query(default=30, ge=1, le=90, description="查询天数，默认30天，最大90天")
):
    """
    获取股票资金流向历史数据
    
    参数:
        code: 股票代码 (如: 000001, 600000)
        days: 查询天数 (1-90天，默认30天)
    
    返回: 历史资金流向数据
    """
    logger.info(f"获取资金流向历史: {code}, 天数: {days}")
    
    # 验证股票代码格式
    if not code or len(code) < 6:
        raise HTTPException(status_code=400, detail="无效的股票代码")
    
    # 生成模拟数据
    data = generate_mock_flow_history(code, days)
    
    return success_response(data)
