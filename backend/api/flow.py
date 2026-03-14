# 资金流向API路由
"""
资金流向数据接口

提供主力资金流向、单日资金流向等功能
使用 AkShare 获取真实数据
"""

from fastapi import APIRouter, HTTPException
import akshare as ak
import pandas as pd
from datetime import datetime
from models.response import success_response, error_response
from utils.logger import logger

# 创建路由
router = APIRouter(prefix="/api/flow", tags=["资金流向"])


def get_stock_market(code: str) -> str:
    """
    根据股票代码判断市场
    
    Args:
        code: 股票代码
        
    Returns:
        str: 'sh' 或 'sz'
    """
    if code.startswith("6"):
        return "sh"
    else:
        return "sz"


def get_real_main_flow(code: str) -> dict:
    """
    获取真实的主力资金流向数据 (使用 AkShare)
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 主力资金流向数据
    """
    market = get_stock_market(code)
    
    try:
        # 从 AkShare 获取个股资金流向数据
        df = ak.stock_individual_fund_flow(stock=code, market=market)
        
        if df is None or df.empty:
            raise ValueError("未获取到资金流向数据")
        
        # 获取最新一天的数据
        # 列名映射（通过位置索引）:
        # 0: 日期, 1: 收盘价, 2: 涨跌幅, 3: 主力净流入-净额, 4: 主力净流入-净占比
        # 5: 超大单净流入-净额, 6: 超大单净流入-净占比
        # 7: 大单净流入-净额, 8: 大单净流入-净占比
        # 9: 中单净流入-净额, 10: 中单净流入-净占比
        # 11: 小单净流入-净额, 12: 小单净流入-净占比
        
        latest_row = df.iloc[0]  # 最新数据
        
        # 解析主力资金数据
        net_inflow = float(latest_row.iloc[3]) if pd.notna(latest_row.iloc[3]) else 0  # 主力净流入(万元)
        net_inflow_rate = float(latest_row.iloc[4]) / 100 if pd.notna(latest_row.iloc[4]) else 0  # 净占比转百分比
        
        # 解析各档位数据
        super_net = float(latest_row.iloc[5]) if pd.notna(latest_row.iloc[5]) else 0  # 超大单
        large_net = float(latest_row.iloc[7]) if pd.notna(latest_row.iloc[7]) else 0  # 大单
        medium_net = float(latest_row.iloc[9]) if pd.notna(latest_row.iloc[9]) else 0  # 中单
        small_net = float(latest_row.iloc[11]) if pd.notna(latest_row.iloc[11]) else 0  # 小单
        
        # 获取收盘价和涨跌幅
        close_price = float(latest_row.iloc[1]) if pd.notna(latest_row.iloc[1]) else 0
        change_pct = float(latest_row.iloc[2]) if pd.notna(latest_row.iloc[2]) else 0
        
        return {
            "code": code,
            "date": str(latest_row.iloc[0]),
            "close_price": round(close_price, 2),
            "change_pct": round(change_pct, 2),
            "net_inflow": round(net_inflow, 2),  # 主力净流入(万元)
            "net_inflow_rate": round(net_inflow_rate, 4),  # 净流入率
            "super_large": {
                "net_inflow": round(super_net, 2),
                "net_rate": round(float(latest_row.iloc[6]) / 100 if pd.notna(latest_row.iloc[6]) else 0, 4)
            },
            "large": {
                "net_inflow": round(large_net, 2),
                "net_rate": round(float(latest_row.iloc[8]) / 100 if pd.notna(latest_row.iloc[8]) else 0, 4)
            },
            "medium": {
                "net_inflow": round(medium_net, 2),
                "net_rate": round(float(latest_row.iloc[10]) / 100 if pd.notna(latest_row.iloc[10]) else 0, 4)
            },
            "small": {
                "net_inflow": round(small_net, 2),
                "net_rate": round(float(latest_row.iloc[12]) / 100 if pd.notna(latest_row.iloc[12]) else 0, 4)
            },
            "main_force_action": "买入" if net_inflow > 0 else "卖出",
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"获取真实资金流向数据失败: {e}")
        raise


def get_real_daily_flow(code: str, days: int = 5) -> dict:
    """
    获取真实的多日资金流向数据 (使用 AkShare)
    
    Args:
        code: 股票代码
        days: 查询天数
        
    Returns:
        dict: 多日资金流向数据
    """
    market = get_stock_market(code)
    
    try:
        # 从 AkShare 获取个股资金流向数据
        df = ak.stock_individual_fund_flow(stock=code, market=market)
        
        if df is None or df.empty:
            raise ValueError("未获取到资金流向数据")
        
        # 限制返回天数
        limit = min(days, len(df))
        df = df.head(limit)
        
        daily_data = []
        total_main_inflow = 0
        total_retail_inflow = 0
        
        for idx, row in df.iterrows():
            # 主力净流入 = 超大单 + 大单
            main_net = (float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0) + \
                      (float(row.iloc[7]) if pd.notna(row.iloc[7]) else 0)
            # 散户净流入 = 中单 + 小单
            retail_net = (float(row.iloc[9]) if pd.notna(row.iloc[9]) else 0) + \
                        (float(row.iloc[11]) if pd.notna(row.iloc[11]) else 0)
            
            daily_data.append({
                "date": str(row.iloc[0]),
                "main_net_inflow": round(main_net, 2),
                "retail_net_inflow": round(retail_net, 2),
                "total_net_inflow": round(main_net + retail_net, 2),
                "main_inflow_rate": round(float(row.iloc[4]) / 100 if pd.notna(row.iloc[4]) else 0, 4)
            })
            
            total_main_inflow += main_net
            total_retail_inflow += retail_net
        
        return {
            "code": code,
            "days": limit,
            "data": daily_data,
            "summary": {
                "total_main_inflow": round(total_main_inflow, 2),
                "total_retail_inflow": round(total_retail_inflow, 2),
                "avg_main_inflow": round(total_main_inflow / limit, 2),
                "avg_retail_inflow": round(total_retail_inflow / limit, 2)
            },
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"获取真实多日资金流向数据失败: {e}")
        raise


@router.get("/{code}/main")
async def get_main_flow(code: str):
    """
    获取主力资金流向
    
    参数:
        code: 股票代码 (如: 000001)
    
    返回: 主力资金净流入/流出数据
    数据来源: AkShare - stock_individual_fund_flow
    """
    logger.info(f"获取主力资金流向: {code}")
    
    # 验证股票代码格式
    if not code or len(code) != 6:
        return error_response("无效的股票代码")
    
    try:
        # 获取真实数据
        data = get_real_main_flow(code)
        return success_response(data)
    except Exception as e:
        logger.error(f"获取主力资金流向数据失败: {e}")
        return {
            "code": 1,
            "message": "资金流向数据获取失败",
            "error": "data_fetch_failed"
        }


@router.get("/{code}/daily")
async def get_daily_flow(code: str, days: int = 5):
    """
    获取单日资金流向
    
    参数:
        code: 股票代码 (如: 000001)
        days: 查询天数 (默认5天，最大30天)
    
    返回: 单日资金流向数据
    数据来源: AkShare - stock_individual_fund_flow
    """
    logger.info(f"获取单日资金流向: {code}, 天数: {days}")
    
    # 验证股票代码格式
    if not code or len(code) != 6:
        return error_response("无效的股票代码")
    
    # 限制天数范围
    if days < 1:
        days = 1
    elif days > 30:
        days = 30
    
    try:
        # 获取真实数据
        data = get_real_daily_flow(code, days)
        return success_response(data)
    except Exception as e:
        logger.error(f"获取单日资金流向数据失败: {e}")
        return {
            "code": 1,
            "message": "资金流向数据获取失败",
            "error": "data_fetch_failed"
        }
