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
        # 从 AkShare 获取K线数据
        df = ak.stock_zh_a_hist(
            symbol=code,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        
        if df is None or df.empty:
            logger.error(f"未找到股票{code}的K线数据")
            return error_response(f"未找到股票{code}的K线数据，请检查股票代码是否正确")
        
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
            except Exception as e:
                logger.warning(f"解析K线数据行失败: {e}")
                continue
        
        if not kline_data:
            return error_response(f"股票{code}的K线数据解析失败")
        
        return success_response(kline_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取K线数据失败: {e}")
        return error_response(f"获取K线数据失败: {str(e)}")


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
            logger.error(f"未找到股票{code}的分时数据")
            return error_response(f"未找到股票{code}的分时数据，请检查股票代码是否正确")
        
        # 解析数据
        intraday_data = []
        for idx, row in df.iterrows():
            try:
                # 时间可能是index或者某个列
                time_val = str(idx) if idx is not None else ""
                if not time_val or time_val == "0":
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
            except Exception as e:
                logger.warning(f"解析分时数据行失败: {e}")
                continue
        
        if not intraday_data:
            return error_response(f"股票{code}的分时数据解析失败")
        
        return success_response(intraday_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分时数据失败: {e}")
        return error_response(f"获取分时数据失败: {str(e)}")


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
        # 从 AkShare 获取日K线数据 (等同于日周期的K线)
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        
        if df is None or df.empty:
            logger.error(f"未找到股票{code}的日K线数据")
            return error_response(f"未找到股票{code}的日K线数据，请检查股票代码是否正确")
        
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
            except Exception as e:
                logger.warning(f"解析日K线数据行失败: {e}")
                continue
        
        if not daily_data:
            return error_response(f"股票{code}的日K线数据解析失败")
        
        return success_response(daily_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取日K线数据失败: {e}")
        return error_response(f"获取日K线数据失败: {str(e)}")
