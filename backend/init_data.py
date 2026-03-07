# 初始化股票数据
"""
初始化股票数据到数据库

初始化13只股票（10只热门股票 + 3大指数）
"""

from database import SessionLocal, engine, Base
from models.stock import Stock
from config import STOCK_LIST

def init_stocks():
    """
    初始化股票数据
    
    将配置的股票列表插入数据库（如果不存在）
    """
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查是否已存在数据
        existing = db.query(Stock).count()
        if existing > 0:
            print(f"数据库已存在 {existing} 条股票数据，跳过初始化")
            return
        
        # 插入数据
        for stock_data in STOCK_LIST:
            stock = Stock(**stock_data)
            db.add(stock)
        
        db.commit()
        print(f"成功初始化 {len(STOCK_LIST)} 条股票数据")
        
    except Exception as e:
        db.rollback()
        print(f"初始化股票数据失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_stocks()
