# 定时任务 API
from fastapi import APIRouter, Query
from typing import Optional
from scheduler.tasks import (
    start_scheduler, 
    stop_scheduler, 
    trigger_manual_update,
    get_scheduler_status,
    collector
)

router = APIRouter(prefix="/api/scheduler", tags=["定时任务"])

@router.get("/status")
def get_status():
    """获取定时任务状态"""
    return get_scheduler_status()

@router.post("/start")
def start():
    """启动定时任务"""
    start_scheduler()
    return {"message": "定时任务已启动"}

@router.post("/stop")
def stop():
    """停止定时任务"""
    stop_scheduler()
    return {"message": "定时任务已停止"}

@router.post("/trigger")
def trigger(period: str = Query("daily", description="数据类型: daily/weekly/monthly")):
    """手动触发数据更新"""
    result = trigger_manual_update(period)
    return {"code": 0, "data": result}

@router.post("/update/{stock_code}")
def update_stock(
    stock_code: str,
    period: str = Query("daily", description="数据类型: daily/weekly/monthly")
):
    """更新单只股票数据"""
    result = collector.update_single_stock(stock_code, period)
    return {"code": 0, "data": result}

@router.get("/jobs")
def list_jobs():
    """列出所有定时任务"""
    status = get_scheduler_status()
    return {"code": 0, "data": status}
