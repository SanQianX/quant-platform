# 财务数据 API
"""
财务数据接口
使用 AkShare 获取财务报表数据
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
import akshare as ak
from datetime import datetime

router = APIRouter(prefix="/api/stock", tags=["财务数据"])

@router.get("/{code}/financial/balance")
def get_balance_sheet(
    code: str = Path(..., description="股票代码"),
    year: Optional[int] = Query(None, description="年份，如2024"),
    quarter: Optional[int] = Query(None, description="季度: 1, 2, 3, 4")
):
    """
    获取资产负债表
    
    Args:
        code: 股票代码
        year: 年份
        quarter: 季度
        
    Returns:
        资产负债表数据
    """
    try:
        # 转换股票代码格式
        symbol = f"{code}"
        
        # 使用 AkShare 获取资产负债表
        df = ak.stock_balancesheet_a(symbol=symbol, year=year, quarter=quarter)
        
        if df is None or df.empty:
            return {"code": 0, "data": [], "message": "暂无数据"}
        
        # 转换为字典列表
        data = df.to_dict(orient="records")
        
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
    
    Args:
        code: 股票代码
        year: 年份
        quarter: 季度
        
    Returns:
        利润表数据
    """
    try:
        symbol = f"{code}"
        
        df = ak.stock_income_a(symbol=symbol, year=year, quarter=quarter)
        
        if df is None or df.empty:
            return {"code": 0, "data": [], "message": "暂无数据"}
        
        data = df.to_dict(orient="records")
        
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
    
    Args:
        code: 股票代码
        year: 年份
        quarter: 季度
        
    Returns:
        现金流量表数据
    """
    try:
        symbol = f"{code}"
        
        df = ak.stock_cashflow_a(symbol=symbol, year=year, quarter=quarter)
        
        if df is None or df.empty:
            return {"code": 0, "data": [], "message": "暂无数据"}
        
        data = df.to_dict(orient="records")
        
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
    
    Args:
        code: 股票代码
        year: 年份
        quarter: 季度
        
    Returns:
        财务指标数据
    """
    try:
        symbol = f"{code}"
        
        df = ak.stock_financial_abstract_a(symbol=symbol, year=year, quarter=quarter)
        
        if df is None or df.empty:
            return {"code": 0, "data": [], "message": "暂无数据"}
        
        data = df.to_dict(orient="records")
        
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
    
    Args:
        code: 股票代码
        year: 年份
        quarter: 季度
        
    Returns:
        所有财务数据
    """
    result = {
        "stock_code": code,
        "year": year,
        "quarter": quarter,
        "balance": [],
        "income": [],
        "cashflow": [],
        "indicator": []
    }
    
    # 获取资产负债表
    try:
        df = ak.stock_balancesheet_a(symbol=f"{code}", year=year, quarter=quarter)
        if df is not None and not df.empty:
            result["balance"] = df.to_dict(orient="records")[:10]
    except:
        pass
    
    # 获取利润表
    try:
        df = ak.stock_income_a(symbol=f"{code}", year=year, quarter=quarter)
        if df is not None and not df.empty:
            result["income"] = df.to_dict(orient="records")[:10]
    except:
        pass
    
    # 获取现金流量表
    try:
        df = ak.stock_cashflow_a(symbol=f"{code}", year=year, quarter=quarter)
        if df is not None and not df.empty:
            result["cashflow"] = df.to_dict(orient="records")[:10]
    except:
        pass
    
    # 获取财务指标
    try:
        df = ak.stock_financial_abstract_a(symbol=f"{code}", year=year, quarter=quarter)
        if df is not None and not df.empty:
            result["indicator"] = df.to_dict(orient="records")[:10]
    except:
        pass
    
    return {"code": 0, "data": result}
