# 数据采集定时任务
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pandas as pd
from database import SessionLocal
from models.stock import Stock, KLine
from services.stock_service import StockService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局调度器
scheduler = BackgroundScheduler()

class DataCollector:
    """数据采集器"""
    
    def __init__(self):
        self.retry_times = 3
        self.retry_delay = 5  # 秒
    
    def update_all_stocks(self, period: str = "daily"):
        """更新所有股票的K线数据"""
        db = SessionLocal()
        try:
            stocks = db.query(Stock).all()
            total = len(stocks)
            success = 0
            failed = 0
            
            logger.info(f"开始更新 {total} 只股票的 {period} 数据...")
            
            for i, stock in enumerate(stocks):
                try:
                    # 获取最新数据
                    klines = StockService.get_history_kline(
                        stock.code,
                        period=period,
                        start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                        end_date=datetime.now().strftime("%Y-%m-%d")
                    )
                    
                    if klines:
                        # 增量保存到数据库
                        for kline in klines:
                            existing = db.query(KLine).filter(
                                KLine.stock_code == stock.code,
                                KLine.date == kline['date']
                            ).first()
                            
                            if not existing:
                                new_kline = KLine(
                                    stock_code=stock.code,
                                    date=datetime.strptime(kline['date'], "%Y-%m-%d").date(),
                                    open=kline['open'],
                                    high=kline['high'],
                                    low=kline['low'],
                                    close=kline['close'],
                                    volume=kline['volume']
                                )
                                db.add(new_kline)
                        
                        db.commit()
                        success += 1
                    else:
                        failed += 1
                        
                    logger.info(f"进度: {i+1}/{total} - {stock.code} {'成功' if klines else '无数据'}")
                    
                except Exception as e:
                    logger.error(f"更新 {stock.code} 失败: {e}")
                    failed += 1
                    continue
            
            logger.info(f"更新完成: 成功 {success}, 失败 {failed}")
            return {"total": total, "success": success, "failed": failed}
            
        except Exception as e:
            logger.error(f"更新任务异常: {e}")
            db.rollback()
            return {"error": str(e)}
        finally:
            db.close()
    
    def update_single_stock(self, stock_code: str, period: str = "daily"):
        """更新单只股票数据"""
        try:
            logger.info(f"开始更新股票 {stock_code}...")
            
            klines = StockService.get_history_kline(
                stock_code,
                period=period,
                start_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                end_date=datetime.now().strftime("%Y-%m-%d")
            )
            
            if not klines:
                return {"code": stock_code, "status": "no_data"}
            
            # 保存到数据库
            db = SessionLocal()
            try:
                for kline in klines:
                    existing = db.query(KLine).filter(
                        KLine.stock_code == stock_code,
                        KLine.date == kline['date']
                    ).first()
                    
                    if not existing:
                        new_kline = KLine(
                            stock_code=stock_code,
                            date=datetime.strptime(kline['date'], "%Y-%m-%d").date(),
                            open=kline['open'],
                            high=kline['high'],
                            low=kline['low'],
                            close=kline['close'],
                            volume=kline['volume']
                        )
                        db.add(new_kline)
                
                db.commit()
                logger.info(f"股票 {stock_code} 更新完成，共 {len(klines)} 条数据")
                return {"code": stock_code, "status": "success", "count": len(klines)}
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"更新股票 {stock_code} 失败: {e}")
            return {"code": stock_code, "status": "error", "message": str(e)}
    
    def get_task_status(self):
        """获取任务状态"""
        jobs = scheduler.get_jobs()
        return {
            "running": scheduler.running,
            "jobs": [
                {
                    "id": job.id,
                    "next_run": str(job.next_run_time) if job.next_run_time else None
                }
                for job in jobs
            ]
        }


# 全局采集器实例
collector = DataCollector()


def start_scheduler():
    """启动定时任务"""
    if scheduler.running:
        logger.warning("调度器已在运行中")
        return
    
    # 每天 16:00 执行（日盘收盘后）
    trigger = CronTrigger(hour=16, minute=0)
    scheduler.add_job(
        collector.update_all_stocks,
        trigger=trigger,
        id="daily_update",
        name="每日股票数据更新",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("定时任务已启动 - 每天 16:00 执行")


def stop_scheduler():
    """停止定时任务"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务已停止")


def trigger_manual_update(period: str = "daily"):
    """手动触发更新"""
    return collector.update_all_stocks(period)


def get_scheduler_status():
    """获取调度器状态"""
    return collector.get_task_status()
