# 选股筛选 API
"""
股票筛选功能接口
支持多条件组合筛选
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from services.stock_filter import StockFilter, PRESET_FILTERS
from services.stock_service import StockService
from models.response import success_response, error_response

router = APIRouter(prefix="/api/filter", tags=["选股筛选"])

# 筛选请求模型
class FilterRequest(BaseModel):
    """筛选请求"""
    filters: Dict[str, Any] = {}
    page: int = 1
    page_size: int = 50


@router.get("/presets")
def get_preset_filters():
    """
    获取预设筛选条件
    """
    return {
        "code": 0,
        "data": PRESET_FILTERS
    }


@router.post("/stocks")
def filter_stocks(
    filters: Dict[str, Any] = Body(...),
    page: int = Query(1, description="页码"),
    page_size: int = Query(50, description="每页数量")
):
    """
    筛选股票
    
    请求体:
    {
        "filters": {
            "min_change": 5,        // 最小涨跌幅
            "max_change": 10,       // 最大涨跌幅
            "min_volume": 1000000,   // 最小成交量
            "min_price": 10,         // 最低股价
            "max_price": 100         // 最高股价
        }
    }
    """
    # 获取所有股票
    stocks_result = StockService.get_stock_list()
    
    if isinstance(stocks_result, dict):
        if stocks_result.get("code") != 0:
            return error_response(stocks_result.get("message", "获取股票列表失败"))
        stocks = stocks_result.get("data", [])
    else:
        stocks = stocks_result
    
    if not stocks:
        return error_response("没有股票数据")
    
    # 筛选股票
    filtered_stocks = StockFilter.filter_stocks(stocks, filters)
    
    # 分页
    total = len(filtered_stocks)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_stocks = filtered_stocks[start:end]
    
    return {
        "code": 0,
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "results": paginated_stocks
        }
    }


@router.get("/stocks/simple")
def simple_filter(
    min_price: Optional[float] = Query(None, description="最低股价"),
    max_price: Optional[float] = Query(None, description="最高股价"),
    market: Optional[str] = Query(None, description="市场: sh/sz"),
    stock_type: Optional[str] = Query(None, description="股票类型: stock/index"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(50, description="每页数量")
):
    """
    简单筛选 - 使用URL参数
    
    示例:
    /api/filter/stocks/simple?min_price=10&max_price=50&market=sh
    """
    # 构建筛选条件
    filters = {}
    if min_price is not None:
        filters['min_price'] = min_price
    if max_price is not None:
        filters['max_price'] = max_price
    
    # 获取股票列表
    stocks_result = StockService.get_stock_list()
    
    if isinstance(stocks_result, dict):
        if stocks_result.get("code") != 0:
            return error_response(stocks_result.get("message", "获取股票列表失败"))
        stocks = stocks_result.get("data", [])
    else:
        stocks = stocks_result
    
    if not stocks:
        return error_response("没有股票数据")
    
    # 应用筛选
    filtered = stocks
    
    if market:
        filtered = [s for s in filtered if s.get('market') == market]
    
    if stock_type:
        filtered = [s for s in filtered if s.get('stock_type') == stock_type]
    
    if min_price is not None:
        filtered = [s for s in filtered if s.get('price', 0) >= min_price]
    
    if max_price is not None:
        filtered = [s for s in filtered if s.get('price', 999999) <= max_price]
    
    # 分页
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_stocks = filtered[start:end]
    
    return {
        "code": 0,
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "results": paginated_stocks
        }
    }


@router.get("/market/overview")
def get_market_overview():
    """
    获取市场概览数据
    
    返回市场整体统计信息
    """
    # 获取所有股票
    stocks_result = StockService.get_stock_list()
    
    if isinstance(stocks_result, dict):
        if stocks_result.get("code") != 0:
            return error_response(stocks_result.get("message", "获取股票列表失败"))
        stocks = stocks_result.get("data", [])
    else:
        stocks = stocks_result
    
    if not stocks:
        return error_response("没有股票数据")
    
    # 统计
    total_stocks = len(stocks)
    sh_stocks = len([s for s in stocks if s.get('market') == 'sh'])
    sz_stocks = len([s for s in stocks if s.get('market') == 'sz'])
    index_stocks = len([s for s in stocks if s.get('stock_type') == 'index'])
    
    return {
        "code": 0,
        "data": {
            "total_stocks": total_stocks,
            "sh_stocks": sh_stocks,
            "sz_stocks": sz_stocks,
            "index_stocks": index_stocks,
            "stock_stocks": total_stocks - index_stocks
        }
    }


@router.get("/hot")
def get_hot_stocks(
    limit: int = Query(10, description="返回数量")
):
    """
    获取热门股票
    
    根据预设条件返回热门股票
    """
    # 获取所有股票
    stocks_result = StockService.get_stock_list()
    
    if isinstance(stocks_result, dict):
        if stocks_result.get("code") != 0:
            return error_response(stocks_result.get("message", "获取股票列表失败"))
        stocks = stocks_result.get("data", [])
    else:
        stocks = stocks_result
    
    if not stocks:
        return error_response("没有股票数据")
    
    # 返回前N个股票作为热门
    hot_stocks = stocks[:limit]
    
    return {
        "code": 0,
        "data": hot_stocks
    }
