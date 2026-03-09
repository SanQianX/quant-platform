# 龙虎榜历史数据API路由
from fastapi import APIRouter, Path, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
import random

# 创建路由
router = APIRouter(prefix="/api/toplist", tags=["龙虎榜"])

# 股票信息映射
STOCK_INFO = {
    "000001": {"name": "平安银行", "industry": "银行"},
    "000002": {"name": "万科A", "industry": "房地产"},
    "600519": {"name": "贵州茅台", "industry": "白酒"},
    "600036": {"name": "招商银行", "industry": "银行"},
    "000858": {"name": "五粮液", "industry": "白酒"},
    "300750": {"name": "宁德时代", "industry": "新能源"},
    "601318": {"name": "中国平安", "industry": "保险"},
    "002594": {"name": "比亚迪", "industry": "汽车"},
    "000333": {"name": "美的集团", "industry": "家电"},
    "600900": {"name": "长江电力", "industry": "电力"},
}


def generate_history_data(code: str, days: int = 30) -> List[dict]:
    """
    生成模拟的历史龙虎榜数据
    
    Args:
        code: 股票代码
        days: 查询天数，默认30天
        
    Returns:
        list: 历史龙虎榜数据列表
    """
    info = STOCK_INFO.get(code, {"name": f"股票{code}", "industry": "未知"})
    
    records = []
    base_date = datetime.now()
    
    for i in range(days):
        date = base_date - timedelta(days=i)
        
        # 随机决定是否有龙虎榜数据 (约60%概率)
        if random.random() > 0.4:
            change_pct = round(random.uniform(-10, 10), 2)
            is_rise = change_pct > 0
            
            # 根据涨跌生成买卖数据
            if is_rise:
                net_buy = round(random.uniform(10000000, 100000000), 2)
                net_sell = round(net_buy * random.uniform(0.2, 0.6), 2)
            else:
                net_buy = round(random.uniform(5000000, 30000000), 2)
                net_sell = round(random.uniform(15000000, 80000000), 2)
            
            turnover = round(random.uniform(1.0, 20), 2)
            amount = round(random.uniform(100000000, 5000000000), 2)
            
            reason = random.choice([
                "业绩预增",
                "政策利好",
                "板块轮动",
                "资金大幅流入",
                "重组预期",
                "业绩兑现",
                "行业景气",
                "龙头股上涨",
                "业绩亏损",
                "股东减持"
            ])
            
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "code": code,
                "name": info["name"],
                "industry": info["industry"],
                "change_pct": change_pct,
                "close": round(random.uniform(10, 500), 2),
                "turnover": turnover,
                "amount": amount,
                "net_buy": net_buy,
                "net_sell": net_sell,
                "net_amount": round(net_buy - net_sell, 2),
                "reason": reason,
                "institution_net": round(random.uniform(-10000000, 20000000), 2),
                "broker_net": round(random.uniform(-8000000, 15000000), 2),
                "rank": random.randint(1, 50) if random.random() > 0.3 else None,
                "buy_seats": random.randint(5, 30),
                "sell_seats": random.randint(5, 30),
            })
    
    # 按日期排序
    records.sort(key=lambda x: x["date"], reverse=True)
    
    return records


def generate_summary(code: str, data: List[dict]) -> dict:
    """
    生成历史数据统计摘要
    
    Args:
        code: 股票代码
        data: 历史数据
        
    Returns:
        dict: 统计摘要
    """
    if not data:
        return {
            "total_days": 0,
            "rise_days": 0,
            "fall_days": 0,
            "avg_turnover": 0,
            "total_amount": 0,
            "total_net_amount": 0,
        }
    
    rise_days = sum(1 for r in data if r["change_pct"] > 0)
    fall_days = sum(1 for r in data if r["change_pct"] < 0)
    
    return {
        "total_days": len(data),
        "rise_days": rise_days,
        "fall_days": fall_days,
        "flat_days": len(data) - rise_days - fall_days,
        "avg_turnover": round(sum(r["turnover"] for r in data) / len(data), 2),
        "total_amount": round(sum(r["amount"] for r in data), 2),
        "total_net_amount": round(sum(r["net_amount"] for r in data), 2),
        "max_rise": max(r["change_pct"] for r in data),
        "max_fall": min(r["change_pct"] for r in data),
    }


@router.get("/{code}/history")
def get_toplist_history(
    code: str = Path(..., description="股票代码"),
    days: int = 30
):
    """
    获取股票龙虎榜历史数据
    
    返回指定股票的历史龙虎榜数据及统计摘要
    
    Args:
        code: 股票代码 (如: 600519, 000001)
        days: 查询天数，默认30天，最大180天
        
    Returns:
        dict: 统一响应格式，包含历史龙虎榜数据和统计摘要
    """
    # 验证股票代码格式
    if not code or len(code) < 6:
        raise HTTPException(status_code=400, detail="无效的股票代码")
    
    # 限制查询天数
    if days > 180:
        days = 180
    elif days < 1:
        days = 1
    
    # 生成模拟数据
    history_data = generate_history_data(code, days)
    summary = generate_summary(code, history_data)
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": code,
            "name": STOCK_INFO.get(code, {}).get("name", f"股票{code}"),
            "history": history_data,
            "summary": summary
        }
    }
