# 实时行情API路由
"""
实时行情数据接口

提供股票实时行情、涨跌榜、成交明细等功能
使用 AkShare 获取实时数据
"""

from fastapi import APIRouter, Query, HTTPException
import akshare as ak
import pandas as pd
from datetime import datetime
from models.response import success_response, error_response
from config import MOCK_DATA_CONFIG
from utils.logger import logger
import random

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票实时行情"])


def get_mock_quote(stock_code: str) -> dict:
    """
    生成模拟实时行情数据
    
    Args:
        stock_code: 股票代码
        
    Returns:
        dict: 模拟行情数据
    """
    # 基于股票代码生成稳定的随机数
    seed = int(stock_code) if stock_code.isdigit() else hash(stock_code) % 10000
    random.seed(seed)
    
    # 基础价格
    base_prices = {
        "600519": 1850.0,
        "000001": 12.5,
        "300750": 210.0,
        "600036": 36.0,
        "601318": 46.0,
        "000858": 155.0,
        "002594": 260.0,
        "600900": 23.0,
        "601888": 72.0,
        "300059": 21.0,
    }
    base_price = base_prices.get(stock_code, 50.0)
    
    # 生成随机价格
    change_pct = random.uniform(-5, 5)
    price = base_price * (1 + change_pct / 100)
    prev_close = base_price
    
    return {
        "code": stock_code,
        "name": f"股票{stock_code}",
        "latest_price": round(price, 2),
        "prev_close": round(prev_close, 2),
        "open": round(prev_close * (1 + random.uniform(-0.02, 0.02)), 2),
        "high": round(price * (1 + random.uniform(0, 0.03)), 2),
        "low": round(price * (1 - random.uniform(0, 0.03)), 2),
        "change": round(price - prev_close, 2),
        "change_pct": round(change_pct, 2),
        "volume": random.randint(1000000, 50000000),
        "amount": round(price * random.randint(1000000, 50000000), 2),
        "bid_price1": round(price * 0.998, 2),
        "bid_price2": round(price * 0.996, 2),
        "bid_price3": round(price * 0.994, 2),
        "ask_price1": round(price * 1.002, 2),
        "ask_price2": round(price * 1.004, 2),
        "ask_price3": round(price * 1.006, 2),
        "bid_volume1": random.randint(1000, 100000),
        "bid_volume2": random.randint(1000, 100000),
        "bid_volume3": random.randint(1000, 100000),
        "ask_volume1": random.randint(1000, 100000),
        "ask_volume2": random.randint(1000, 100000),
        "ask_volume3": random.randint(1000, 100000),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def get_mock_transactions(stock_code: str, limit: int = 50) -> list:
    """
    生成模拟成交明细数据
    
    Args:
        stock_code: 股票代码
        limit: 返回条数
        
    Returns:
        list: 模拟成交明细列表
    """
    seed = int(stock_code) if stock_code.isdigit() else hash(stock_code) % 10000
    random.seed(seed)
    
    base_price = 50.0
    transactions = []
    
    for i in range(limit):
        time_str = f"{random.randint(9, 15)}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
        price = base_price * (1 + random.uniform(-0.01, 0.01))
        volume = random.randint(100, 10000)
        is_buy = random.choice([True, False])
        
        transactions.append({
            "time": time_str,
            "price": round(price, 2),
            "volume": volume,
            "amount": round(price * volume, 2),
            "type": "买入" if is_buy else "卖出"
        })
    
    return transactions


def get_mock_changes(top_n: int = 50) -> list:
    """
    生成模拟涨跌榜数据
    
    Args:
        top_n: 返回条数
        
    Returns:
        list: 模拟涨跌榜列表
    """
    # 模拟股票列表
    mock_stocks = [
        {"code": "600519", "name": "贵州茅台"},
        {"code": "000001", "name": "平安银行"},
        {"code": "300750", "name": "宁德时代"},
        {"code": "600036", "name": "招商银行"},
        {"code": "601318", "name": "中国平安"},
        {"code": "000858", "name": "五粮液"},
        {"code": "002594", "name": "比亚迪"},
        {"code": "600900", "name": "长江电力"},
        {"code": "601888", "name": "中国中免"},
        {"code": "300059", "name": "东方财富"},
    ]
    
    changes = []
    for i, stock in enumerate(mock_stocks[:top_n]):
        change_pct = random.uniform(-10, 10)
        base_price = 100
        price = base_price * (1 + change_pct / 100)
        
        changes.append({
            "code": stock["code"],
            "name": stock["name"],
            "latest_price": round(price, 2),
            "change": round(price - base_price, 2),
            "change_pct": round(change_pct, 2),
            "volume": random.randint(1000000, 50000000),
            "amount": round(price * random.randint(1000000, 50000000), 2),
            "turnover": round(random.uniform(0.1, 10), 2)
        })
    
    # 按涨跌幅排序
    changes.sort(key=lambda x: x["change_pct"], reverse=True)
    return changes


@router.get("/{code}/quote")
def get_stock_quote(code: str):
    """
    获取股票实时行情
    
    返回股票的实时行情数据，包括最新价、涨跌幅、成交量等
    
    Args:
        code: 股票代码 (如: 600519)
        
    Returns:
        dict: 统一响应格式，包含实时行情数据
    """
    logger.info(f"获取实时行情: {code}")
    
    # 验证股票代码
    if not code or len(code) != 6:
        return error_response("股票代码格式错误，应为6位数字")
    
    try:
        # 尝试从 AkShare 获取实时行情
        try:
            df = ak.stock_zh_a_spot_em()
            
            # 过滤指定股票
            stock_df = df[df['代码'] == code]
            
            if stock_df.empty:
                # 尝试使用模拟数据
                if MOCK_DATA_CONFIG["enabled"]:
                    logger.warning(f"未找到股票{code}的实时数据，使用模拟数据")
                    return success_response(get_mock_quote(code))
                return error_response(f"未找到股票: {code}")
            
            row = stock_df.iloc[0]
            
            quote_data = {
                "code": code,
                "name": row.get("名称", ""),
                "latest_price": float(row.get("最新价", 0)) if pd.notna(row.get("最新价")) else 0,
                "prev_close": float(row.get("昨收", 0)) if pd.notna(row.get("昨收")) else 0,
                "open": float(row.get("今开", 0)) if pd.notna(row.get("今开")) else 0,
                "high": float(row.get("最高", 0)) if pd.notna(row.get("最高")) else 0,
                "low": float(row.get("最低", 0)) if pd.notna(row.get("最低")) else 0,
                "change": float(row.get("涨跌额", 0)) if pd.notna(row.get("涨跌额")) else 0,
                "change_pct": float(row.get("涨跌幅", 0)) if pd.notna(row.get("涨跌幅")) else 0,
                "volume": int(row.get("成交量", 0)) if pd.notna(row.get("成交量")) else 0,
                "amount": float(row.get("成交额", 0)) if pd.notna(row.get("成交额")) else 0,
                "bid_price1": float(row.get("买一", 0)) if pd.notna(row.get("买一")) else 0,
                "bid_volume1": int(row.get("买一量", 0)) if pd.notna(row.get("买一量")) else 0,
                "bid_price2": float(row.get("买二", 0)) if pd.notna(row.get("买二")) else 0,
                "bid_volume2": int(row.get("买二量", 0)) if pd.notna(row.get("买二量")) else 0,
                "bid_price3": float(row.get("买三", 0)) if pd.notna(row.get("买三")) else 0,
                "bid_volume3": int(row.get("买三量", 0)) if pd.notna(row.get("买三量")) else 0,
                "ask_price1": float(row.get("卖一", 0)) if pd.notna(row.get("卖一")) else 0,
                "ask_volume1": int(row.get("卖一量", 0)) if pd.notna(row.get("卖一量")) else 0,
                "ask_price2": float(row.get("卖二", 0)) if pd.notna(row.get("卖二")) else 0,
                "ask_volume2": int(row.get("卖二量", 0)) if pd.notna(row.get("卖二量")) else 0,
                "ask_price3": float(row.get("卖三", 0)) if pd.notna(row.get("卖三")) else 0,
                "ask_volume3": int(row.get("卖三量", 0)) if pd.notna(row.get("卖三量")) else 0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return success_response(quote_data)
            
        except Exception as e:
            logger.error(f"AkShare获取实时行情失败: {e}")
            
            # 降级使用模拟数据
            if MOCK_DATA_CONFIG["enabled"]:
                return success_response(get_mock_quote(code))
            return error_response(f"获取实时行情失败: {str(e)}")
    
    except Exception as e:
        logger.error(f"获取实时行情异常: {e}")
        return error_response(f"获取实时行情异常: {str(e)}")


@router.get("/quote/changes")
def get_stock_changes(
    top: int = Query(50, ge=1, le=100, description="返回条数，默认50"),
    direction: str = Query("all", regex="^(all|up|down)$", description="筛选方向: all=全部 up=上涨 down=下跌")
):
    """
    获取实时涨跌榜
    
    返回股票涨跌幅排名
    
    Args:
        top: 返回条数 (1-100)
        direction: 筛选方向 (all/up/down)
        
    Returns:
        dict: 统一响应格式，包含涨跌榜数据
    """
    logger.info(f"获取涨跌榜: top={top}, direction={direction}")
    
    try:
        try:
            # 从 AkShare 获取涨跌榜
            df = ak.stock_changes_em()
            
            if df is None or df.empty:
                if MOCK_DATA_CONFIG["enabled"]:
                    return success_response(get_mock_changes(top))
                return error_response("获取涨跌榜数据失败")
            
            # 解析数据
            changes = []
            for _, row in df.head(top * 2).iterrows():  # 多获取一些数据以便筛选
                try:
                    code = str(row.get("代码", ""))
                    name = str(row.get("名称", ""))
                    if not code or code == "None":
                        continue
                    
                    change_pct = float(row.get("涨跌幅", 0)) if pd.notna(row.get("涨跌幅")) else 0
                    
                    # 根据方向筛选
                    if direction == "up" and change_pct <= 0:
                        continue
                    if direction == "down" and change_pct >= 0:
                        continue
                    
                    changes.append({
                        "code": code,
                        "name": name,
                        "latest_price": float(row.get("最新价", 0)) if pd.notna(row.get("最新价")) else 0,
                        "change": float(row.get("涨跌额", 0)) if pd.notna(row.get("涨跌额")) else 0,
                        "change_pct": change_pct,
                        "volume": int(row.get("成交量", 0)) if pd.notna(row.get("成交量")) else 0,
                        "amount": float(row.get("成交额", 0)) if pd.notna(row.get("成交额")) else 0,
                        "turnover": float(row.get("换手率", 0)) if pd.notna(row.get("换手率")) else 0
                    })
                except Exception:
                    continue
                
                if len(changes) >= top:
                    break
            
            # 按涨跌幅排序
            changes.sort(key=lambda x: x["change_pct"], reverse=True)
            changes = changes[:top]
            
            return success_response(changes)
            
        except Exception as e:
            logger.error(f"AkShare获取涨跌榜失败: {e}")
            
            # 降级使用模拟数据
            if MOCK_DATA_CONFIG["enabled"]:
                return success_response(get_mock_changes(top))
            return error_response(f"获取涨跌榜失败: {str(e)}")
    
    except Exception as e:
        logger.error(f"获取涨跌榜异常: {e}")
        return error_response(f"获取涨跌榜异常: {str(e)}")


@router.get("/{code}/transactions")
def get_stock_transactions(
    code: str,
    limit: int = Query(50, ge=1, le=200, description="返回条数，默认50")
):
    """
    获取实时成交明细
    
    返回股票逐笔成交数据
    
    Args:
        code: 股票代码 (如: 600519)
        limit: 返回条数 (1-200)
        
    Returns:
        dict: 统一响应格式，包含成交明细列表
    """
    logger.info(f"获取成交明细: {code}, limit={limit}")
    
    # 验证股票代码
    if not code or len(code) != 6:
        return error_response("股票代码格式错误，应为6位数字")
    
    try:
        try:
            # 确定市场
            if code.startswith("6"):
                symbol = f"sh{code}"
            else:
                symbol = f"sz{code}"
            
            # 从 AkShare 获取逐笔成交
            df = ak.stock_zh_a_tick_tx_js(symbol=symbol, limit=limit)
            
            if df is None or df.empty:
                if MOCK_DATA_CONFIG["enabled"]:
                    return success_response(get_mock_transactions(code, limit))
                return error_response(f"未找到股票{code}的成交明细")
            
            # 解析数据
            transactions = []
            for _, row in df.iterrows():
                try:
                    # 判断买卖方向
                    price_change = row.get("价格", 0)
                    volume = int(row.get("成交量", 0))
                    
                    # 根据价格变化判断买卖方向
                    direction = "买入" if price_change > 0 else "卖出" if price_change < 0 else "中性"
                    
                    transactions.append({
                        "time": str(row.get("时间", "")),
                        "price": float(row.get("价格", 0)) if pd.notna(row.get("价格")) else 0,
                        "volume": volume,
                        "amount": float(row.get("成交额", 0)) if pd.notna(row.get("成交额")) else 0,
                        "type": direction
                    })
                except Exception:
                    continue
            
            return success_response(transactions)
            
        except Exception as e:
            logger.error(f"AkShare获取成交明细失败: {e}")
            
            # 降级使用模拟数据
            if MOCK_DATA_CONFIG["enabled"]:
                return success_response(get_mock_transactions(code, limit))
            return error_response(f"获取成交明细失败: {str(e)}")
    
    except Exception as e:
        logger.error(f"获取成交明细异常: {e}")
        return error_response(f"获取成交明细异常: {str(e)}")
