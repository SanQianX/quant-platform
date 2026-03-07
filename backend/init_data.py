# 初始化股票数据
from database import SessionLocal, engine, Base
from models.stock import Stock

# 10只热门股票 + 3大指数
STOCKS_DATA = [
    # 热门股票
    {"code": "000001", "name": "平安银行", "market": "sz", "stock_type": "stock"},
    {"code": "600519", "name": "贵州茅台", "market": "sh", "stock_type": "stock"},
    {"code": "300750", "name": "宁德时代", "market": "sz", "stock_type": "stock"},
    {"code": "600036", "name": "招商银行", "market": "sh", "stock_type": "stock"},
    {"code": "601318", "name": "中国平安", "market": "sh", "stock_type": "stock"},
    {"code": "000858", "name": "五粮液", "market": "sz", "stock_type": "stock"},
    {"code": "002594", "name": "比亚迪", "market": "sz", "stock_type": "stock"},
    {"code": "600900", "name": "长江电力", "market": "sh", "stock_type": "stock"},
    {"code": "601888", "name": "中国中免", "market": "sh", "stock_type": "stock"},
    {"code": "300059", "name": "东方财富", "market": "sz", "stock_type": "stock"},
    # 三大指数
    {"code": "000001_sh", "name": "上证指数", "market": "sh", "stock_type": "index"},
    {"code": "399001", "name": "深证成指", "market": "sz", "stock_type": "index"},
    {"code": "399006", "name": "创业板指", "market": "sz", "stock_type": "index"},
]

def init_stocks():
    """初始化股票数据"""
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查是否已存在数据
        existing = db.query(Stock).count()
        if existing > 0:
            print(f"数据库已存在 {existing} 条股票数据")
            return
        
        # 插入数据
        for stock_data in STOCKS_DATA:
            stock = Stock(**stock_data)
            db.add(stock)
        
        db.commit()
        print(f"成功初始化 {len(STOCKS_DATA)} 条股票数据")
    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_stocks()
