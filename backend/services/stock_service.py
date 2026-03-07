# 股票数据服务
import akshare as ak
import pandas as pd
from datetime import datetime
from database import SessionLocal
from models.stock import Stock, KLine

class StockService:
    """股票数据服务"""
    
    @staticmethod
    def get_stock_list():
        """获取股票列表"""
        db = SessionLocal()
        try:
            stocks = db.query(Stock).all()
            return [
                {
                    "code": s.code,
                    "name": s.name,
                    "market": s.market,
                    "stock_type": s.stock_type
                }
                for s in stocks
            ]
        finally:
            db.close()
    
    @staticmethod
    def search_stocks(keyword: str):
        """搜索股票"""
        db = SessionLocal()
        try:
            stocks = db.query(Stock).filter(
                (Stock.name.like(f"%{keyword}%")) | 
                (Stock.code.like(f"%{keyword}%"))
            ).all()
            return [
                {
                    "code": s.code,
                    "name": s.name,
                    "market": s.market,
                    "stock_type": s.stock_type
                }
                for s in stocks
            ]
        finally:
            db.close()
    
    @staticmethod
    def fetch_kline_from_akshare(stock_code: str, market: str = "sh") -> pd.DataFrame:
        """从AkShare获取K线数据"""
        try:
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
                start_date="20240101", 
                end_date=datetime.now().strftime("%Y%m%d"), 
                adjust="qfq"
            )
            
            return df
        except Exception as e:
            print(f"获取K线数据失败: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_kline_data(stock_code: str):
        """获取股票的K线数据"""
        db = SessionLocal()
        try:
            # 先从数据库查询
            klines = db.query(KLine).filter(
                KLine.stock_code == stock_code
            ).order_by(KLine.date).all()
            
            if klines:
                return [
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
            
            # 数据库没有，从AkShare获取
            stock = db.query(Stock).filter(Stock.code == stock_code).first()
            if not stock:
                return []
            
            df = StockService.fetch_kline_from_akshare(stock_code, stock.market)
            
            if df.empty:
                return []
            
            # 保存到数据库
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
            return kline_list
            
        except Exception as e:
            db.rollback()
            print(f"获取K线数据失败: {e}")
            return []
        finally:
            db.close()
