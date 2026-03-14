# -*- coding: utf-8 -*-
"""
K线数据下载脚本
从 Tushare 下载日K、周K、月K数据
如果权限不够，使用 AkShare 下载分时数据

运行方式: 
    python sync_kline.py                    # 下载所有配置股票的数据
    python sync_kline.py --stock 600519     # 下载指定股票
    python sync_kline.py --type daily       # 只下载日K
    python sync_kline.py --freq 5min        # 下载5分钟分时数据
    python sync_kline.py --batch            # 批量下载100只热门股票
    python sync_kline.py --batch --limit 150 # 批量下载150只热门股票
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd
import tushare as ts
import akshare as ak
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, db_config, Base
from models.stock import Stock
from models.kline import KLineDaily, KLineWeekly, KLineMonthly, KLineMinute
from utils.logger import logger

# Tushare Token 配置
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "87f3e60abf63e49dc8589ab903515d6e4cde5a07a54066845180d38b")

# PostgreSQL连接 - 直接使用PostgreSQL
POSTGRES_URL = "postgresql://quant_user:quant_pass@localhost:5432/quant_platform"

# 创建PostgreSQL引擎和会话
pg_engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
PgSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)

# 默认配置
DEFAULT_START_DATE = "20240101"
DEFAULT_END_DATE = datetime.now().strftime("%Y%m%d")
DEFAULT_STOCKS = [
    {"code": "600519", "name": "贵州茅台"},
    {"code": "000001", "name": "平安银行"},
    {"code": "300750", "name": "宁德时代"},
    {"code": "600036", "name": "招商银行"},
    {"code": "601318", "name": "中国平安"},
    {"code": "000858", "name": "五粮液"},
    {"code": "002594", "name": "比亚迪"},
    {"code": "600900", "name": "长江电力"},
]

# 沪深300成分股代码列表 (部分)
HS300_STOCKS = [
    {"code": "600519", "name": "贵州茅台"},
    {"code": "600036", "name": "招商银行"},
    {"code": "601318", "name": "中国平安"},
    {"code": "000001", "name": "平安银行"},
    {"code": "000002", "name": "万科A"},
    {"code": "000333", "name": "美的集团"},
    {"code": "000651", "name": "格力电器"},
    {"code": "000858", "name": "五粮液"},
    {"code": "002594", "name": "比亚迪"},
    {"code": "002415", "name": "海康威视"},
    {"code": "300059", "name": "东方财富"},
    {"code": "300015", "name": "爱尔眼科"},
    {"code": "300750", "name": "宁德时代"},
    {"code": "600030", "name": "中信证券"},
    {"code": "600016", "name": "民生银行"},
    {"code": "600028", "name": "中国石化"},
    {"code": "600031", "name": "三一重工"},
    {"code": "600048", "name": "保利发展"},
    {"code": "600050", "name": "中国联通"},
    {"code": "600104", "name": "上汽集团"},
    {"code": "600176", "name": "中国巨石"},
    {"code": "600309", "name": "万华化学"},
    {"code": "600406", "name": "国电南瑞"},
    {"code": "600585", "name": "海螺水泥"},
    {"code": "600690", "name": "青岛海尔"},
    {"code": "600887", "name": "伊利股份"},
    {"code": "600900", "name": "长江电力"},
    {"code": "601012", "name": "隆基绿能"},
    {"code": "601088", "name": "上海机场"},
    {"code": "601166", "name": "兴业银行"},
    {"code": "601169", "name": "北京银行"},
    {"code": "601288", "name": "农业银行"},
    {"code": "601328", "name": "交通银行"},
    {"code": "601398", "name": "工商银行"},
    {"code": "601601", "name": "中国太保"},
    {"code": "601628", "name": "中国人寿"},
    {"code": "601668", "name": "中国建筑"},
    {"code": "601766", "name": "中国中车"},
    {"code": "601816", "name": "京沪高铁"},
    {"code": "601818", "name": "光大银行"},
    {"code": "601857", "name": "中国石油"},
    {"code": "601888", "name": "中国中铁"},
    {"code": "601939", "name": "建设银行"},
    {"code": "601988", "name": "中国银行"},
    {"code": "000063", "name": "中兴通讯"},
    {"code": "000100", "name": "TCL科技"},
    {"code": "000333", "name": "美的集团"},
    {"code": "000338", "name": "潍柴动力"},
    {"code": "000538", "name": "云南白药"},
    {"code": "000568", "name": "泸州老窖"},
    {"code": "000596", "name": "古井贡酒"},
    {"code": "000651", "name": "格力电器"},
    {"code": "000661", "name": "长春高新"},
    {"code": "000725", "name": "京东方A"},
    {"code": "000858", "name": "五粮液"},
    {"code": "000876", "name": "新希望"},
    {"code": "000938", "name": "紫光国微"},
    {"code": "002001", "name": "新和成"},
    {"code": "002027", "name": "分众传媒"},
    {"code": "002044", "name": "江苏国泰"},
    {"code": "002049", "name": "紫光国微"},
    {"code": "002050", "name": "三花智控"},
    {"code": "002142", "name": "棉花业"},
    {"code": "002230", "name": "科大讯飞"},
    {"code": "002236", "name": "大华股份"},
    {"code": "002252", "name": "上海莱士"},
    {"code": "002304", "name": "南山控股"},
    {"code": "002311", "name": "海大集团"},
    {"code": "002371", "name": "北方华创"},
    {"code": "002385", "name": "大北农"},
    {"code": "002399", "name": "高伟达"},
    {"code": "002415", "name": "海康威视"},
    {"code": "002460", "name": "赣锋锂业"},
    {"code": "002475", "name": "立讯精密"},
    {"code": "002493", "name": "恒逸石化"},
    {"code": "002594", "name": "比亚迪"},
    {"code": "002601", "name": "龙蟒佰利"},
    {"code": "002714", "name": "牧原股份"},
    {"code": "002736", "name": "国光电器"},
    {"code": "002812", "name": "恩捷股份"},
    {"code": "002841", "name": "视源股份"},
    {"code": "002925", "name": "盈趣科技"},
    {"code": "300015", "name": "爱尔眼科"},
    {"code": "300033", "name": "同花顺"},
    {"code": "300059", "name": "东方财富"},
    {"code": "300122", "name": "智飞生物"},
    {"code": "300124", "name": "汇川技术"},
    {"code": "300142", "name": "沃森生物"},
    {"code": "300166", "name": "东方国信"},
    {"code": "300251", "name": "光线传媒"},
    {"code": "300347", "name": "泰格医药"},
    {"code": "300408", "name": "三环集团"},
    {"code": "300433", "name": "蓝思科技"},
    {"code": "300454", "name": "网宿科技"},
    {"code": "300498", "name": "中科曙光"},
    {"code": "300529", "name": "健帆生物"},
    {"code": "300595", "name": "欧普康视"},
    {"code": "300601", "name": "康泰生物"},
    {"code": "300750", "name": "宁德时代"},
    {"code": "300760", "name": "迈瑞医疗"},
    {"code": "300896", "name": "爱美客"},
]


class KLineDataSync:
    """K线数据同步类"""
    
    def __init__(self):
        self.tushare_available = False
        self._init_tushare()
    
    def _init_tushare(self):
        """初始化 Tushare"""
        try:
            ts.set_token(TUSHARE_TOKEN)
            self.pro = ts.pro_api()
            # 测试连接
            self.pro.daily(ts_code='600519.SH', start_date='20240301', end_date='20240302')
            self.tushare_available = True
            print("[OK] Tushare initialized successfully")
        except Exception as e:
            print(f"[WARN] Tushare initialization failed: {e}")
            print("[INFO] Will use AkShare as fallback")
            self.tushare_available = False
    
    def _get_ts_code(self, stock_code: str) -> str:
        """获取 Tushare 格式的股票代码"""
        # 判断市场
        if stock_code.startswith('6'):
            return f"{stock_code}.SH"
        else:
            return f"{stock_code}.SZ"
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        if isinstance(date_str, datetime):
            return date_str
        if isinstance(date_str, (int, float)):
            return pd.to_datetime(str(int(date_str)), format='%Y%m%d')
        return pd.to_datetime(date_str, format='%Y%m%d')
    
    def download_daily(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """下载日K线数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            DataFrame: 日K线数据
        """
        ts_code = self._get_ts_code(stock_code)
        
        try:
            if self.tushare_available:
                df = self.pro.daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date
                )
                if df is not None and not df.empty:
                    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
                    df['stock_code'] = stock_code
                    return df
            else:
                # 使用 AkShare 作为备选
                return self._download_daily_akshare(stock_code, start_date, end_date)
        except Exception as e:
            print(f"[ERROR] Download daily data failed for {stock_code}: {e}")
            # 尝试使用 AkShare
            try:
                return self._download_daily_akshare(stock_code, start_date, end_date)
            except Exception as e2:
                print(f"[ERROR] AkShare download also failed: {e2}")
        
        return pd.DataFrame()
    
    def _download_daily_akshare(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """使用 AkShare 下载日K线数据"""
        symbol = f"{stock_code}" if stock_code.startswith('6') else f"{stock_code}"
        
        # 转换为日期格式
        start = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
        
        try:
            df = ak.stock_zh_a_hist(symbol=symbol, start_date=start, end_date=end, adjust="qfq")
            if df is not None and not df.empty:
                # 重命名列
                df = df.rename(columns={
                    '日期': 'trade_date',
                    '股票代码': 'ts_code',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'vol',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '涨跌幅': 'pct_chg',
                    '涨跌额': 'change',
                    '换手率': 'turnover'
                })
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df['stock_code'] = stock_code
                return df
        except Exception as e:
            print(f"[ERROR] AkShare daily download failed: {e}")
        
        return pd.DataFrame()
    
    def download_weekly(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """下载周K线数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            DataFrame: 周K线数据
        """
        if not self.tushare_available:
            print("[WARN] Weekly data requires Tushare, skipping...")
            return pd.DataFrame()
        
        ts_code = self._get_ts_code(stock_code)
        
        try:
            df = self.pro.weekly(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            if df is not None and not df.empty:
                df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
                df['stock_code'] = stock_code
                return df
        except Exception as e:
            print(f"[ERROR] Download weekly data failed for {stock_code}: {e}")
        
        return pd.DataFrame()
    
    def download_monthly(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """下载月K线数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            DataFrame: 月K线数据
        """
        if not self.tushare_available:
            print("[WARN] Monthly data requires Tushare, skipping...")
            return pd.DataFrame()
        
        ts_code = self._get_ts_code(stock_code)
        
        try:
            df = self.pro.monthly(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            if df is not None and not df.empty:
                df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
                df['stock_code'] = stock_code
                return df
        except Exception as e:
            print(f"[ERROR] Download monthly data failed for {stock_code}: {e}")
        
        return pd.DataFrame()
    
    def download_minute(self, stock_code: str, freq: str = "5min", 
                       start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """下载分时数据
        
        Args:
            stock_code: 股票代码
            freq: 频率 (1min/5min/15min/30min/60min)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            DataFrame: 分时数据
        """
        symbol = f"{stock_code}" if stock_code.startswith('6') else f"{stock_code}"
        
        # 映射 AkShare 需要的频率参数
        freq_map = {
            "1min": "1",
            "5min": "5",
            "15min": "15",
            "30min": "30",
            "60min": "60"
        }
        
        akshare_freq = freq_map.get(freq, "5")
        
        try:
            # 使用 AkShare 获取分时数据
            df = ak.stock_zh_a_hist_min_em(
                symbol=symbol,
                period=akshare_freq,
                start_date=start_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                end_date=end_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                adjust="qfq"
            )
            
            if df is not None and not df.empty:
                # 重命名列
                df = df.rename(columns={
                    '时间': 'trade_time',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '涨跌幅': 'pct_chg',
                    '涨跌额': 'change',
                    '换手率': 'turnover'
                })
                df['trade_time'] = pd.to_datetime(df['trade_time'])
                df['trade_date'] = df['trade_time'].dt.date
                df['stock_code'] = stock_code
                df['freq'] = freq
                return df
        except Exception as e:
            print(f"[ERROR] Download minute data failed for {stock_code}: {e}")
        
        return pd.DataFrame()
    
    def save_daily(self, df: pd.DataFrame) -> int:
        """保存日K线数据到数据库
        
        Args:
            df: 日K线数据
            
        Returns:
            int: 保存的记录数
        """
        if df.empty:
            return 0
        
        db = PgSessionLocal()
        saved_count = 0
        
        try:
            for _, row in df.iterrows():
                # 检查是否已存在
                existing = db.query(KLineDaily).filter(
                    KLineDaily.stock_code == row.get('stock_code'),
                    KLineDaily.trade_date == row.get('trade_date')
                ).first()
                
                if existing:
                    # 更新
                    existing.open = row.get('open')
                    existing.high = row.get('high')
                    existing.low = row.get('low')
                    existing.close = row.get('close')
                    existing.pre_close = row.get('pre_close')
                    existing.change = row.get('change')
                    existing.pct_chg = row.get('pct_chg')
                    existing.vol = row.get('vol')
                    existing.amount = row.get('amount')
                else:
                    # 新增
                    kline = KLineDaily(
                        stock_code=row.get('stock_code'),
                        trade_date=row.get('trade_date'),
                        open=row.get('open'),
                        high=row.get('high'),
                        low=row.get('low'),
                        close=row.get('close'),
                        pre_close=row.get('pre_close'),
                        change=row.get('change'),
                        pct_chg=row.get('pct_chg'),
                        vol=row.get('vol'),
                        amount=row.get('amount')
                    )
                    db.add(kline)
                    saved_count += 1
                
                # 批量提交
                if saved_count % 100 == 0:
                    db.commit()
            
            db.commit()
            print(f"[OK] Daily data saved: {saved_count} records")
            return saved_count
            
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Save daily data failed: {e}")
            raise
        finally:
            db.close()
    
    def save_weekly(self, df: pd.DataFrame) -> int:
        """保存周K线数据到数据库"""
        if df.empty:
            return 0
        
        db = PgSessionLocal()
        saved_count = 0
        
        try:
            for _, row in df.iterrows():
                existing = db.query(KLineWeekly).filter(
                    KLineWeekly.stock_code == row.get('stock_code'),
                    KLineWeekly.trade_date == row.get('trade_date')
                ).first()
                
                if existing:
                    existing.open = row.get('open')
                    existing.high = row.get('high')
                    existing.low = row.get('low')
                    existing.close = row.get('close')
                    existing.vol = row.get('vol')
                    existing.amount = row.get('amount')
                    existing.pct_chg = row.get('pct_chg')
                else:
                    kline = KLineWeekly(
                        stock_code=row.get('stock_code'),
                        trade_date=row.get('trade_date'),
                        open=row.get('open'),
                        high=row.get('high'),
                        low=row.get('low'),
                        close=row.get('close'),
                        vol=row.get('vol'),
                        amount=row.get('amount'),
                        pct_chg=row.get('pct_chg')
                    )
                    db.add(kline)
                    saved_count += 1
            
            db.commit()
            print(f"[OK] Weekly data saved: {saved_count} records")
            return saved_count
            
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Save weekly data failed: {e}")
            raise
        finally:
            db.close()
    
    def save_monthly(self, df: pd.DataFrame) -> int:
        """保存月K线数据到数据库"""
        if df.empty:
            return 0
        
        db = PgSessionLocal()
        saved_count = 0
        
        try:
            for _, row in df.iterrows():
                existing = db.query(KLineMonthly).filter(
                    KLineMonthly.stock_code == row.get('stock_code'),
                    KLineMonthly.trade_date == row.get('trade_date')
                ).first()
                
                if existing:
                    existing.open = row.get('open')
                    existing.high = row.get('high')
                    existing.low = row.get('low')
                    existing.close = row.get('close')
                    existing.vol = row.get('vol')
                    existing.amount = row.get('amount')
                    existing.pct_chg = row.get('pct_chg')
                else:
                    kline = KLineMonthly(
                        stock_code=row.get('stock_code'),
                        trade_date=row.get('trade_date'),
                        open=row.get('open'),
                        high=row.get('high'),
                        low=row.get('low'),
                        close=row.get('close'),
                        vol=row.get('vol'),
                        amount=row.get('amount'),
                        pct_chg=row.get('pct_chg')
                    )
                    db.add(kline)
                    saved_count += 1
            
            db.commit()
            print(f"[OK] Monthly data saved: {saved_count} records")
            return saved_count
            
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Save monthly data failed: {e}")
            raise
        finally:
            db.close()
    
    def save_minute(self, df: pd.DataFrame) -> int:
        """保存分时数据到数据库"""
        if df.empty:
            return 0
        
        db = PgSessionLocal()
        saved_count = 0
        
        try:
            for _, row in df.iterrows():
                existing = db.query(KLineMinute).filter(
                    KLineMinute.stock_code == row.get('stock_code'),
                    KLineMinute.freq == row.get('freq'),
                    KLineMinute.trade_time == row.get('trade_time')
                ).first()
                
                if not existing:
                    kline = KLineMinute(
                        stock_code=row.get('stock_code'),
                        trade_date=row.get('trade_date'),
                        trade_time=row.get('trade_time'),
                        open=row.get('open'),
                        high=row.get('high'),
                        low=row.get('low'),
                        close=row.get('close'),
                        volume=row.get('volume'),
                        amount=row.get('amount'),
                        freq=row.get('freq')
                    )
                    db.add(kline)
                    saved_count += 1
                
                if saved_count % 500 == 0:
                    db.commit()
            
            db.commit()
            print(f"[OK] Minute data saved: {saved_count} records")
            return saved_count
            
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Save minute data failed: {e}")
            raise
        finally:
            db.close()
    
    def sync_stock(self, stock_code: str, start_date: str, end_date: str,
                   data_types: List[str], minute_freq: str = "5min") -> dict:
        """同步单个股票的数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            data_types: 数据类型列表 ['daily', 'weekly', 'monthly', 'minute']
            minute_freq: 分时频率
            
        Returns:
            dict: 同步结果统计
        """
        results = {
            'stock_code': stock_code,
            'daily': 0,
            'weekly': 0,
            'monthly': 0,
            'minute': 0
        }
        
        print(f"\n{'='*50}")
        print(f"Syncing data for stock: {stock_code}")
        print(f"Date range: {start_date} - {end_date}")
        print(f"{'='*50}")
        
        # 下载并保存日K
        if 'daily' in data_types:
            print(f"\n[INFO] Downloading daily data...")
            df_daily = self.download_daily(stock_code, start_date, end_date)
            if not df_daily.empty:
                results['daily'] = self.save_daily(df_daily)
                print(f"[OK] Daily: {len(df_daily)} records downloaded, {results['daily']} saved")
        
        # 下载并保存周K
        if 'weekly' in data_types:
            print(f"\n[INFO] Downloading weekly data...")
            df_weekly = self.download_weekly(stock_code, start_date, end_date)
            if not df_weekly.empty:
                results['weekly'] = self.save_weekly(df_weekly)
                print(f"[OK] Weekly: {len(df_weekly)} records downloaded, {results['weekly']} saved")
        
        # 下载并保存月K
        if 'monthly' in data_types:
            print(f"\n[INFO] Downloading monthly data...")
            df_monthly = self.download_monthly(stock_code, start_date, end_date)
            if not df_monthly.empty:
                results['monthly'] = self.save_monthly(df_monthly)
                print(f"[OK] Monthly: {len(df_monthly)} records downloaded, {results['monthly']} saved")
        
        # 下载并保存分时数据
        if 'minute' in data_types:
            print(f"\n[INFO] Downloading {minute_freq} minute data...")
            df_minute = self.download_minute(stock_code, minute_freq, start_date, end_date)
            if not df_minute.empty:
                results['minute'] = self.save_minute(df_minute)
                print(f"[OK] Minute: {len(df_minute)} records downloaded, {results['minute']} saved")
        
        return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='K线数据同步脚本')
    parser.add_argument('--stock', type=str, help='股票代码 (如: 600519)')
    parser.add_argument('--start', type=str, default=DEFAULT_START_DATE, help='开始日期 (YYYYMMDD)')
    parser.add_argument('--end', type=str, default=DEFAULT_END_DATE, help='结束日期 (YYYYMMDD)')
    parser.add_argument('--type', type=str, default='daily,weekly,monthly', 
                       help='数据类型,逗号分隔 (daily,weekly,monthly,minute)')
    parser.add_argument('--freq', type=str, default='5min', 
                       help='分时频率 (1min,5min,15min,30min,60min)')
    parser.add_argument('--batch', action='store_true', help='批量下载100只热门股票数据')
    parser.add_argument('--limit', type=int, default=100, help='批量下载时下载的股票数量 (默认100)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("K线数据同步脚本")
    print("=" * 60)
    
    # 解析数据类型
    data_types = [t.strip() for t in args.type.split(',')]
    
    # 确定要同步的股票列表
    stocks = []
    if args.stock:
        # 下载指定股票
        stocks = [{"code": args.stock}]
    elif args.batch:
        # 批量下载沪深300成分股
        stocks = HS300_STOCKS[:args.limit]
        print(f"[INFO] Batch mode: downloading {len(stocks)} popular stocks")
    else:
        # 从数据库获取股票列表
        db = PgSessionLocal()
        try:
            db_stocks = db.query(Stock).limit(10).all()
            for s in db_stocks:
                stocks.append({"code": s.code})
        except:
            stocks = DEFAULT_STOCKS
        finally:
            db.close()
    
    if not stocks:
        print("[ERROR] No stocks to sync")
        return
    
    print(f"Stocks to sync: {len(stocks)}")
    print(f"Date range: {args.start} - {args.end}")
    print(f"Data types: {data_types}")
    print(f"Minute frequency: {args.freq}")
    
    # 创建同步实例
    sync = KLineDataSync()
    
    # 同步数据
    total_results = []
    for stock in stocks:
        try:
            result = sync.sync_stock(
                stock['code'], 
                args.start, 
                args.end,
                data_types,
                args.freq
            )
            total_results.append(result)
        except Exception as e:
            print(f"[ERROR] Sync failed for {stock['code']}: {e}")
    
    # 打印汇总
    print("\n" + "=" * 60)
    print("同步完成!")
    print("=" * 60)
    for result in total_results:
        print(f"Stock {result['stock_code']}: "
              f"Daily={result['daily']}, "
              f"Weekly={result['weekly']}, "
              f"Monthly={result['monthly']}, "
              f"Minute={result['minute']}")


if __name__ == "__main__":
    main()
