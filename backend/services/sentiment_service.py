# 舆情数据服务
"""
舆情监控数据服务模块

提供股票新闻、公告、研报等功能
优先使用 AkShare 真实数据
情绪/舆情模块不支持模拟数据降级，必须返回真实数据或明确报错
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from models.response import success_response, error_response, not_found_error
from utils.logger import logger
from utils.cache import cache


class SentimentService:
    """舆情数据服务"""
    
    @staticmethod
    def validate_stock_code(code: str) -> tuple[bool, str]:
        """
        验证股票代码格式
        返回: (是否有效, 错误信息)
        """
        if not code:
            return False, "股票代码不能为空"
        
        if len(code) != 6 or not code.isdigit():
            return False, "股票代码格式错误，应为6位数字"
        
        return True, ""
    
    @staticmethod
    def get_stock_news(stock_code: str):
        """
        获取股票新闻
        
        Args:
            stock_code: 股票代码
            
        Returns:
            dict: 统一响应格式
        """
        # 验证股票代码
        is_valid, error_msg = SentimentService.validate_stock_code(stock_code)
        if not is_valid:
            return error_response(error_msg)
        
        # 尝试从缓存获取
        cache_key = f"sentiment:news:{stock_code}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"从缓存获取股票新闻: {stock_code}")
            return success_response(cached_data)
        
        logger.info(f"获取股票新闻: {stock_code}")
        
        try:
            # 从AkShare获取新闻数据
            df = ak.stock_news_em(symbol=stock_code)
            
            if df is None or df.empty:
                # 情绪模块：无数据就是无数据，不使用模拟数据降级
                return not_found_error(
                    message="暂无新闻数据",
                    detail=f"股票 {stock_code} 今日暂无新闻发布"
                )
            
            # 转换数据格式
            news_list = []
            for _, row in df.iterrows():
                news_item = {
                    "title": str(row.get("新闻标题", "")),
                    "pub_date": str(row.get("发布时间", "")),
                    "source": str(row.get("文章来源", "")),
                    "url": str(row.get("新闻链接", ""))
                }
                # 过滤空标题
                if news_item["title"]:
                    news_list.append(news_item)
            
            if not news_list:
                # 情绪模块：无数据就是无数据
                return not_found_error(
                    message="暂无新闻数据",
                    detail=f"股票 {stock_code} 今日暂无新闻发布"
                )
            
            # 存入缓存
            cache.set(cache_key, news_list, ttl=300)
            logger.info(f"获取股票新闻成功: {stock_code}, 共{len(news_list)}条")
            
            return success_response(news_list)
            
        except Exception as e:
            logger.error(f"获取股票新闻失败: {e}")
            # 情绪模块：即使出错也不使用模拟数据，返回明确错误
            return {
                "code": 1,
                "message": "情绪数据获取失败",
                "error": "data_fetch_failed"
            }
    
    @staticmethod
    def get_stock_announcements(stock_code: str, date: str = None):
        """
        获取股票公告
        
        Args:
            stock_code: 股票代码
            date: 日期（YYYYMMDD格式）
            
        Returns:
            dict: 统一响应格式
        """
        # 验证股票代码
        is_valid, error_msg = SentimentService.validate_stock_code(stock_code)
        if not is_valid:
            return error_response(error_msg)
        
        # 如果没有指定日期，默认获取当天的
        if not date:
            date = datetime.now().strftime("%Y%m%d")
        
        # 尝试从缓存获取
        cache_key = f"sentiment:announcements:{stock_code}:{date}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"从缓存获取股票公告: {stock_code}, date={date}")
            return success_response(cached_data)
        
        logger.info(f"获取股票公告: {stock_code}, date={date}")
        
        try:
            # 从AkShare获取公告数据
            df = ak.stock_notice_report(symbol=stock_code, date=date)
            
            if df is None or df.empty:
                # 情绪模块：无数据就是无数据，不使用模拟数据降级
                return not_found_error(
                    message="暂无公告数据",
                    detail=f"股票 {stock_code} 在 {date} 暂无公告发布"
                )
            
            # 转换数据格式
            announcements = []
            for _, row in df.iterrows():
                # 尝试多种可能的列名
                title = row.get("公告标题") or row.get("title") or row.get("notice_title", "")
                pub_date = row.get("公告日期") or row.get("pub_date") or row.get("date", "")
                ann_type = row.get("公告类型") or row.get("type") or row.get("notice_type", "")
                url = row.get("公告链接") or row.get("url") or row.get("link", "")
                
                announcement = {
                    "title": str(title),
                    "pub_date": str(pub_date),
                    "announcement_type": str(ann_type) if ann_type else "其他",
                    "url": str(url) if url else ""
                }
                
                # 过滤空标题
                if announcement["title"]:
                    announcements.append(announcement)
            
            if not announcements:
                # 情绪模块：无数据就是无数据
                return not_found_error(
                    message="暂无公告数据",
                    detail=f"股票 {stock_code} 在 {date} 暂无公告发布"
                )
            
            # 存入缓存
            cache.set(cache_key, announcements, ttl=300)
            logger.info(f"获取股票公告成功: {stock_code}, date={date}, 共{len(announcements)}条")
            
            return success_response(announcements)
            
        except Exception as e:
            logger.error(f"获取股票公告失败: {e}")
            # 情绪模块：即使出错也不使用模拟数据，返回明确错误
            return {
                "code": 1,
                "message": "情绪数据获取失败",
                "error": "data_fetch_failed"
            }
    
    @staticmethod
    def get_stock_research(stock_code: str):
        """
        获取券商研报
        
        Args:
            stock_code: 股票代码
            
        Returns:
            dict: 统一响应格式
        """
        # 验证股票代码
        is_valid, error_msg = SentimentService.validate_stock_code(stock_code)
        if not is_valid:
            return error_response(error_msg)
        
        # 尝试从缓存获取
        cache_key = f"sentiment:research:{stock_code}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"从缓存获取券商研报: {stock_code}")
            return success_response(cached_data)
        
        logger.info(f"获取券商研报: {stock_code}")
        
        try:
            # 从AkShare获取研报数据
            df = ak.stock_research_report_em(symbol=stock_code)
            
            if df is None or df.empty:
                # 情绪模块：无数据就是无数据，不使用模拟数据降级
                return not_found_error(
                    message="暂无研报数据",
                    detail=f"股票 {stock_code} 暂无研报发布"
                )
            
            # 转换数据格式
            research_list = []
            for _, row in df.iterrows():
                # 尝试多种可能的列名
                title = row.get("研报标题") or row.get("title") or row.get("report_title", "")
                pub_date = row.get("研报发布日期") or row.get("pub_date") or row.get("date", "")
                institute = row.get("证券公司") or row.get("institute") or row.get("org_name", "")
                author = row.get("分析师") or row.get("author") or row.get("analyst", "")
                rating = row.get("评级") or row.get("rating") or row.get("rating_name", "")
                url = row.get("研报链接") or row.get("url") or row.get("link", "")
                
                research = {
                    "title": str(title),
                    "pub_date": str(pub_date),
                    "institute": str(institute),
                    "author": str(author) if author else "未知",
                    "rating": str(rating) if rating else "未评级",
                    "url": str(url) if url else ""
                }
                
                # 过滤空标题
                if research["title"]:
                    research_list.append(research)
            
            if not research_list:
                # 情绪模块：无数据就是无数据
                return not_found_error(
                    message="暂无研报数据",
                    detail=f"股票 {stock_code} 暂无研报发布"
                )
            
            # 存入缓存
            cache.set(cache_key, research_list, ttl=3600)
            logger.info(f"获取券商研报成功: {stock_code}, 共{len(research_list)}条")
            
            return success_response(research_list)
            
        except Exception as e:
            logger.error(f"获取券商研报失败: {e}")
            # 情绪模块：即使出错也不使用模拟数据，返回明确错误
            return {
                "code": 1,
                "message": "情绪数据获取失败",
                "error": "data_fetch_failed"
            }
