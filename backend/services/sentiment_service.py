# 舆情数据服务
"""
舆情监控数据服务模块

提供股票新闻、公告、研报等功能
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from models.response import success_response, error_response
from config import MOCK_DATA_CONFIG
from utils.logger import logger
from utils.cache import cache
import random


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
    def get_mock_news_data(stock_code: str) -> list:
        """获取模拟新闻数据"""
        news_list = []
        titles = [
            f"{stock_code}发布最新财报，营收同比增长",
            f"券商上调{stock_code}目标价",
            f"{stock_code}获得重大合同订单",
            f"机构扎堆调研{stock_code}",
            f"{stock_code}布局新能源领域"
        ]
        
        for i, title in enumerate(titles):
            news_list.append({
                "title": title + f" {random.randint(10, 50)}%",
                "pub_date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S"),
                "source": random.choice(["新浪财经", "东方财富", "证券日报", "第一财经"]),
                "url": f"https://example.com/news/{stock_code}/{i}"
            })
        
        return news_list
    
    @staticmethod
    def get_mock_announcement_data(stock_code: str) -> list:
        """获取模拟公告数据"""
        announcements = []
        titles = [
            f"关于{stock_code}2024年度股东大会决议公告",
            f"{stock_code}2024年年度报告摘要",
            f"关于{stock_code}重大资产重组进展公告",
            f"{stock_code}关于股票异常波动的澄清公告",
            f"{stock_code}2024年度利润分配方案"
        ]
        
        for i, title in enumerate(titles):
            announcements.append({
                "title": title,
                "pub_date": (datetime.now() - timedelta(days=i*2)).strftime("%Y-%m-%d"),
                "announcement_type": random.choice(["定期报告", "临时公告", "业绩预告", "风险提示"]),
                "url": f"https://example.com/announcement/{stock_code}/{i}"
            })
        
        return announcements
    
    @staticmethod
    def get_mock_research_data(stock_code: str) -> list:
        """获取模拟研报数据"""
        research_list = []
        institutes = ["中金公司", "华泰证券", "国泰君安", "中信证券", "银河证券", "申万宏源"]
        titles = [
            "首次覆盖，给予买入评级",
            "年报点评：业绩超预期",
            "深度报告：龙头地位稳固",
            "季报点评：增长动能强劲",
            "行业专题：景气度上行"
        ]
        
        for i, title in enumerate(titles):
            research_list.append({
                "title": f"{stock_code}：{title}",
                "pub_date": (datetime.now() - timedelta(days=i*3)).strftime("%Y-%m-%d"),
                "institute": random.choice(institutes),
                "author": random.choice(["分析师A", "分析师B", "首席分析师"]),
                "rating": random.choice(["买入", "增持", "中性", "推荐"]),
                "url": f"https://example.com/research/{stock_code}/{i}"
            })
        
        return research_list
    
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
                if MOCK_DATA_CONFIG["enabled"]:
                    mock_data = SentimentService.get_mock_news_data(stock_code)
                    cache.set(cache_key, mock_data, ttl=300)
                    return success_response(mock_data)
                return error_response("暂无新闻数据")
            
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
                if MOCK_DATA_CONFIG["enabled"]:
                    mock_data = SentimentService.get_mock_news_data(stock_code)
                    cache.set(cache_key, mock_data, ttl=300)
                    return success_response(mock_data)
                return error_response("暂无新闻数据")
            
            # 存入缓存
            cache.set(cache_key, news_list, ttl=300)
            logger.info(f"获取股票新闻成功: {stock_code}, 共{len(news_list)}条")
            
            return success_response(news_list)
            
        except Exception as e:
            logger.error(f"获取股票新闻失败: {e}")
            if MOCK_DATA_CONFIG["enabled"]:
                mock_data = SentimentService.get_mock_news_data(stock_code)
                cache.set(cache_key, mock_data, ttl=60)
                return success_response(mock_data)
            return error_response(f"获取股票新闻失败: {str(e)}")
    
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
                if MOCK_DATA_CONFIG["enabled"]:
                    mock_data = SentimentService.get_mock_announcement_data(stock_code)
                    cache.set(cache_key, mock_data, ttl=300)
                    return success_response(mock_data)
                return error_response("暂无公告数据")
            
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
                if MOCK_DATA_CONFIG["enabled"]:
                    mock_data = SentimentService.get_mock_announcement_data(stock_code)
                    cache.set(cache_key, mock_data, ttl=300)
                    return success_response(mock_data)
                return error_response("暂无公告数据")
            
            # 存入缓存
            cache.set(cache_key, announcements, ttl=300)
            logger.info(f"获取股票公告成功: {stock_code}, date={date}, 共{len(announcements)}条")
            
            return success_response(announcements)
            
        except Exception as e:
            logger.error(f"获取股票公告失败: {e}")
            if MOCK_DATA_CONFIG["enabled"]:
                mock_data = SentimentService.get_mock_announcement_data(stock_code)
                cache.set(cache_key, mock_data, ttl=60)
                return success_response(mock_data)
            return error_response(f"获取股票公告失败: {str(e)}")
    
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
                if MOCK_DATA_CONFIG["enabled"]:
                    mock_data = SentimentService.get_mock_research_data(stock_code)
                    cache.set(cache_key, mock_data, ttl=300)
                    return success_response(mock_data)
                return error_response("暂无研报数据")
            
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
                if MOCK_DATA_CONFIG["enabled"]:
                    mock_data = SentimentService.get_mock_research_data(stock_code)
                    cache.set(cache_key, mock_data, ttl=300)
                    return success_response(mock_data)
                return error_response("暂无研报数据")
            
            # 存入缓存
            cache.set(cache_key, research_list, ttl=3600)
            logger.info(f"获取券商研报成功: {stock_code}, 共{len(research_list)}条")
            
            return success_response(research_list)
            
        except Exception as e:
            logger.error(f"获取券商研报失败: {e}")
            if MOCK_DATA_CONFIG["enabled"]:
                mock_data = SentimentService.get_mock_research_data(stock_code)
                cache.set(cache_key, mock_data, ttl=60)
                return success_response(mock_data)
            return error_response(f"获取券商研报失败: {str(e)}")
