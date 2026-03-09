# 舆情监控API
from fastapi import APIRouter, Query, HTTPException
from services.sentiment_service import SentimentService

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["舆情监控"])

@router.get("/{code}/news")
def get_stock_news(code: str):
    """
    获取股票新闻
    
    获取指定股票的新闻列表
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含新闻列表
    """
    return SentimentService.get_stock_news(code)

@router.get("/{code}/announcements")
def get_stock_announcements(
    code: str,
    date: str = Query(None, description="日期 YYYYMMDD，默认获取最新")
):
    """
    获取股票公告
    
    获取指定股票的公告列表
    
    Args:
        code: 股票代码
        date: 日期（可选，格式：YYYYMMDD）
        
    Returns:
        dict: 统一响应格式，包含公告列表
    """
    return SentimentService.get_stock_announcements(code, date)

@router.get("/{code}/research")
def get_stock_research(code: str):
    """
    获取券商研报
    
   获取指定股票的券商研报列表
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含研报列表
    """
    return SentimentService.get_stock_research(code)
