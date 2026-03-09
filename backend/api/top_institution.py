# 机构龙虎榜API路由
from fastapi import APIRouter, Path, HTTPException
from datetime import datetime, timedelta
import random

# 创建路由
router = APIRouter(prefix="/api/topinstitution", tags=["机构龙虎榜"])

# 机构类型定义
INSTITUTION_TYPES = ["基金", "券商", "保险", "社保", "QFII", "信托", "银行", "私募"]

# 模拟机构买卖榜数据
def generate_mock_top_institution_list():
    """生成模拟的机构买卖榜列表数据"""
    stocks = [
        {"code": "000001", "name": "平安银行", "industry": "银行", "change_pct": 5.82, "institution_net_buy": 256800000, "institution_net_sell": 128500000, "institution_net_amount": 128300000},
        {"code": "000002", "name": "万科A", "industry": "房地产", "change_pct": 3.45, "institution_net_buy": 189200000, "institution_net_sell": 98500000, "institution_net_amount": 90700000},
        {"code": "600519", "name": "贵州茅台", "industry": "白酒", "change_pct": -2.15, "institution_net_buy": 568000000, "institution_net_sell": 892000000, "institution_net_amount": -324000000},
        {"code": "600036", "name": "招商银行", "industry": "银行", "change_pct": 4.21, "institution_net_buy": 325600000, "institution_net_sell": 156800000, "institution_net_amount": 168800000},
        {"code": "000858", "name": "五粮液", "industry": "白酒", "change_pct": 2.88, "institution_net_buy": 198500000, "institution_net_sell": 87600000, "institution_net_amount": 110900000},
        {"code": "300750", "name": "宁德时代", "industry": "新能源", "change_pct": -4.56, "institution_net_buy": 156200000, "institution_net_sell": 398500000, "institution_net_amount": -242300000},
        {"code": "601318", "name": "中国平安", "industry": "保险", "change_pct": 1.95, "institution_net_buy": 278900000, "institution_net_sell": 145600000, "institution_net_amount": 133300000},
        {"code": "002594", "name": "比亚迪", "industry": "汽车", "change_pct": 6.72, "institution_net_buy": 456800000, "institution_net_sell": 198700000, "institution_net_amount": 258100000},
        {"code": "000333", "name": "美的集团", "industry": "家电", "change_pct": 3.12, "institution_net_buy": 167800000, "institution_net_sell": 78500000, "institution_net_amount": 89300000},
        {"code": "600900", "name": "长江电力", "industry": "电力", "change_pct": -0.85, "institution_net_buy": 98600000, "institution_net_sell": 112500000, "institution_net_amount": -13900000},
        {"code": "600276", "name": "恒瑞医药", "industry": "医药", "change_pct": 2.35, "institution_net_buy": 215600000, "institution_net_sell": 98700000, "institution_net_amount": 116900000},
        {"code": "000725", "name": "京东方A", "industry": "电子", "change_pct": -1.28, "institution_net_buy": 87500000, "institution_net_sell": 156200000, "institution_net_amount": -68700000},
    ]
    
    # 添加日期和序号
    today = datetime.now().strftime("%Y-%m-%d")
    for i, stock in enumerate(stocks, 1):
        stock["date"] = today
        stock["rank"] = i
        stock["buy_count"] = random.randint(5, 25)
        stock["sell_count"] = random.randint(3, 18)
        stock["net_buy_rate"] = round(stock["institution_net_amount"] / (stock["institution_net_buy"] + stock["institution_net_sell"]) * 100, 2)
    
    return stocks


def generate_mock_stock_institution(code: str):
    """生成模拟的个股机构买卖数据"""
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
        "600276": {"name": "恒瑞医药", "industry": "医药"},
        "000725": {"name": "京东方A", "industry": "电子"},
    }
    
    info = stock_info.get(code, {"name": f"股票{code}", "industry": "未知"})
    
    # 生成最近30天的数据
    records = []
    base_date = datetime.now()
    
    for i in range(30):
        date = base_date - timedelta(days=i)
        
        # 约60%概率有机构买卖数据
        if random.random() > 0.4:
            change_pct = round(random.uniform(-8, 8), 2)
            
            # 生成各个机构的买卖数据
            institutions = []
            total_buy = 0
            total_sell = 0
            
            for inst_type in random.sample(INSTITUTION_TYPES, random.randint(4, 8)):
                buy_amount = round(random.uniform(500000, 15000000), 2)
                sell_amount = round(random.uniform(300000, 12000000), 2)
                net_amount = buy_amount - sell_amount
                
                institutions.append({
                    "type": inst_type,
                    "buy_amount": buy_amount,
                    "sell_amount": sell_amount,
                    "net_amount": net_amount,
                    "net_type": "买入" if net_amount > 0 else "卖出"
                })
                
                total_buy += buy_amount
                total_sell += sell_amount
            
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "code": code,
                "name": info["name"],
                "industry": info["industry"],
                "change_pct": change_pct,
                "close_price": round(random.uniform(10, 200), 2),
                "total_buy": round(total_buy, 2),
                "total_sell": round(total_sell, 2),
                "net_amount": round(total_buy - total_sell, 2),
                "net_type": "净买入" if total_buy > total_sell else "净卖出",
                "institution_count": len(institutions),
                "institutions": sorted(institutions, key=lambda x: abs(x["net_amount"]), reverse=True)[:10]
            })
    
    return records


@router.get("/list")
def get_top_institution_list():
    """
    获取机构买卖榜列表
    
    返回当日机构买卖榜数据
    
    Returns:
        dict: 统一响应格式，包含机构买卖榜股票列表
    """
    data = generate_mock_top_institution_list()
    return {
        "code": 0,
        "message": "success",
        "data": data
    }


@router.get("/{code}")
def get_stock_institution(code: str = Path(..., description="股票代码")):
    """
    获取个股机构买卖数据
    
    返回指定股票的机构买卖历史数据
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含个股机构买卖数据
    """
    # 验证股票代码格式
    if not code or len(code) < 6:
        raise HTTPException(status_code=400, detail="无效的股票代码")
    
    data = generate_mock_stock_institution(code)
    return {
        "code": 0,
        "message": "success",
        "data": data
    }
