# 股票数据服务
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
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
    def get_mock_kline_data(stock_code: str) -> list:
        """获取模拟K线数据（用于演示）"""
        import random
        # 基础价格
        base_prices = {
            "600519": 1800,  # 茅台
            "000001": 12,    # 平安银行
            "300750": 200,   # 宁德时代
            "600036": 35,    # 招商银行
            "601318": 45,    # 中国平安
            "000858": 150,   # 五粮液
            "002594": 250,   # 比亚迪
            "600900": 22,    # 长江电力
            "601888": 70,    # 中国中免
            "300059": 20,    # 东方财富
            "000001_sh": 3200,  # 上证指数
            "399001": 11000,    # 深证成指
            "399006": 2200,     # 创业板指
        }
        
        base_price = base_prices.get(stock_code, 100)
        kline_list = []
        
        # 生成90天数据
        for i in range(90):
            date = datetime.now() - timedelta(days=90-i)
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
            
            base_price = close_price
        
        return kline_list
    
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
            
            # 如果AkShare获取失败，使用模拟数据
            if df.empty:
                print(f"使用模拟数据: {stock_code}")
                return StockService.get_mock_kline_data(stock_code)
            
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
            # 失败时返回模拟数据
            return StockService.get_mock_kline_data(stock_code)
        finally:
            db.close()
