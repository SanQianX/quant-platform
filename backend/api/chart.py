# 可视化图表API路由
"""
K线图表数据接口

提供K线数据、分时图、日K线等功能
使用 AkShare 获取数据
"""

from fastapi import APIRouter, Query, HTTPException
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from models.response import success_response, error_response
from config import MOCK_DATA_CONFIG
from utils.logger import logger

# 创建路由
router = APIRouter(prefix="/api/chart", tags=["图表数据"])


def parse_float(value, default=0.0):
    """安全解析浮点数"""
    try:
        return float(value) if pd.notna(value) else default
    except:
        return default


def parse_int(value, default=0):
    """安全解析整数"""
    try:
        return int(value) if pd.notna(value) else default
    except:
        return default


def get_mock_kline_data(stock_code: str, period: str = "daily", limit: int = 100) -> list:
    """
    生成模拟K线数据
    
    Args:
        stock_code: 股票代码
        period: 周期 (daily/weekly/monthly)
        limit: 返回条数
        
    Returns:
        list: 模拟K线数据列表
    """
    import random
    seed = int(stock_code) if stock_code.isdigit() else hash(stock_code) % 10000
    random.seed(seed)
    
    base_price = 50.0
    kline_data = []
    
    # 确定每日波动
    for i in range(limit):
        date = datetime.now() - timedelta(days=limit - i)
        date_str = date.strftime("%Y-%m-%d")
        
        # 随机生成涨跌
        change_pct = random.uniform(-5, 5)
        open_price = base_price * (1 + random.uniform(-0.02, 0.02))
        close_price = open_price * (1 + change_pct / 100)
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.03))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.03))
        volume = random.randint(1000000, 50000000)
        
        kline_data.append({
            "date": date_str,
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume,
            "amount": round((open_price + close_price) * volume / 2, 2),
            "change_pct": round(change_pct, 2)
        })
        
        base_price = close_price
    
    return kline_data


def get_mock_intraday_data(stock_code: str) -> list:
    """
    生成模拟分时图数据
    
    Args:
        stock_code: 股票代码
        
    Returns:
        list: 模拟分时图数据列表
    """
    import random
    seed = int(stock_code) if stock_code.isdigit() else hash(stock_code) % 10000
    random.seed(seed)
    
    base_price = 50.0
    intraday_data = []
    
    # 生成当天的分时数据 (9:30 - 15:00)
    start_hour = 9
    start_minute = 30
    current_price = base_price
    
    # 每5分钟一个数据点
    for i in range(78):  # 4小时 = 240分钟, 240/5 = 48个点 + 30分钟 = 78个点
        if i < 33:  # 上午 9:30 - 11:30
            hour = 9 if i < 3 else 10 if i < 15 else 11
            minute = (i % 30) * 5 + 30 if hour == 9 else (i % 30) * 5
        else:  # 下午 13:00 - 15:00
            hour = 13 if i < 45 else 14
            minute = (i - 33) % 30 * 5
        
        time_str = f"{hour:02d}:{minute:02d}"
        
        # 随机波动
        change_pct = random.uniform(-0.5, 0.5)
        current_price = current_price * (1 + change_pct / 100)
        
        volume = random.randint(10000, 500000)
        
        intraday_data.append({
            "time": time_str,
            "price": round(current_price, 2),
            "volume": volume,
            "amount": round(current_price * volume, 2),
            "change_pct": round(change_pct, 2)
        })
    
    return intraday_data


@router.get("/{code}/kline")
async def get_kline(
    code: str,
    period: str = Query("daily", regex="^(daily|weekly|monthly)$", description="周期: daily/weekly/monthly"),
    start_date: str = Query(None, description="开始日期 (YYYYMMDD)"),
    end_date: str = Query(None, description="结束日期 (YYYYMMDD)"),
    adjust: str = Query("qfq", regex="^(qfq|hfq|None)$", description="复权类型: qfq=前复权 hfq=后复权 None=不复权")
):
    """
    获取K线数据
    
    返回股票的K线数据，包含开盘价、收盘价、最高价、最低价、成交量等
    
    Args:
        code: 股票代码 (如: 600519)
        period: 周期 (daily=日K, weekly=周K, monthly=月K)
        start_date: 开始日期 (YYYYMMDD格式)
        end_date: 结束日期 (YYYYMMDD格式)
        adjust: 复权类型 (qfq=前复权, hfq=后复权, None=不复权)
        
    Returns:
        dict: 统一响应格式，包含K线数据列表
    """
    logger.info(f"获取K线数据: {code}, period={period}, adjust={adjust}")
    
    # 验证股票代码
    if not code or len(code) != 6:
        return error_response("股票代码格式错误，应为6位数字")
    
    # 设置默认日期范围
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
    
    try:
        try:
            # 从 AkShare 获取K线数据
            df = ak.stock_zh_a_hist(
                symbol=code,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if df is None or df.empty:
                if MOCK_DATA_CONFIG["enabled"]:
                    logger.warning(f"未找到股票{code}的K线数据，使用模拟数据")
                    return success_response(get_mock_kline_data(code, period))
                return error_response(f"未找到股票{code}的K线数据")
            
            # 解析数据
            kline_data = []
            for _, row in df.iterrows():
                try:
                    kline_data.append({
                        "date": str(row.get("日期", "")),
                        "open": parse_float(row.get("开盘")),
                        "high": parse_float(row.get("最高")),
                        "low": parse_float(row.get("最低")),
                        "close": parse_float(row.get("收盘")),
                        "volume": parse_int(row.get("成交量")),
                        "amount": parse_float(row.get("成交额")),
                        "change_pct": parse_float(row.get("涨跌幅"))
                    })
                except Exception:
                    continue
            
            return success_response(kline_data)
            
        except Exception as e:
            logger.error(f"AkShare获取K线数据失败: {e}")
            
            # 降级使用模拟数据
            if MOCK_DATA_CONFIG["enabled"]:
                return success_response(get_mock_kline_data(code, period))
            return error_response(f"获取K线数据失败: {str(e)}")
    
    except Exception as e:
        logger.error(f"获取K线数据异常: {e}")
        return error_response(f"获取K线数据异常: {str(e)}")


@router.get("/{code}/intraday")
async def get_intraday(
    code: str,
    period: str = Query("5", regex="^(1|5|15|30|60)$", description="周期: 1/5/15/30/60分钟")
):
    """
    获取分时图数据
    
    返回股票的分时图数据，包含时间、价格、成交量等
    
    Args:
        code: 股票代码 (如: 600519)
        period: 周期 (1=1分钟, 5=5分钟, 15=15分钟, 30=30分钟, 60=60分钟)
        
    Returns:
        dict: 统一响应格式，包含分时图数据列表
    """
    logger.info(f"获取分时图数据: {code}, period={period}")
    
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
            
            # 从 AkShare 获取分时数据
            df = ak.stock_zh_a_minute(
                symbol=symbol,
                period=period,
                adjust="qfq"
            )
            
            if df is None or df.empty:
                if MOCK_DATA_CONFIG["enabled"]:
                    logger.warning(f"未找到股票{code}的分时数据，使用模拟数据")
                    return success_response(get_mock_intraday_data(code))
                return error_response(f"未找到股票{code}的分时数据")
            
            # 解析数据
            intraday_data = []
            for idx, row in df.iterrows():
                try:
                    # 时间可能是index或者某个列
                    # 检查是否是index
                    time_val = str(idx) if idx is not None else ""
                    if not time_val or time_val == "0":
                        # 尝试从row获取
                        time_val = str(row.get("时间", "")) if "时间" in row.index else str(row.get("time", ""))
                    
                    # 检查是否有有效价格数据
                    price = 0.0
                    volume = 0
                    amount = 0.0
                    
                    # 尝试多种可能的列名
                    for col in ["收盘", "close", "Close", "价格", "price"]:
                        if col in row.index:
                            price = parse_float(row.get(col))
                            break
                    
                    for col in ["成交量", "volume", "Volume"]:
                        if col in row.index:
                            volume = parse_int(row.get(col))
                            break
                    
                    for col in ["成交额", "amount", "Amount"]:
                        if col in row.index:
                            amount = parse_float(row.get(col))
                            break
                    
                    if price > 0:
                        intraday_data.append({
                            "time": time_val,
                            "price": price,
                            "volume": volume,
                            "amount": amount,
                            "change_pct": 0.0
                        })
                except Exception:
                    continue
            
            # 如果解析后没有数据，使用模拟数据
            if not intraday_data and MOCK_DATA_CONFIG["enabled"]:
                return success_response(get_mock_intraday_data(code))
            
            return success_response(intraday_data)
            
        except Exception as e:
            logger.error(f"AkShare获取分时数据失败: {e}")
            
            # 降级使用模拟数据
            if MOCK_DATA_CONFIG["enabled"]:
                return success_response(get_mock_intraday_data(code))
            return error_response(f"获取分时数据失败: {str(e)}")
    
    except Exception as e:
        logger.error(f"获取分时数据异常: {e}")
        return error_response(f"获取分时数据异常: {str(e)}")


@router.get("/{code}/daily")
async def get_daily(
    code: str,
    start_date: str = Query(None, description="开始日期 (YYYYMMDD)"),
    end_date: str = Query(None, description="结束日期 (YYYYMMDD)"),
    adjust: str = Query("qfq", regex="^(qfq|hfq|None)$", description="复权类型: qfq=前复权 hfq=后复权 None=不复权")
):
    """
    获取日K线数据
    
    返回股票的日K线数据，包含开盘价、收盘价、最高价、最低价、成交量等
    
    Args:
        code: 股票代码 (如: 600519)
        start_date: 开始日期 (YYYYMMDD格式)
        end_date: 结束日期 (YYYYMMDD格式)
        adjust: 复权类型 (qfq=前复权, hfq=后复权, None=不复权)
        
    Returns:
        dict: 统一响应格式，包含日K线数据列表
    """
    logger.info(f"获取日K线数据: {code}, adjust={adjust}")
    
    # 验证股票代码
    if not code or len(code) != 6:
        return error_response("股票代码格式错误，应为6位数字")
    
    # 设置默认日期范围
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
    
    try:
        try:
            # 从 AkShare 获取日K线数据 (等同于日周期的K线)
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if df is None or df.empty:
                if MOCK_DATA_CONFIG["enabled"]:
                    logger.warning(f"未找到股票{code}的日K线数据，使用模拟数据")
                    return success_response(get_mock_kline_data(code, "daily"))
                return error_response(f"未找到股票{code}的日K线数据")
            
            # 解析数据
            daily_data = []
            for _, row in df.iterrows():
                try:
                    daily_data.append({
                        "date": str(row.get("日期", "")),
                        "open": parse_float(row.get("开盘")),
                        "high": parse_float(row.get("最高")),
                        "low": parse_float(row.get("最低")),
                        "close": parse_float(row.get("收盘")),
                        "volume": parse_int(row.get("成交量")),
                        "amount": parse_float(row.get("成交额")),
                        "change_pct": parse_float(row.get("涨跌幅"))
                    })
                except Exception:
                    continue
            
            return success_response(daily_data)
            
        except Exception as e:
            logger.error(f"AkShare获取日K线数据失败: {e}")
            
            # 降级使用模拟数据
            if MOCK_DATA_CONFIG["enabled"]:
                return success_response(get_mock_kline_data(code, "daily"))
            return error_response(f"获取日K线数据失败: {str(e)}")
    
    except Exception as e:
        logger.error(f"获取日K线数据异常: {e}")
        return error_response(f"获取日K线数据异常: {str(e)}")
