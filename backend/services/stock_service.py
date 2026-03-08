# 股票数据服务
"""
股票数据服务模块

提供股票列表、搜索、K线数据等功能
支持缓存和数据源适配
"""

import akshare as ak
import tushare as ts
import os
import pandas as pd
from datetime import datetime, timedelta
from database import SessionLocal
from models.stock import Stock, KLine
from models.response import success_response, error_response
from config import AKSHARE_CONFIG, MOCK_DATA_CONFIG, BASE_PRICES, PERFORMANCE_CONFIG, STOCK_CODE_REGEX
from utils.logger import logger
from utils.cache import cache
import random

# Tushare Token 配置
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")
_tushare_initialized = False

def _init_tushare():
    """初始化 Tushare"""
    global _tushare_initialized
    if TUSHARE_TOKEN and not _tushare_initialized:
        try:
            ts.set_token(TUSHARE_TOKEN)
            _tushare_initialized = True
            print("Tushare 初始化成功")
        except Exception as e:
            print(f"Tushare 初始化失败: {e}")

class StockService:
    """股票数据服务"""
    
    @staticmethod
    def validate_stock_code(code: str) -> tuple[bool, str]:
        """
        验证股票代码格式
        返回: (是否有效, 错误信息)
        """
        if not code:
            return False, "股票代码不能为空"
        
        if not STOCK_CODE_REGEX.match(code):
            return False, "股票代码格式错误，应为6位数字"
        
        return True, ""
    
    @staticmethod
    def get_stock_list():
        """
        获取股票列表
        
        Returns:
            dict: 统一响应格式
        """
        # 尝试从缓存获取
        cache_key = "stock:list"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info("从缓存获取股票列表")
            return success_response(cached_data)
        
        try:
            db = SessionLocal()
            stocks = db.query(Stock).all()
            result = [
                {
                    "code": s.code,
                    "name": s.name,
                    "market": s.market,
                    "stock_type": s.stock_type
                }
                for s in stocks
            ]
            
            # 存入缓存
            cache.set(cache_key, result, ttl=3600)
            logger.info(f"获取股票列表成功，共{len(result)}条")
            
            return success_response(result)
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return error_response(f"获取股票列表失败: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def search_stocks(keyword: str):
        """
        搜索股票
        
        Args:
            keyword: 搜索关键词（股票代码或名称）
            
        Returns:
            dict: 统一响应格式
        """
        try:
            if not keyword or len(keyword.strip()) == 0:
                return error_response("搜索关键词不能为空")
            
            logger.info(f"搜索股票: {keyword}")
            
            db = SessionLocal()
            stocks = db.query(Stock).filter(
                (Stock.name.like(f"%{keyword}%")) | 
                (Stock.code.like(f"%{keyword}%"))
            ).all()
            
            result = [
                {
                    "code": s.code,
                    "name": s.name,
                    "market": s.market,
                    "stock_type": s.stock_type
                }
                for s in stocks
            ]
            
            logger.info(f"搜索'{keyword}'找到{len(result)}条结果")
            return success_response(result)
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return error_response(f"搜索失败: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def fetch_kline_from_akshare(stock_code: str, market: str = "sh") -> pd.DataFrame:
        """
        从AkShare获取K线数据
        
        Args:
            stock_code: 股票代码
            market: 市场类型 (sh/sz)
            
        Returns:
            DataFrame: K线数据
        """
        try:
            # 确定股票代码符号
            if market == "sh" and stock_code.startswith("000"):
                symbol = "sh000001"
            elif market == "sz" and stock_code.startswith("399"):
                symbol = f"sz{stock_code}"
            else:
                symbol = f"{market}{stock_code}"
            
            # 获取日K线数据
            df = ak.stock_zh_a_hist(
                symbol=symbol, 
                period="daily", 
                start_date=AKSHARE_CONFIG["start_date"], 
                end_date=datetime.now().strftime("%Y%m%d"), 
                adjust=AKSHARE_CONFIG["adjust"]
            )
            
            return df
        except Exception as e:
            print(f"从AkShare获取K线数据失败: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_mock_kline_data(stock_code: str) -> list:
        """
        获取模拟K线数据（用于演示或网络不可用时）
        
        Args:
            stock_code: 股票代码
            
        Returns:
            list: K线数据列表
        """
        # 获取基础价格
        base_price = BASE_PRICES.get(stock_code, 100)
        kline_list = []
        
        # 生成指定天数的模拟数据
        for i in range(MOCK_DATA_CONFIG["days"]):
            date = datetime.now() - timedelta(days=MOCK_DATA_CONFIG["days"]-i)
            
            # 随机波动
            change = random.uniform(-0.03, 0.03)
            open_price = base_price * (1 + random.uniform(-0.02, 0.02))
            close_price = open_price * (1 + change)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
            volume = random.randint(5000000, 50000000)
            
            kline_list.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
            
            # 更新基础价格
            base_price = close_price
        
        return kline_list
    
    @staticmethod
    def get_kline_data(stock_code: str):
        """
        获取股票的K线数据
        
        Args:
            stock_code: 股票代码
            
        Returns:
            dict: 统一响应格式
        """
        # 验证股票代码
        is_valid, error_msg = StockService.validate_stock_code(stock_code)
        if not is_valid:
            return error_response(error_msg)
        
        # 尝试从缓存获取
        cache_key = f"kline:{stock_code}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"从缓存获取K线数据: {stock_code}")
            return success_response(cached_data)
        
        logger.info(f"获取K线数据: {stock_code}")
        
        db = SessionLocal()
        try:
            # 1. 先从数据库查询
            klines = db.query(KLine).filter(
                KLine.stock_code == stock_code
            ).order_by(KLine.date).all()
            
            if klines:
                result = [
                    {
                        "date": k.date.strftime("%Y-%m-%d"),
                        "open": k.open,
                        "high": k.high,
                        "low": k.low,
                        "close": k.close,
                        "volume": k.volume
                    }
                    for k in klines
                ]
                return success_response(result)
            
            # 2. 数据库没有，从AkShare获取
            stock = db.query(Stock).filter(Stock.code == stock_code).first()
            if not stock:
                return error_response(f"未找到股票: {stock_code}")
            
            df = StockService.fetch_kline_from_akshare(stock_code, stock.market)
            
            # 3. 如果AkShare获取失败，使用模拟数据
            if df.empty:
                if MOCK_DATA_CONFIG["enabled"]:
                    print(f"使用模拟数据: {stock_code}")
                    return success_response(StockService.get_mock_kline_data(stock_code))
                else:
                    return error_response("数据源不可用，且模拟数据已禁用")
            
            # 4. 保存到数据库并返回
            kline_list = []
            for _, row in df.iterrows():
                date_str = row.get("日期", "")
                if not date_str:
                    continue
                    
                kline = KLine(
                    stock_code=stock_code,
                    date=datetime.strptime(date_str, "%Y-%m-%d").date(),
                    open=float(row.get("开盘", 0)),
                    high=float(row.get("最高", 0)),
                    low=float(row.get("最低", 0)),
                    close=float(row.get("收盘", 0)),
                    volume=float(row.get("成交量", 0))
                )
                db.add(kline)
                kline_list.append({
                    "date": date_str,
                    "open": float(row.get("开盘", 0)),
                    "high": float(row.get("最高", 0)),
                    "low": float(row.get("最低", 0)),
                    "close": float(row.get("收盘", 0)),
                    "volume": float(row.get("成交量", 0))
                })
            
            db.commit()
            
            # 存入缓存
            cache.set(cache_key, kline_list, ttl=300)
            logger.info(f"K线数据已缓存: {stock_code}")
            
            return success_response(kline_list)
            
        except Exception as e:
            db.rollback()
            error_msg = f"获取K线数据失败: {str(e)}"
            logger.error(error_msg)
            
            # 失败时尝试返回模拟数据
            if MOCK_DATA_CONFIG["enabled"]:
                mock_data = StockService.get_mock_kline_data(stock_code)
                cache.set(cache_key, mock_data, ttl=60)
                return success_response(mock_data)
            
            return error_response(error_msg)
        finally:
            db.close()
    
    @staticmethod
    def fetch_kline_from_tushare(stock_code: str, market: str = "sh", 
                                  start_date: str = None, end_date: str = None,
                                  period: str = "daily") -> pd.DataFrame:
        """从Tushare获取K线数据"""
        _init_tushare()
        try:
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            
            ts_code = f"{stock_code}.SH" if market == "sh" else f"{stock_code}.SZ"
            pro = ts.pro_api()
            
            if period == "daily":
                df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            elif period == "weekly":
                df = pro.weekly(ts_code=ts_code, start_date=start_date, end_date=end_date)
            elif period == "monthly":
                df = pro.monthly(ts_code=ts_code, start_date=start_date, end_date=end_date)
            else:
                return pd.DataFrame()
            
            if df is None or df.empty:
                return pd.DataFrame()
            
            df = df.rename(columns={'trade_date': 'date', 'vol': 'volume'})
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            return df.sort_values('date')
        except Exception as e:
            print(f"获取Tushare数据失败: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_history_kline(stock_code: str, period: str = "daily", 
                          start_date: str = None, end_date: str = None):
        """获取股票历史K线数据（支持日线、周线、月线）"""
        is_valid, error_msg = StockService.validate_stock_code(stock_code)
        if not is_valid:
            return error_response(error_msg)
        
        cache_key = f"kline:{stock_code}:{period}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return success_response(cached_data)
        
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        db = SessionLocal()
        try:
            stock = db.query(Stock).filter(Stock.code == stock_code).first()
            if not stock:
                return error_response(f"未找到股票: {stock_code}")
            
            if TUSHARE_TOKEN:
                df = StockService.fetch_kline_from_tushare(
                    stock_code, stock.market,
                    start_date.replace("-", ""),
                    end_date.replace("-", ""), period)
            else:
                s_ak = start_date.replace("-", "")
                e_ak = end_date.replace("-", "")
                symbol = f"{stock.market}{stock_code}"
                df = ak.stock_zh_a_hist(symbol=symbol, period=period, start_date=s_ak, end_date=e_ak, adjust="qfq") if period in ["daily", "weekly", "monthly"] else pd.DataFrame()
            
            if df is None or df.empty:
                if MOCK_DATA_CONFIG["enabled"]:
                    mock = StockService.get_mock_kline_data(stock_code)
                    cache.set(cache_key, mock, ttl=60)
                    return success_response(mock)
                return error_response("无法获取数据")
            
            klines = []
            for _, r in df.iterrows():
                d = r.get("date") or r.get("日期") or r.get("trade_date")
                if not d: continue
                if "open" in r:
                    klines.append({"date": str(d), "open": float(r.get("open", 0) or 0), "high": float(r.get("high", 0) or 0), "low": float(r.get("low", 0) or 0), "close": float(r.get("close", 0) or 0), "volume": float(r.get("volume", 0) or 0)})
                else:
                    klines.append({"date": str(d), "open": float(r.get("开盘", 0)), "high": float(r.get("最高", 0)), "low": float(r.get("最低", 0)), "close": float(r.get("收盘", 0)), "volume": float(r.get("成交量", 0))})
            
            cache.set(cache_key, klines, ttl={"daily": 300, "weekly": 1800, "monthly": 3600}.get(period, 300))
            return success_response(klines)
        except Exception as e:
            return error_response(f"获取历史K线失败: {str(e)}")
        finally:
            db.close()
