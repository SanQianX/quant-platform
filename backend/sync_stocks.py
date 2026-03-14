# 股票数据同步脚本
"""
从 Tushare 同步完整股票列表到数据库
运行方式: python sync_stocks.py
"""

import tushare as ts
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.stock import Stock
from utils.logger import logger

# Tushare Token 配置
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "87f3e60abf63e49dc8589ab903515d6e4cde5a07a54066845180d38b")

def init_tushare():
    """初始化 Tushare"""
    if TUSHARE_TOKEN:
        try:
            ts.set_token(TUSHARE_TOKEN)
            print("Tushare 初始化成功")
            return True
        except Exception as e:
            print(f"Tushare 初始化失败: {e}")
            return False
    else:
        print("未配置 TUSHARE_TOKEN")
        return False

def get_stock_list_from_tushare():
    """
    从 Tushare 获取完整股票列表
    
    Returns:
        list: 股票列表
    """
    pro = ts.pro_api()
    result = []
    
    try:
        # 获取上海A股 (上交所)
        print("正在获取上海A股列表...")
        df_sh = pro.stock_basic(exchange='SSE', list_status='L', 
                                fields='ts_code,symbol,name,area,industry,market,exchange,list_date')
        if df_sh is not None and not df_sh.empty:
            print(f"  上海A股: {len(df_sh)} 只")
            for _, row in df_sh.iterrows():
                ts_code = str(row.get('ts_code', ''))
                code = ts_code.replace('.SH', '') if ts_code else ''
                result.append({
                    "code": code,
                    "name": row.get('name', ''),
                    "market": "sh",
                    "stock_type": "stock",
                    "area": row.get('area', ''),
                    "industry": row.get('industry', '')
                })
        
        # 获取深圳A股 (深交所)
        print("正在获取深圳A股列表...")
        df_sz = pro.stock_basic(exchange='SZSE', list_status='L', 
                                fields='ts_code,symbol,name,area,industry,market,exchange,list_date')
        if df_sz is not None and not df_sz.empty:
            print(f"  深圳A股: {len(df_sz)} 只")
            for _, row in df_sz.iterrows():
                ts_code = str(row.get('ts_code', ''))
                code = ts_code.replace('.SZ', '') if ts_code else ''
                result.append({
                    "code": code,
                    "name": row.get('name', ''),
                    "market": "sz",
                    "stock_type": "stock",
                    "area": row.get('area', ''),
                    "industry": row.get('industry', '')
                })
        
        print(f"共获取 {len(result)} 只股票")
        return result
        
    except Exception as e:
        print(f"从 Tushare 获取股票列表失败: {e}")
        return []

def save_to_database(stocks):
    """
    将股票列表保存到数据库
    
    Args:
        stocks: 股票列表
        
    Returns:
        int: 保存的股票数量
    """
    db = SessionLocal()
    saved_count = 0
    updated_count = 0
    existed_count = 0
    
    try:
        for stock_data in stocks:
            # 检查是否已存在
            existing = db.query(Stock).filter(Stock.code == stock_data['code']).first()
            
            if existing:
                # 更新现有记录
                existing.name = stock_data['name']
                existing.market = stock_data['market']
                existing.stock_type = stock_data['stock_type']
                updated_count += 1
            else:
                # 创建新记录
                stock = Stock(
                    code=stock_data['code'],
                    name=stock_data['name'],
                    market=stock_data['market'],
                    stock_type=stock_data['stock_type']
                )
                db.add(stock)
                saved_count += 1
            
            # 每1000条提交一次
            if (saved_count + updated_count) % 1000 == 0:
                db.commit()
                print(f"  已处理 {saved_count + updated_count} 条...")
        
        # 提交剩余数据
        db.commit()
        print(f"\n数据库操作完成: 新增 {saved_count} 条, 更新 {updated_count} 条")
        
        return saved_count + updated_count
        
    except Exception as e:
        db.rollback()
        print(f"保存到数据库失败: {e}")
        raise
    finally:
        db.close()

def main():
    """主函数"""
    print("=" * 50)
    print("股票数据同步脚本")
    print("=" * 50)
    
    # 1. 初始化 Tushare
    if not init_tushare():
        print("程序退出")
        return
    
    # 2. 从 Tushare 获取股票列表
    stocks = get_stock_list_from_tushare()
    if not stocks:
        print("未获取到股票数据，程序退出")
        return
    
    # 3. 保存到数据库
    print("\n开始保存到数据库...")
    count = save_to_database(stocks)
    
    print(f"\n同步完成! 共同步 {count} 只股票到数据库")

if __name__ == "__main__":
    main()
