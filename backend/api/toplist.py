# 龙虎榜API路由
from fastapi import APIRouter, Path, HTTPException
from datetime import datetime, timedelta
import random

# 创建路由
router = APIRouter(prefix="/api/toplist", tags=["龙虎榜"])

# 模拟龙虎榜数据
def generate_mock_toplist():
    """生成模拟的当日龙虎榜数据"""
    stocks = [
        {"code": "000001", "name": "平安银行", "change_pct": 9.85, "turnover": 8.52, "amount": 1256800000, "reason": "银行板块轮动"},
        {"code": "000002", "name": "万科A", "change_pct": 7.23, "turnover": 12.35, "amount": 2380000000, "reason": "地产政策利好"},
        {"code": "600519", "name": "贵州茅台", "change_pct": -3.21, "turnover": 1.25, "amount": 3560000000, "reason": "业绩不及预期"},
        {"code": "600036", "name": "招商银行", "change_pct": 5.67, "turnover": 4.58, "amount": 1890000000, "reason": "银行板块走强"},
        {"code": "000858", "name": "五粮液", "change_pct": 4.12, "turnover": 3.89, "amount": 987000000, "reason": "消费复苏"},
        {"code": "300750", "name": "宁德时代", "change_pct": -2.45, "turnover": 2.15, "amount": 2150000000, "reason": "新能源调整"},
        {"code": "601318", "name": "中国平安", "change_pct": 3.56, "turnover": 2.88, "amount": 1680000000, "reason": "保险板块反弹"},
        {"code": "002594", "name": "比亚迪", "change_pct": 6.78, "turnover": 5.42, "amount": 3250000000, "reason": "销量数据亮眼"},
        {"code": "000333", "name": "美的集团", "change_pct": 2.34, "turnover": 1.95, "amount": 876000000, "reason": "家电板块轮动"},
        {"code": "600900", "name": "长江电力", "change_pct": -1.23, "turnover": 0.85, "amount": 654000000, "reason": "高位回调"},
    ]
    
    # 添加日期和序号
    today = datetime.now().strftime("%Y-%m-%d")
    for i, stock in enumerate(stocks, 1):
        stock["date"] = today
        stock["rank"] = i
        stock["net_buy"] = round(random.uniform(10000000, 50000000), 2)
        stock["net_sell"] = round(random.uniform(8000000, 30000000), 2)
        stock["net_amount"] = stock["net_buy"] - stock["net_sell"]
    
    return stocks

def generate_mock_stock_toplist(code: str):
    """生成模拟的个股历史龙虎榜数据"""
    # 模拟最近30天的数据
    records = []
    base_date = datetime.now()
    
    stock_info = {
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
    
    info = stock_info.get(code, {"name": f"股票{code}", "industry": "未知"})
    
    for i in range(30):
        date = base_date - timedelta(days=i)
        
        # 随机决定是否有龙虎榜数据 (约50%概率)
        if random.random() > 0.5:
            change_pct = round(random.uniform(-10, 10), 2)
            net_buy = round(random.uniform(5000000, 80000000), 2)
            turnover = round(random.uniform(0.5, 15), 2)
            
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "code": code,
                "name": info["name"],
                "industry": info["industry"],
                "change_pct": change_pct,
                "turnover": turnover,
                "net_buy": net_buy,
                "net_sell": round(net_buy * random.uniform(0.3, 0.8), 2),
                "net_amount": round(net_buy * random.uniform(-0.5, 1.0), 2),
                "reason": random.choice(["业绩预增", "政策利好", "板块轮动", "资金流入", "重组预期", "业绩兑现"]),
                "institution_buy": round(random.uniform(1000000, 20000000), 2),
                "institution_sell": round(random.uniform(800000, 15000000), 2),
            })
    
    return records


@router.get("")
def get_toplist():
    """
    获取当日龙虎榜列表
    
    返回所有当日登上龙虎榜的股票
    
    Returns:
        dict: 统一响应格式，包含龙虎榜股票列表
    """
    data = generate_mock_toplist()
    return {
        "code": 0,
        "message": "success",
        "data": data
    }

@router.get("/{code}")
def get_stock_toplist(code: str = Path(..., description="股票代码")):
    """
    获取个股历史龙虎榜
    
    返回指定股票的历史龙虎榜数据
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含历史龙虎榜数据
    """
    # 验证股票代码格式
    if not code or len(code) < 6:
        raise HTTPException(status_code=400, detail="无效的股票代码")
    
    data = generate_mock_stock_toplist(code)
    return {
        "code": 0,
        "message": "success",
        "data": data
    }
