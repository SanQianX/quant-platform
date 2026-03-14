# 股票所属板块API路由
"""
股票所属板块数据接口

提供股票所属板块查询功能、板块列表、板块成分股等功能
使用 AkShare 获取真实数据
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import akshare as ak
import pandas as pd
from models.response import success_response, error_response
from utils.logger import logger

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票所属板块"])

# 板块缓存
_industry_list_cache = None
_industry_list_cache_time = None


def get_industry_list() -> List[dict]:
    """
    获取板块列表（使用 AkShare）
    
    Returns:
        List[dict]: 板块列表
    """
    global _industry_list_cache, _industry_list_cache_time
    
    from datetime import datetime, timedelta
    
    # 缓存1小时
    if _industry_list_cache is not None and _industry_list_cache_time is not None:
        if (datetime.now() - _industry_list_cache_time).total_seconds() < 3600:
            return _industry_list_cache
    
    try:
        df = ak.stock_board_industry_name_em()
        
        if df is None or df.empty:
            raise ValueError("未获取到板块数据")
        
        # 列名: 序号, 板块名称, 板块代码, 总市值, 换手率, 上涨家数, 下跌家数, 
        #       领涨股票, 领涨股票-涨跌幅, 涨跌
        industries = []
        for _, row in df.iterrows():
            industries.append({
                "name": str(row.iloc[1]),  # 板块名称
                "code": str(row.iloc[2]),  # 板块代码
                "total_market_value": float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0,
                "turnover_rate": float(row.iloc[4]) if pd.notna(row.iloc[4]) else 0,
                "up_count": int(row.iloc[5]) if pd.notna(row.iloc[5]) else 0,
                "down_count": int(row.iloc[6]) if pd.notna(row.iloc[6]) else 0,
                "leader_stock": str(row.iloc[7]) if pd.notna(row.iloc[7]) else "",
                "leader_change_pct": float(row.iloc[8]) if pd.notna(row.iloc[8]) else 0
            })
        
        _industry_list_cache = industries
        _industry_list_cache_time = datetime.now()
        
        return industries
        
    except Exception as e:
        logger.error(f"获取板块列表失败: {e}")
        raise


def get_industry_stocks(industry_name: str) -> List[dict]:
    """
    获取板块成分股（使用 AkShare）
    
    Args:
        industry_name: 板块名称
        
    Returns:
        List[dict]: 板块成分股列表
    """
    try:
        df = ak.stock_board_industry_cons_em(symbol=industry_name)
        
        if df is None or df.empty:
            raise ValueError(f"未获取到板块 {industry_name} 的成分股数据")
        
        # 列名: 序号, 代码, 名称, 涨跌幅, 涨跌, 成交价, 成交额, 成交量,
        #       今开, 最高, 最低, 昨收, 量比, 换手率, 振幅
        stocks = []
        for _, row in df.iterrows():
            stocks.append({
                "code": str(row.iloc[1]),  # 代码
                "name": str(row.iloc[2]),  # 名称
                "change_pct": float(row.iloc[3]) if pd.notna(row.iloc[3]) else 0,
                "change": float(row.iloc[4]) if pd.notna(row.iloc[4]) else 0,
                "price": float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0,
                "amount": float(row.iloc[6]) if pd.notna(row.iloc[6]) else 0,
                "volume": float(row.iloc[7]) if pd.notna(row.iloc[7]) else 0,
                "open": float(row.iloc[8]) if pd.notna(row.iloc[8]) else 0,
                "high": float(row.iloc[9]) if pd.notna(row.iloc[9]) else 0,
                "low": float(row.iloc[10]) if pd.notna(row.iloc[10]) else 0,
                "prev_close": float(row.iloc[11]) if pd.notna(row.iloc[11]) else 0,
                "volume_ratio": float(row.iloc[12]) if pd.notna(row.iloc[12]) else 0,
                "turnover_rate": float(row.iloc[13]) if pd.notna(row.iloc[13]) else 0,
                "amplitude": float(row.iloc[14]) if pd.notna(row.iloc[14]) else 0
            })
        
        return stocks
        
    except Exception as e:
        logger.error(f"获取板块成分股失败: {e}")
        raise


def get_stock_industry_info(code: str) -> dict:
    """
    获取股票所属板块信息（通过查询板块成分股）
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 股票所属板块信息
    """
    try:
        # 获取所有板块列表
        industries = get_industry_list()
        
        # 遍历板块，查找股票所属板块
        for industry in industries:
            try:
                stocks = get_industry_stocks(industry["name"])
                for stock in stocks:
                    if stock["code"] == code:
                        return {
                            "code": code,
                            "name": stock["name"],
                            "industry": industry["name"],
                            "industry_code": industry["code"],
                            "sector": industry["name"],  # 板块名作为行业分类
                            "change_pct": stock["change_pct"],
                            "price": stock["price"]
                        }
            except:
                continue
        
        # 如果遍历完所有板块都没找到，返回空
        raise ValueError(f"未找到股票 {code} 的所属板块")
        
    except Exception as e:
        logger.error(f"获取股票所属板块信息失败: {e}")
        raise


@router.get("/{code}/industry")
def get_stock_industry(code: str):
    """
    获取股票所属板块
    
    获取指定股票代码的所属板块信息
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含股票所属板块信息
    数据来源: AkShare - stock_board_industry_name_em + stock_board_industry_cons_em
    """
    logger.info(f"获取股票所属板块: {code}")
    
    # 验证股票代码格式
    if not code or len(code) != 6:
        return error_response("无效的股票代码")
    
    try:
        # 获取真实数据
        industry_data = get_stock_industry_info(code)
        return success_response(industry_data)
    except Exception as e:
        logger.error(f"获取股票所属板块失败: {e}")
        return {
            "code": 1,
            "message": "板块数据获取失败",
            "error": "data_fetch_failed"
        }


@router.get("/industry/list")
def get_industry_list_api():
    """
    获取板块列表
    
    返回所有行业板块的列表信息
    
    Returns:
        dict: 统一响应格式，包含板块列表
    数据来源: AkShare - stock_board_industry_name_em
    """
    logger.info("获取板块列表")
    
    try:
        industries = get_industry_list()
        return success_response(industries)
    except Exception as e:
        logger.error(f"获取板块列表失败: {e}")
        return {
            "code": 1,
            "message": "板块数据获取失败",
            "error": "data_fetch_failed"
        }


@router.get("/industry/{industry_name}/stocks")
def get_industry_stocks_api(industry_name: str):
    """
    获取板块成分股
    
    获取指定板块的成分股列表
    
    Args:
        industry_name: 板块名称（如: 银行、房地产、医药等）
        
    Returns:
        dict: 统一响应格式，包含板块成分股列表
    数据来源: AkShare - stock_board_industry_cons_em
    """
    logger.info(f"获取板块成分股: {industry_name}")
    
    if not industry_name:
        return error_response("板块名称不能为空")
    
    try:
        stocks = get_industry_stocks(industry_name)
        return success_response({
            "industry": industry_name,
            "count": len(stocks),
            "stocks": stocks
        })
    except Exception as e:
        logger.error(f"获取板块成分股失败: {e}")
        return {
            "code": 1,
            "message": "板块数据获取失败",
            "error": "data_fetch_failed"
        }
