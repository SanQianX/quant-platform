# 股东增减持数据API路由
"""
股东增减持数据接口

提供股东增减持列表查询、个股股东增减持详情等功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import random

# 创建路由
router = APIRouter(prefix="/api/holder-trade", tags=["股东增减持数据"])

# 股东增减持股票配置 - 模拟A股市场中的股东增减持股票
HOLDER_TRADE_STOCKS = {
    "600519": {"name": "贵州茅台", "industry": "白酒", "base_price": 1650.0},
    "600036": {"name": "招商银行", "industry": "银行", "base_price": 35.8},
    "600900": {"name": "长江电力", "industry": "电力", "base_price": 22.5},
    "601318": {"name": "中国平安", "industry": "保险", "base_price": 48.2},
    "601398": {"name": "工商银行", "industry": "银行", "base_price": 5.2},
    "600887": {"name": "伊利股份", "industry": "食品", "base_price": 28.5},
    "600276": {"name": "恒瑞医药", "industry": "医药", "base_price": 52.3},
    "601888": {"name": "中国中免", "industry": "旅游", "base_price": 68.5},
    "600309": {"name": "万华化学", "industry": "化工", "base_price": 98.6},
    "601012": {"name": "隆基绿能", "industry": "光伏", "base_price": 28.2},
    "002594": {"name": "比亚迪", "industry": "汽车", "base_price": 268.5},
    "000858": {"name": "五粮液", "industry": "白酒", "base_price": 145.8},
    "000333": {"name": "美的集团", "industry": "家电", "base_price": 58.6},
    "000651": {"name": "格力电器", "industry": "家电", "base_price": 38.2},
    "300750": {"name": "宁德时代", "industry": "新能源", "base_price": 185.6},
    "600048": {"name": "保利发展", "industry": "房地产", "base_price": 12.8},
    "000002": {"name": "万科A", "industry": "房地产", "base_price": 8.2},
    "600028": {"name": "中国石化", "industry": "石油", "base_price": 6.5},
    "600585": {"name": "海螺水泥", "industry": "水泥", "base_price": 28.6},
    "600009": {"name": "上海机场", "industry": "机场", "base_price": 45.6},
    "000001": {"name": "平安银行", "industry": "银行", "base_price": 12.5},
    "600030": {"name": "中信证券", "industry": "证券", "base_price": 19.8},
    "601166": {"name": "兴业银行", "industry": "银行", "base_price": 17.6},
    "600000": {"name": "浦发银行", "industry": "银行", "base_price": 8.9},
    "601328": {"name": "交通银行", "industry": "银行", "base_price": 5.6},
    "000725": {"name": "京东方A", "industry": "电子", "base_price": 4.2},
    "002415": {"name": "海康威视", "industry": "安防", "base_price": 32.5},
    "300059": {"name": "东方财富", "industry": "金融", "base_price": 18.9},
    "601688": {"name": "中国巨石", "industry": "玻纤", "base_price": 15.6},
    "600104": {"name": "上汽集团", "industry": "汽车", "base_price": 14.8},
}


def generate_holder_trade_date(days_ago: int = 0) -> str:
    """生成交易日期"""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")


def get_holder_name() -> str:
    """生成模拟股东名称"""
    surnames = ["张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴", "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"]
    given_names = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀英", "霞", "平"]
    first_name = random.choice(surnames) + random.choice(given_names)
    
    # 股东类型
    holder_types = ["个人股东", "机构股东", "高管", "员工持股计划", "战略投资者", "基金", "保险资金", "社保基金"]
    
    return f"{first_name}（{random.choice(holder_types)}）"


def get_mock_holder_trade_list() -> list:
    """
    生成模拟股东增减持列表数据
    
    Returns:
        list: 模拟股东增减持列表
    """
    trade_list = []
    
    # 为每只股票生成多笔增减持记录
    for code, info in HOLDER_TRADE_STOCKS.items():
        # 每只股票生成1-4笔增减持记录
        num_trades = random.randint(1, 4)
        
        for i in range(num_trades):
            base_price = info["base_price"]
            
            # 增减持类型
            trade_type = random.choice(["增持", "减持"])
            
            # 变动股数（增持或减持）
            if trade_type == "增持":
                volume = random.randint(10000, 5000000)
            else:
                volume = random.randint(10000, 8000000)
            
            # 变动比例（占总股本）
            change_ratio = round(random.uniform(0.01, 2.5), 2)
            
            # 变动后持股比例
            if trade_type == "增持":
                holding_ratio = round(random.uniform(1.0, 10.0), 2)
            else:
                holding_ratio = round(random.uniform(0.5, 5.0), 2)
            
            # 变动均价
            change_price = round(base_price * random.uniform(0.95, 1.05), 2)
            
            # 变动日期
            change_date = generate_holder_trade_date(random.randint(0, 60))
            
            # 股东名称
            holder_name = get_holder_name()
            
            # 股东性质
            holder_natures = ["自然人", "法人", "其他", "高管及员工"]
            holder_nature = random.choice(holder_natures)
            
            # 公告日期
            announcement_date = generate_holder_trade_date(random.randint(0, 5))
            
            trade_list.append({
                "code": code,
                "name": info["name"],
                "industry": info["industry"],
                "holder_name": holder_name,
                "holder_nature": holder_nature,
                "trade_type": trade_type,
                "volume": volume,
                "change_ratio": change_ratio,
                "change_price": change_price,
                "change_amount": round(volume * change_price, 2),
                "holding_ratio": holding_ratio,
                "change_date": change_date,
                "announcement_date": announcement_date,
                "source": "上市公司公告"
            })
    
    # 按日期排序（最近的在前）
    trade_list.sort(key=lambda x: x["change_date"], reverse=True)
    
    return trade_list


def get_mock_holder_trade_detail(code: str) -> dict:
    """
    生成模拟个股股东增减持详情数据
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 模拟个股股东增减持详情
    """
    if code not in HOLDER_TRADE_STOCKS:
        raise HTTPException(status_code=404, detail=f"股票代码 {code} 不存在")
    
    info = HOLDER_TRADE_STOCKS[code]
    base_price = info["base_price"]
    
    # 生成该股票的多笔增减持记录
    trades = []
    num_trades = random.randint(8, 20)
    
    for i in range(num_trades):
        # 增减持类型
        trade_type = random.choice(["增持", "减持"])
        
        # 变动股数
        if trade_type == "增持":
            volume = random.randint(10000, 5000000)
        else:
            volume = random.randint(10000, 8000000)
        
        # 变动比例
        change_ratio = round(random.uniform(0.01, 3.0), 2)
        
        # 变动后持股比例
        if trade_type == "增持":
            holding_ratio = round(random.uniform(1.0, 15.0), 2)
        else:
            holding_ratio = round(random.uniform(0.5, 8.0), 2)
        
        # 变动均价
        change_price = round(base_price * random.uniform(0.92, 1.08), 2)
        
        # 变动日期
        change_date = generate_holder_trade_date(random.randint(0, 90))
        
        # 股东名称
        holder_name = get_holder_name()
        
        # 股东性质
        holder_natures = ["自然人", "法人", "其他", "高管及员工"]
        holder_nature = random.choice(holder_natures)
        
        # 公告日期
        announcement_date = generate_holder_trade_date(random.randint(0, 5))
        
        trades.append({
            "holder_name": holder_name,
            "holder_nature": holder_nature,
            "trade_type": trade_type,
            "volume": volume,
            "change_ratio": change_ratio,
            "change_price": change_price,
            "change_amount": round(volume * change_price, 2),
            "holding_ratio": holding_ratio,
            "change_date": change_date,
            "announcement_date": announcement_date,
            "source": "上市公司公告"
        })
    
    # 按日期排序
    trades.sort(key=lambda x: x["change_date"], reverse=True)
    
    # 计算汇总统计
    total_increase = sum(t["volume"] for t in trades if t["trade_type"] == "增持")
    total_decrease = sum(t["volume"] for t in trades if t["trade_type"] == "减持")
    net_change = total_increase - total_decrease
    
    increase_count = sum(1 for t in trades if t["trade_type"] == "增持")
    decrease_count = sum(1 for t in trades if t["trade_type"] == "减持")
    
    # 最新价格
    change_pct = round(random.uniform(-8, 8), 2)
    latest_price = round(base_price * (1 + change_pct / 100), 2)
    
    return {
        "code": code,
        "name": info["name"],
        "industry": info["industry"],
        "latest_price": latest_price,
        "prev_close": base_price,
        "change_pct": change_pct,
        "trades": trades,
        "summary": {
            "total_trades": len(trades),
            "increase_count": increase_count,
            "decrease_count": decrease_count,
            "total_increase": total_increase,
            "total_decrease": total_decrease,
            "net_change": net_change,
            "increase_amount": round(total_increase * base_price, 2),
            "decrease_amount": round(total_decrease * base_price, 2),
            "net_amount": round(net_change * base_price, 2)
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/list")
async def get_holder_trade_list():
    """
    获取股东增减持列表
    
    返回所有股东增减持记录列表
    
    Returns:
        股东增减持列表数据
    """
    try:
        trade_list = get_mock_holder_trade_list()
        
        # 计算汇总数据
        total_increase = sum(item["volume"] for item in trade_list if item["trade_type"] == "增持")
        total_decrease = sum(item["volume"] for item in trade_list if item["trade_type"] == "减持")
        increase_count = sum(1 for item in trade_list if item["trade_type"] == "增持")
        decrease_count = sum(1 for item in trade_list if item["trade_type"] == "减持")
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "list": trade_list,
                "total_count": len(trade_list),
                "summary": {
                    "increase_count": increase_count,
                    "decrease_count": decrease_count,
                    "total_increase": total_increase,
                    "total_decrease": total_decrease,
                    "net_change": total_increase - total_decrease
                },
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except Exception as e:
        return {
            "code": -1,
            "message": str(e),
            "data": None
        }


@router.get("/{code}")
async def get_holder_trade_detail(code: str):
    """
    获取个股股东增减持详情
    
    返回指定股票的股东增减持详细数据
    
    Args:
        code: 股票代码
        
    Returns:
        个股股东增减持详情数据
    """
    try:
        detail = get_mock_holder_trade_detail(code)
        return {
            "code": 0,
            "message": "success",
            "data": detail
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "code": -1,
            "message": str(e),
            "data": None
        }
