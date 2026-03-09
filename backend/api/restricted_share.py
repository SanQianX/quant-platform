# 限售股解禁数据API路由
"""
限售股解禁数据接口

提供限售股解禁列表查询、个股限售股解禁详情等功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import random

# 创建路由
router = APIRouter(prefix="/api/restricted-share", tags=["限售股解禁数据"])

# 限售股解禁股票配置 - 模拟A股市场中的限售股解禁股票
RESTRICTED_SHARE_STOCKS = {
    "600519": {"name": "贵州茅台", "industry": "白酒", "base_price": 1650.0, "total_shares": 1000000000},
    "600036": {"name": "招商银行", "industry": "银行", "base_price": 35.8, "total_shares": 2500000000},
    "600900": {"name": "长江电力", "industry": "电力", "base_price": 22.5, "total_shares": 1800000000},
    "601318": {"name": "中国平安", "industry": "保险", "base_price": 48.2, "total_shares": 3500000000},
    "601398": {"name": "工商银行", "industry": "银行", "base_price": 5.2, "total_shares": 15000000000},
    "600887": {"name": "伊利股份", "industry": "食品", "base_price": 28.5, "total_shares": 600000000},
    "600276": {"name": "恒瑞医药", "industry": "医药", "base_price": 52.3, "total_shares": 800000000},
    "601888": {"name": "中国中免", "industry": "旅游", "base_price": 68.5, "total_shares": 500000000},
    "600309": {"name": "万华化学", "industry": "化工", "base_price": 98.6, "total_shares": 700000000},
    "601012": {"name": "隆基绿能", "industry": "光伏", "base_price": 28.2, "total_shares": 900000000},
    "002594": {"name": "比亚迪", "industry": "汽车", "base_price": 268.5, "total_shares": 1200000000},
    "000858": {"name": "五粮液", "industry": "白酒", "base_price": 145.8, "total_shares": 400000000},
    "000333": {"name": "美的集团", "industry": "家电", "base_price": 58.6, "total_shares": 850000000},
    "000651": {"name": "格力电器", "industry": "家电", "base_price": 38.2, "total_shares": 600000000},
    "300750": {"name": "宁德时代", "industry": "新能源", "base_price": 185.6, "total_shares": 950000000},
    "600048": {"name": "保利发展", "industry": "房地产", "base_price": 12.8, "total_shares": 1200000000},
    "000002": {"name": "万科A", "industry": "房地产", "base_price": 8.2, "total_shares": 1500000000},
    "600028": {"name": "中国石化", "industry": "石油", "base_price": 6.5, "total_shares": 8000000000},
    "600585": {"name": "海螺水泥", "industry": "水泥", "base_price": 28.6, "total_shares": 550000000},
    "600009": {"name": "上海机场", "industry": "机场", "base_price": 45.6, "total_shares": 300000000},
    "000001": {"name": "平安银行", "industry": "银行", "base_price": 12.5, "total_shares": 950000000},
    "600030": {"name": "中信证券", "industry": "证券", "base_price": 19.8, "total_shares": 1200000000},
    "601166": {"name": "兴业银行", "industry": "银行", "base_price": 17.6, "total_shares": 1800000000},
    "600000": {"name": "浦发银行", "industry": "银行", "base_price": 8.9, "total_shares": 2800000000},
    "601328": {"name": "交通银行", "industry": "银行", "base_price": 5.6, "total_shares": 5000000000},
    "000725": {"name": "京东方A", "industry": "电子", "base_price": 4.2, "total_shares": 3500000000},
    "002415": {"name": "海康威视", "industry": "安防", "base_price": 32.5, "total_shares": 950000000},
    "300059": {"name": "东方财富", "industry": "金融", "base_price": 18.9, "total_shares": 650000000},
    "601688": {"name": "中国巨石", "industry": "玻纤", "base_price": 15.6, "total_shares": 400000000},
    "600104": {"name": "上汽集团", "industry": "汽车", "base_price": 14.8, "total_shares": 2300000000},
}


def generate_unlock_date(days_ago: int = 0) -> str:
    """生成解禁日期"""
    date = datetime.now() + timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")


def get_holder_type() -> str:
    """生成模拟股东类型"""
    holder_types = [
        "首发原股东限售股",
        "定向增发机构配售股",
        "股权激励限售股",
        "追加承诺限售股",
        "首发战略配售股",
        "股改限售股",
        "配股原股东限售股"
    ]
    return random.choice(holder_types)


def get_holder_name() -> str:
    """生成模拟股东名称"""
    # 机构投资者
    institutions = [
        "华能资本", "国新投资", "国开金融", "社保基金", "中国人寿", 
        "中国平安", "泰康人寿", "太平洋保险", "中信证券", "华泰证券",
        "国泰君安", "招商证券", "高瓴资本", "红杉中国", "IDG资本",
        "软银中国", "腾讯投资", "阿里资本", "百度风投", "京东投资"
    ]
    
    # 个人投资者
    individuals = [
        "张某", "王某", "李某", "赵某", "刘某", "陈某", "杨某", 
        "黄某", "周某", "吴某", "徐某", "孙某", "胡某", "朱某"
    ]
    
    if random.random() > 0.5:
        return random.choice(institutions)
    else:
        return random.choice(individuals)


def get_mock_restricted_share_list() -> list:
    """
    生成模拟限售股解禁列表数据
    
    Returns:
        list: 模拟限售股解禁列表
    """
    unlock_list = []
    
    # 为每只股票生成多笔解禁记录
    for code, info in RESTRICTED_SHARE_STOCKS.items():
        # 每只股票生成1-3笔解禁记录
        num_unlocks = random.randint(1, 3)
        
        for i in range(num_unlocks):
            total_shares = info["total_shares"]
            base_price = info["base_price"]
            
            # 解禁股数（占总股本的1%-15%）
            unlock_ratio = round(random.uniform(1, 15), 2)
            unlock_shares = int(total_shares * unlock_ratio / 100)
            
            # 解禁日期（未来30天内）
            days_offset = random.randint(-30, 60)
            unlock_date = generate_unlock_date(days_offset)
            
            # 股东类型
            holder_type = get_holder_type()
            
            # 股东名称
            holder_name = get_holder_name()
            
            # 解禁前持股比例
            holding_ratio_before = round(random.uniform(1, 20), 2)
            
            # 解禁后持股比例
            holding_ratio_after = round(holding_ratio_before * random.uniform(0.3, 0.9), 2)
            
            # 限售股成本价
            cost_price = round(base_price * random.uniform(0.2, 0.7), 2)
            
            # 当前价格
            current_price = base_price
            
            # 浮盈比例
            profit_ratio = round((current_price - cost_price) / cost_price * 100, 2)
            
            # 解禁市值
            unlock_market_value = round(unlock_shares * current_price / 100000000, 2)
            
            # 公告日期
            announcement_date = generate_unlock_date(random.randint(-5, 0))
            
            unlock_list.append({
                "code": code,
                "name": info["name"],
                "industry": info["industry"],
                "holder_name": holder_name,
                "holder_type": holder_type,
                "unlock_shares": unlock_shares,
                "unlock_ratio": unlock_ratio,
                "unlock_date": unlock_date,
                "holding_ratio_before": holding_ratio_before,
                "holding_ratio_after": holding_ratio_after,
                "cost_price": cost_price,
                "current_price": current_price,
                "profit_ratio": profit_ratio,
                "unlock_market_value": unlock_market_value,
                "announcement_date": announcement_date,
                "source": "上市公司公告"
            })
    
    # 按解禁日期排序（未来的在前）
    unlock_list.sort(key=lambda x: x["unlock_date"], reverse=True)
    
    return unlock_list


def get_mock_restricted_share_detail(code: str) -> dict:
    """
    生成模拟个股限售股解禁详情数据
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 模拟个股限售股解禁详情
    """
    if code not in RESTRICTED_SHARE_STOCKS:
        raise HTTPException(status_code=404, detail=f"股票代码 {code} 不存在")
    
    info = RESTRICTED_SHARE_STOCKS[code]
    base_price = info["base_price"]
    total_shares = info["total_shares"]
    
    # 生成该股票的多笔解禁记录
    unlocks = []
    num_unlocks = random.randint(8, 15)
    
    for i in range(num_unlocks):
        # 解禁股数
        unlock_ratio = round(random.uniform(0.5, 20), 2)
        unlock_shares = int(total_shares * unlock_ratio / 100)
        
        # 解禁日期
        days_offset = random.randint(-90, 90)
        unlock_date = generate_unlock_date(days_offset)
        
        # 股东类型
        holder_type = get_holder_type()
        
        # 股东名称
        holder_name = get_holder_name()
        
        # 解禁前后持股比例
        holding_ratio_before = round(random.uniform(0.5, 25), 2)
        holding_ratio_after = round(holding_ratio_before * random.uniform(0.2, 0.95), 2)
        
        # 限售股成本价
        cost_price = round(base_price * random.uniform(0.15, 0.8), 2)
        
        # 当前价格
        current_price = base_price
        
        # 浮盈比例
        profit_ratio = round((current_price - cost_price) / cost_price * 100, 2)
        
        # 解禁市值
        unlock_market_value = round(unlock_shares * current_price / 100000000, 2)
        
        # 公告日期
        announcement_date = generate_unlock_date(random.randint(-10, 0))
        
        unlocks.append({
            "holder_name": holder_name,
            "holder_type": holder_type,
            "unlock_shares": unlock_shares,
            "unlock_ratio": unlock_ratio,
            "unlock_date": unlock_date,
            "holding_ratio_before": holding_ratio_before,
            "holding_ratio_after": holding_ratio_after,
            "cost_price": cost_price,
            "current_price": current_price,
            "profit_ratio": profit_ratio,
            "unlock_market_value": unlock_market_value,
            "announcement_date": announcement_date,
            "source": "上市公司公告"
        })
    
    # 按解禁日期排序（未来的在前）
    unlocks.sort(key=lambda x: x["unlock_date"], reverse=True)
    
    # 计算汇总统计
    total_unlock_shares = sum(u["unlock_shares"] for u in unlocks)
    total_market_value = sum(u["unlock_market_value"] for u in unlocks)
    unlocked_shares = sum(u["unlock_shares"] for u in unlocks if u["unlock_date"] <= datetime.now().strftime("%Y-%m-%d"))
    future_unlock_shares = sum(u["unlock_shares"] for u in unlocks if u["unlock_date"] > datetime.now().strftime("%Y-%m-%d"))
    
    # 最新价格
    change_pct = round(random.uniform(-8, 8), 2)
    latest_price = round(base_price * (1 + change_pct / 100), 2)
    
    # 即将解禁（30天内）
    upcoming = [u for u in unlocks if 0 <= (datetime.strptime(u["unlock_date"], "%Y-%m-%d") - datetime.now()).days <= 30]
    upcoming_unlock_shares = sum(u["unlock_shares"] for u in upcoming)
    
    return {
        "code": code,
        "name": info["name"],
        "industry": info["industry"],
        "total_shares": total_shares,
        "latest_price": latest_price,
        "prev_close": base_price,
        "change_pct": change_pct,
        "unlocks": unlocks,
        "summary": {
            "total_records": len(unlocks),
            "total_unlock_shares": total_unlock_shares,
            "total_market_value": total_market_value,
            "unlocked_shares": unlocked_shares,
            "future_unlock_shares": future_unlock_shares,
            "upcoming_unlock_shares": upcoming_unlock_shares,
            "upcoming_count": len(upcoming),
            "unlock_ratio": round(total_unlock_shares / total_shares * 100, 2)
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/list")
async def get_restricted_share_list():
    """
    获取限售股解禁列表
    
    返回所有限售股解禁记录列表
    
    Returns:
        限售股解禁列表数据
    """
    try:
        unlock_list = get_mock_restricted_share_list()
        
        # 计算汇总数据
        total_unlock_shares = sum(item["unlock_shares"] for item in unlock_list)
        total_market_value = sum(item["unlock_market_value"] for item in unlock_list)
        
        # 即将解禁（30天内）
        now = datetime.now()
        upcoming = [u for u in unlock_list if 0 <= (datetime.strptime(u["unlock_date"], "%Y-%m-%d") - now).days <= 30]
        past = [u for u in unlock_list if u["unlock_date"] < now.strftime("%Y-%m-%d")]
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "list": unlock_list,
                "total_count": len(unlock_list),
                "summary": {
                    "total_unlock_shares": total_unlock_shares,
                    "total_market_value": total_market_value,
                    "upcoming_count": len(upcoming),
                    "upcoming_unlock_shares": sum(u["unlock_shares"] for u in upcoming),
                    "past_count": len(past)
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
async def get_restricted_share_detail(code: str):
    """
    获取个股限售股解禁详情
    
    返回指定股票的限售股解禁详细数据
    
    Args:
        code: 股票代码
        
    Returns:
        个股限售股解禁详情数据
    """
    try:
        detail = get_mock_restricted_share_detail(code)
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
