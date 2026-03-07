# 股票API路由
from fastapi import APIRouter, Query
from services.stock_service import StockService

router = APIRouter(prefix="/api/stock", tags=["股票"])

@router.get("/list")
def get_stock_list():
    """获取股票列表"""
    stocks = StockService.get_stock_list()
    return {"code": 0, "data": stocks}

@router.get("/search")
def search_stocks(keyword: str = Query(..., description="搜索关键词")):
    """搜索股票"""
    stocks = StockService.search_stocks(keyword)
    return {"code": 0, "data": stocks}

@router.get("/{code}")
def get_stock_kline(code: str):
    """获取股票K线数据"""
    klines = StockService.get_kline_data(code)
    return {"code": 0, "data": klines}
