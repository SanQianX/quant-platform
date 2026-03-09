# 财务数据 API
"""
财务数据接口
使用 AkShare 获取财务报表数据
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
import akshare as ak
from datetime import datetime
import math
import json

router = APIRouter(prefix="/api/stock", tags=["财务数据"])

def clean_data(data):
    """清理数据中的NaN和Inf值"""
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data(item) for item in data]
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return None
        return data
    elif isinstance(data, (int, str)):
        return data
    else:
        return data

@router.get("/{code}/financial/balance")
def get_balance_sheet(
    code: str = Path(..., description="股票代码"),
    year: Optional[int] = Query(None, description="年份，如2024"),
    quarter: Optional[int] = Query(None, description="季度: 1, 2, 3, 4")
):
    """
    获取资产负债表
    """
    try:
        # 转换股票代码格式，添加市场后缀
        if len(code) == 6:
            if code.startswith(('6', '9')):
                symbol = f"{code}.SH"
            else:
                symbol = f"{code}.SZ"
        else:
            symbol = code
        
        # 使用东方财富资产负债表接口
        df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
        
        # 检查返回值类型
        if df is None:
            return {"code": 0, "data": [], "message": "暂无数据"}
        
        # 如果返回的是字典，尝试提取数据
        if isinstance(df, dict):
            if 'data' in df:
                df = df['data']
            if df is None or (hasattr(df, 'empty') and df.empty):
                return {"code": 0, "data": [], "message": "暂无数据"}
        
        if hasattr(df, 'empty') and df.empty:
            return {"code": 0, "data": [], "message": "暂无数据"}
        
        # 转换为字典列表
        data = df.head(20).to_dict(orient="records")
        data = clean_data(data)
        
        return {"code": 0, "data": data}
        
    except Exception as e:
        return {"code": -1, "message": f"获取资产负债表失败: {str(e)}", "data": []}


@router.get("/{code}/financial/income")
def get_income_statement(
    code: str = Path(..., description="股票代码"),
    year: Optional[int] = Query(None, description="年份，如2024"),
    quarter: Optional[int] = Query(None, description="季度: 1, 2, 3, 4")
):
    """
    获取利润表
    """
    try:
        # 转换股票代码格式，添加市场后缀
        if len(code) == 6:
            if code.startswith(('6', '9')):
                symbol = f"{code}.SH"
            else:
                symbol = f"{code}.SZ"
        else:
            symbol = code
        
        # 使用利润表接口
        df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
        
        # 检查返回值类型
        if df is None:
            return {"code": 0, "data": [], "message": "暂无数据"}
        
        # 如果返回的是字典，尝试提取数据
        if isinstance(df, dict):
            if 'data' in df:
                df = df['data']
            if df is None or (hasattr(df, 'empty') and df.empty):
                return {"code": 0, "data": [], "message": "暂无数据"}
        
        if hasattr(df, 'empty') and df.empty:
            return {"code": 0, "data": [], "message": "暂无数据"}
        
        data = df.head(20).to_dict(orient="records")
        data = clean_data(data)
        
        return {"code": 0, "data": data}
        
    except Exception as e:
        return {"code": -1, "message": f"获取利润表失败: {str(e)}", "data": []}


@router.get("/{code}/financial/cashflow")
def get_cashflow_statement(
    code: str = Path(..., description="股票代码"),
    year: Optional[int] = Query(None, description="年份，如2024"),
    quarter: Optional[int] = Query(None, description="季度: 1, 2, 3, 4")
):
    """
    获取现金流量表
    """
    try:
        symbol = f"{code}"
        
        # 使用现金流量表接口
        df = ak.stock_financial_cash_ths(symbol=symbol)
        
        if df is None or df.empty:
            return {"code": 0, "data": [], "message": "暂无数据"}
        
        data = df.head(20).to_dict(orient="records")
        data = clean_data(data)
        
        return {"code": 0, "data": data}
        
    except Exception as e:
        return {"code": -1, "message": f"获取现金流量表失败: {str(e)}", "data": []}


@router.get("/{code}/financial/indicator")
def get_financial_indicator(
    code: str = Path(..., description="股票代码"),
    year: Optional[int] = Query(None, description="年份，如2024"),
    quarter: Optional[int] = Query(None, description="季度: 1, 2, 3, 4")
):
    """
    获取财务指标
    """
    try:
        # 转换股票代码格式，添加市场后缀
        if len(code) == 6:
            if code.startswith(('6', '9')):
                symbol = f"{code}.SH"
            else:
                symbol = f"{code}.SZ"
        else:
            symbol = code
        
        # 使用财务分析指标接口
        df = ak.stock_financial_analysis_indicator_em(symbol=symbol)
        
        # 检查返回值类型
        if df is None:
            return {"code": 0, "data": [], "message": "暂无数据"}
        
        # 如果返回的是字典，尝试提取数据
        if isinstance(df, dict):
            if 'data' in df:
                df = df['data']
            if df is None or (hasattr(df, 'empty') and df.empty):
                return {"code": 0, "data": [], "message": "暂无数据"}
        
        if hasattr(df, 'empty') and df.empty:
            return {"code": 0, "data": [], "message": "暂无数据"}
        
        data = df.head(20).to_dict(orient="records")
        data = clean_data(data)
        
        return {"code": 0, "data": data}
        
    except Exception as e:
        return {"code": -1, "message": f"获取财务指标失败: {str(e)}", "data": []}


@router.get("/{code}/financial/all")
def get_all_financial_data(
    code: str = Path(..., description="股票代码"),
    year: Optional[int] = Query(2024, description="年份"),
    quarter: Optional[int] = Query(4, description="季度")
):
    """
    获取所有财务数据
    """
    result = {
        "stock_code": code,
        "balance": [],
        "income": [],
        "cashflow": [],
        "indicator": []
    }
    
    # 资产负债表
    try:
        df = ak.stock_balance_sheet_by_report_em(symbol=f"{code}")
        if df is not None and not df.empty:
            result["balance"] = df.head(10).to_dict(orient="records")
    except:
        pass
    
    # 利润表
    try:
        df = ak.stock_financial_abstract(symbol=f"{code}", indicator="按报告期")
        if df is not None and not df.empty:
            result["income"] = df.head(10).to_dict(orient="records")
    except:
        pass
    
    # 现金流量表
    try:
        df = ak.stock_financial_cash_ths(symbol=f"{code}")
        if df is not None and not df.empty:
            result["cashflow"] = df.head(10).to_dict(orient="records")
    except:
        pass
    
    # 财务指标
    try:
        df = ak.stock_financial_analysis_indicator_em(symbol=f"{code}")
        if df is not None and not df.empty:
            result["indicator"] = df.head(10).to_dict(orient="records")
    except:
        pass
    
    return {"code": 0, "data": result}
