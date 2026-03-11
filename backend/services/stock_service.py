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
from config import AKSHARE_CONFIG, MOCK_DATA_CONFIG, BASE_PRICES, PERFORMANCE_CONFIG, STOCK_CODE_REGEX, STOCK_LIST
from utils.logger import logger
from utils.cache import cache
import random

# 支持的K线周期
KLINE_PERIODS = ["daily", "weekly", "monthly", "1min", "5min", "15min", "30min", "60min"]

# 周期缓存TTL配置(秒)
PERIOD_TTL = {
    "daily": 300,       # 5分钟
    "weekly": 1800,     # 30分钟
    "monthly": 3600,    # 1小时
    "1min": 60,         # 1分钟
    "5min": 300,        # 5分钟
    "15min": 600,       # 10分钟
    "30min": 900,       # 15分钟
    "60min": 1800,      # 30分钟
}

# Tushare Token 配置
# 可以通过环境变量 TUSHARE_TOKEN 设置，或在此处直接填写Token
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "87f3e60abf63e49dc8589ab903515d6e4cde5a07a54066845180d38b")
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
    def get_stock_list(use_tushare: bool = True):
        """
        获取股票列表
        
        优先从Tushare获取全量A股列表，缓存1小时
        如果Tushare不可用，则从数据库获取
        
        Args:
            use_tushare: 是否优先使用Tushare获取数据
            
        Returns:
            dict: 统一响应格式
        """
        # 尝试从缓存获取
        cache_key = "stock:list:full"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info("从缓存获取股票列表")
            return success_response(cached_data)
        
        result = []
        
        # 优先从Tushare获取全量A股列表
        if use_tushare and TUSHARE_TOKEN:
            try:
                _init_tushare()
                pro = ts.pro_api()
                
                # 获取上海A股
                df_sh = pro.stock_basic(exchange='SSE', list_status='L', fields='ts_code,symbol,name,market,list_status')
                # 获取深圳A股
                df_sz = pro.stock_basic(exchange='SZSE', list_status='L', fields='ts_code,symbol,name,market,list_status')
                
                if df_sh is not None and not df_sh.empty:
                    for _, row in df_sh.iterrows():
                        ts_code = str(row.get('ts_code', ''))
                        code = ts_code.replace('.SH', '') if ts_code else ''
                        result.append({
                            "code": code,
                            "name": row.get('name', ''),
                            "market": "sh",
                            "stock_type": "stock"
                        })
                
                if df_sz is not None and not df_sz.empty:
                    for _, row in df_sz.iterrows():
                        ts_code = str(row.get('ts_code', ''))
                        code = ts_code.replace('.SZ', '') if ts_code else ''
                        result.append({
                            "code": code,
                            "name": row.get('name', ''),
                            "market": "sz",
                            "stock_type": "stock"
                        })
                
                logger.info(f"从Tushare获取股票列表成功，共{len(result)}条")
                
            except Exception as e:
                logger.warning(f"从Tushare获取股票列表失败: {e}，尝试从数据库获取")
        
        # 如果Tushare获取失败或不需要，从数据库获取
        if not result:
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
                db.close()
                logger.info(f"从数据库获取股票列表成功，共{len(result)}条")
            except Exception as e:
                logger.error(f"获取股票列表失败: {e}")
                return error_response(f"获取股票列表失败: {str(e)}")
        
        # 存入缓存（1小时）
        cache.set(cache_key, result, ttl=3600)
        
        return success_response(result)
    
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

            # 获取全量股票列表进行搜索
            all_stocks = StockService.get_stock_list(use_tushare=True)
            if all_stocks.get('code') != 0:
                # 如果获取失败，使用本地列表
                all_stocks = STOCK_LIST
            else:
                all_stocks = all_stocks.get('data', [])

            # 搜索匹配
            keyword_lower = keyword.lower()
            result = [
                stock for stock in all_stocks
                if keyword_lower in str(stock.get("code", "")).lower() or keyword_lower in stock.get("name", "").lower()
            ]

            logger.info(f"搜索'{keyword}'找到{len(result)}条结果")
            return success_response(result)
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return error_response(f"搜索失败: {str(e)}")
    
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
        """
        从Tushare获取K线数据
        
        Args:
            stock_code: 股票代码
            market: 市场类型 (sh/sz)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 周期 (daily/weekly/monthly/1min/5min/15min/30min/60min)
            
        Returns:
            DataFrame: K线数据
        """
        _init_tushare()
        try:
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            if not start_date:
                # 根据不同周期设置不同的默认开始日期
                if period in ["daily"]:
                    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
                elif period in ["weekly", "monthly"]:
                    start_date = (datetime.now() - timedelta(days=365*3)).strftime("%Y%m%d")
                else:  # 分钟级别
                    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            
            ts_code = f"{stock_code}.SH" if market == "sh" else f"{stock_code}.SZ"
            pro = ts.pro_api()
            
            if period == "daily":
                df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            elif period == "weekly":
                df = pro.weekly(ts_code=ts_code, start_date=start_date, end_date=end_date)
            elif period == "monthly":
                df = pro.monthly(ts_code=ts_code, start_date=start_date, end_date=end_date)
            elif period in ["1min", "5min", "15min", "30min", "60min"]:
                # 分钟级别数据
                minute_type = period.replace("min", "")
                # Tushare需要转换为分钟数
                df = pro.minute(ts_code=ts_code, start_date=start_date, end_date=end_date, freq=minute_type)
            else:
                logger.warning(f"不支持的周期: {period}")
                return pd.DataFrame()
            
            if df is None or df.empty:
                return pd.DataFrame()
            
            # 统一字段名
            df = df.rename(columns={'trade_date': 'date', 'vol': 'volume'})
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')
            return df.sort_values('date')
        except Exception as e:
            logger.error(f"从Tushare获取K线数据失败: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_history_kline(stock_code: str, period: str = "daily", 
                          start_date: str = None, end_date: str = None):
        """
        获取股票历史K线数据
        
        支持周期: daily, weekly, monthly, 1min, 5min, 15min, 30min, 60min
        
        Args:
            stock_code: 股票代码
            period: 数据周期
            start_date: 开始日期 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)
            end_date: 结束日期 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)
            
        Returns:
            dict: 统一响应格式
        """
        # 验证股票代码
        is_valid, error_msg = StockService.validate_stock_code(stock_code)
        if not is_valid:
            return error_response(error_msg)
        
        # 验证周期参数
        if period not in KLINE_PERIODS:
            return error_response(f"不支持的周期: {period}，支持的周期: {', '.join(KLINE_PERIODS)}")
        
        # 缓存键包含完整参数
        cache_key = f"kline:{stock_code}:{period}:{start_date}:{end_date}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"从缓存获取K线数据: {stock_code} {period}")
            return success_response(cached_data)
        
        # 设置默认日期
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            if period in ["daily"]:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            elif period in ["weekly", "monthly"]:
                start_date = (datetime.now() - timedelta(days=365*3)).strftime("%Y-%m-%d")
            else:  # 分钟级别
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        db = SessionLocal()
        try:
            # 查询股票信息
            stock = db.query(Stock).filter(Stock.code == stock_code).first()
            if not stock:
                logger.warning(f"未在数据库找到股票: {stock_code}，尝试直接获取数据")
                market = "sh" if stock_code.startswith("6") else "sz"
            else:
                market = stock.market
            
            logger.info(f"获取K线数据: {stock_code} 周期: {period} 市场: {market}")
            
            df = pd.DataFrame()
            
            # 优先使用Tushare
            if TUSHARE_TOKEN:
                df = StockService.fetch_kline_from_tushare(
                    stock_code, market,
                    start_date.replace("-", ""),
                    end_date.replace("-", ""), period)
            
            # 如果Tushare失败，尝试AkShare（仅支持日周月）
            if (df is None or df.empty) and period in ["daily", "weekly", "monthly"]:
                try:
                    s_ak = start_date.replace("-", "")
                    e_ak = end_date.replace("-", "")
                    symbol = f"{market}{stock_code}"
                    df = ak.stock_zh_a_hist(
                        symbol=symbol, 
                        period=period, 
                        start_date=s_ak, 
                        end_date=e_ak, 
                        adjust="qfq"
                    )
                except Exception as e:
                    logger.warning(f"从AkShare获取数据失败: {e}")
            
            # 如果仍然没有数据，使用模拟数据
            if df is None or df.empty:
                if MOCK_DATA_CONFIG["enabled"]:
                    logger.info(f"使用模拟数据: {stock_code}")
                    mock = StockService.get_mock_kline_data_by_period(stock_code, period)
                    cache.set(cache_key, mock, ttl=60)
                    return success_response(mock)
                else:
                    return error_response("无法从数据源获取数据，且模拟数据已禁用")
            
            # 转换为统一格式
            klines = StockService._convert_kline_data(df, period)
            
            # 根据周期设置缓存TTL
            ttl = PERIOD_TTL.get(period, 300)
            cache.set(cache_key, klines, ttl)
            logger.info(f"K线数据已缓存: {stock_code} {period}，共{len(klines)}条")
            
            return success_response(klines)
            
        except Exception as e:
            error_msg = f"获取K线数据失败: {str(e)}"
            logger.error(error_msg)
            
            # 失败时尝试返回模拟数据
            if MOCK_DATA_CONFIG["enabled"]:
                mock = StockService.get_mock_kline_data_by_period(stock_code, period)
                cache.set(cache_key, mock, ttl=60)
                return success_response(mock)
            
            return error_response(error_msg)
        finally:
            db.close()
    
    @staticmethod
    def _convert_kline_data(df: pd.DataFrame, period: str) -> list:
        """
        将DataFrame转换为统一的K线数据格式
        
        Args:
            df: 原始数据
            period: 周期
            
        Returns:
            list: 统一格式的K线数据
        """
        klines = []
        
        # 检查字段名格式（Tushare格式 vs AkShare格式）
        has_tushare_format = 'open' in df.columns and 'close' in df.columns
        has_akshare_format = '开盘' in df.columns
        
        for _, r in df.iterrows():
            if has_tushare_format:
                date_val = r.get('date')
                if pd.isna(date_val):
                    continue
                klines.append({
                    "date": str(date_val),
                    "open": float(r.get("open", 0) or 0),
                    "high": float(r.get("high", 0) or 0),
                    "low": float(r.get("low", 0) or 0),
                    "close": float(r.get("close", 0) or 0),
                    "volume": float(r.get("volume", 0) or 0)
                })
            elif has_akshare_format:
                date_val = r.get("日期")
                if pd.isna(date_val):
                    continue
                klines.append({
                    "date": str(date_val),
                    "open": float(r.get("开盘", 0)),
                    "high": float(r.get("最高", 0)),
                    "low": float(r.get("最低", 0)),
                    "close": float(r.get("收盘", 0)),
                    "volume": float(r.get("成交量", 0))
                })
        
        return klines
    
    @staticmethod
    def get_mock_kline_data_by_period(stock_code: str, period: str = "daily") -> list:
        """
        根据周期获取模拟K线数据
        
        Args:
            stock_code: 股票代码
            period: 周期
            
        Returns:
            list: K线数据列表
        """
        base_price = BASE_PRICES.get(stock_code, 100)
        kline_list = []
        
        # 根据周期确定数据数量
        if period == "daily":
            days = 90
            date_format = "%Y-%m-%d"
            delta = timedelta(days=1)
        elif period == "weekly":
            days = 52
            date_format = "%Y-%m-%d"
            delta = timedelta(weeks=1)
        elif period == "monthly":
            days = 36
            date_format = "%Y-%m-%d"
            delta = timedelta(days=30)
        elif period in ["1min", "5min", "15min", "30min", "60min"]:
            # 分钟级别数据 - 生成最近240个交易分钟
            days = 1  # 1天内的分钟数据
            date_format = "%Y-%m-%d %H:%M:%S"
            
            # 模拟当天的交易时间
            for i in range(240):
                minutes_ago = (239 - i) * int(period.replace("min", ""))
                date = datetime.now().replace(hour=9, minute=30, second=0) - timedelta(minutes=minutes_ago)
                
                # 跳过午间休市时间
                if date.hour == 12:
                    continue
                    
                # 随机波动
                change = random.uniform(-0.02, 0.02)
                open_price = base_price * (1 + random.uniform(-0.01, 0.01))
                close_price = open_price * (1 + change)
                high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))
                low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))
                volume = random.randint(10000, 100000)
                
                kline_list.append({
                    "date": date.strftime(date_format),
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": volume
                })
                
                base_price = close_price
            
            return kline_list
        else:
            days = 90
            date_format = "%Y-%m-%d"
            delta = timedelta(days=1)
        
        # 生成日周月数据
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            
            # 随机波动
            change = random.uniform(-0.03, 0.03)
            open_price = base_price * (1 + random.uniform(-0.02, 0.02))
            close_price = open_price * (1 + change)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
            volume = random.randint(5000000, 50000000)
            
            kline_list.append({
                "date": date.strftime(date_format),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
            
            base_price = close_price
        
        return kline_list
