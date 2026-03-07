# 股票数据服务
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from database import SessionLocal
from models.stock import Stock, KLine
from models.response import success_response, error_response
from config import AKSHARE_CONFIG, MOCK_DATA_CONFIG, BASE_PRICES
import re
import random

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
        
        if not re.match(r"^\d{6}(_sh)?$", code):
            return False, "股票代码格式错误，应为6位数字"
        
        return True, ""
    
    @staticmethod
    def get_stock_list():
        """
        获取股票列表
        
        Returns:
            dict: 统一响应格式
        """
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
            return success_response(result)
        except Exception as e:
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
            return success_response(result)
        except Exception as e:
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
            return success_response(kline_list)
            
        except Exception as e:
            db.rollback()
            error_msg = f"获取K线数据失败: {str(e)}"
            print(error_msg)
            
            # 失败时尝试返回模拟数据
            if MOCK_DATA_CONFIG["enabled"]:
                return success_response(StockService.get_mock_kline_data(stock_code))
            
            return error_response(error_msg)
        finally:
            db.close()
