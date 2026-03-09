# 市场分析API路由
"""
市场分析数据接口

提供大盘指数、涨跌统计、行业板块、概念板块等功能
使用 AkShare 获取市场数据
"""

from fastapi import APIRouter, HTTPException
import akshare as ak
import pandas as pd
from datetime import datetime
from models.response import success_response, error_response
from utils.logger import logger

# 创建路由
router = APIRouter(prefix="/api/market", tags=["市场分析"])


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


@router.get("/overview")
async def get_market_overview():
    """
    获取市场概览
    
    返回: 大盘指数、涨跌统计
    """
    indices_data = []
    up_count = down_count = flat_count = total_count = 0
    
    try:
        # 获取A股实时行情
        df = ak.stock_zh_index_spot_em(symbol="上证系列指数")
        
        # 筛选主要指数
        major_indices = ['上证指数', '深证成指', '创业板指', '科创50', '上证50', '沪深300', '中证500', '中证1000']
        
        for _, row in df.iterrows():
            if row.get('名称') in major_indices:
                indices_data.append({
                    "code": row.get('代码'),
                    "name": row.get('名称'),
                    "latest_price": parse_float(row.get('最新价')),
                    "change": parse_float(row.get('涨跌幅')),
                    "change_amount": parse_float(row.get('涨跌额')),
                    "volume": parse_float(row.get('成交量')),
                    "amount": parse_float(row.get('成交额')),
                    "open": parse_float(row.get('开盘')),
                    "high": parse_float(row.get('最高')),
                    "low": parse_float(row.get('最低')),
                    "prev_close": parse_float(row.get('昨收')),
                })
    except Exception as e:
        logger.warning(f"获取大盘指数失败: {e}")
    
    try:
        # 获取涨跌统计
        df_sh = ak.stock_sh_a_spot_em()
        if df_sh is not None and len(df_sh) > 0:
            up_count = len(df_sh[df_sh['涨跌幅'] > 0])
            down_count = len(df_sh[df_sh['涨跌幅'] < 0])
            flat_count = len(df_sh[df_sh['涨跌幅'] == 0])
            total_count = len(df_sh)
    except Exception as e:
        logger.warning(f"获取涨跌统计失败: {e}")
    
    return success_response({
        "indices": indices_data,
        "statistics": {
            "up_count": up_count,
            "down_count": down_count,
            "flat_count": flat_count,
            "total_count": total_count,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    })


@router.get("/sectors")
async def get_sectors():
    """
    获取行业板块
    
    返回: 行业板块涨跌数据
    """
    sectors_data = []
    
    try:
        # 获取行业板块行情
        df = ak.stock_board_industry_spot_em()
        
        for _, row in df.iterrows():
            sectors_data.append({
                "code": row.get('板块代码'),
                "name": row.get('板块名称'),
                "latest_price": parse_float(row.get('最新价')),
                "change_pct": parse_float(row.get('涨跌幅')),
                "change_amount": parse_float(row.get('涨跌额')),
                "volume": parse_float(row.get('成交量')),
                "amount": parse_float(row.get('成交额')),
                "turnover_rate": parse_float(row.get('换手率')),
                "rise_count": parse_int(row.get('上涨')),
                "fall_count": parse_int(row.get('下跌')),
                "lead_stock": str(row.get('领涨股票', '')),
                "lead_stock_change": parse_float(row.get('领涨股票-涨跌幅')),
            })
        
        # 按涨跌幅排序
        sectors_data = sorted(sectors_data, key=lambda x: x['change_pct'], reverse=True)
        
    except Exception as e:
        logger.warning(f"获取行业板块失败: {e}")
    
    return success_response({
        "sectors": sectors_data,
        "total": len(sectors_data),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@router.get("/concepts")
async def get_concepts():
    """
    获取概念板块
    
    返回: 概念板块涨跌数据
    """
    concepts_data = []
    
    try:
        # 获取概念板块行情
        df = ak.stock_board_concept_spot_em()
        
        for _, row in df.iterrows():
            concepts_data.append({
                "code": row.get('板块代码'),
                "name": row.get('板块名称'),
                "latest_price": parse_float(row.get('最新价')),
                "change_pct": parse_float(row.get('涨跌幅')),
                "change_amount": parse_float(row.get('涨跌额')),
                "volume": parse_float(row.get('成交量')),
                "amount": parse_float(row.get('成交额')),
                "turnover_rate": parse_float(row.get('换手率')),
                "rise_count": parse_int(row.get('上涨')),
                "fall_count": parse_int(row.get('下跌')),
                "lead_stock": str(row.get('领涨股票', '')),
                "lead_stock_change": parse_float(row.get('领涨股票-涨跌幅')),
            })
        
        # 按涨跌幅排序
        concepts_data = sorted(concepts_data, key=lambda x: x['change_pct'], reverse=True)
        
    except Exception as e:
        logger.warning(f"获取概念板块失败: {e}")
    
    return success_response({
        "concepts": concepts_data,
        "total": len(concepts_data),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
