# 数据导出增强 API
"""
增强的数据导出功能
支持批量导出和定时任务查询
"""

from fastapi import APIRouter, Query, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
from services.stock_service import StockService
from scheduler.tasks import scheduler, get_scheduler_status
import io
import csv
import json

router = APIRouter(prefix="/api", tags=["数据导出增强"])


# ============ 请求模型 ============

class BatchExportRequest(BaseModel):
    """批量导出请求"""
    codes: List[str] = Body(..., description="股票代码列表")
    format: str = Body("csv", description="导出格式: csv/json")
    period: str = Body("daily", description="K线周期: daily/weekly/monthly")
    start_date: Optional[str] = Body(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Body(None, description="结束日期 YYYY-MM-DD")


# ============ 批量导出 ============

@router.post("/export/batch")
def export_batch(
    request: BatchExportRequest
):
    """
    批量导出多只股票数据
    
    Args:
        request: 批量导出请求，包含股票代码列表、格式、周期等
        
    Returns:
        合并的导出文件
    """
    codes = request.codes
    export_format = request.format
    period = request.period
    start_date = request.start_date
    end_date = request.end_date
    
    if not codes or len(codes) == 0:
        raise HTTPException(status_code=400, detail="股票代码列表不能为空")
    
    if len(codes) > 50:
        raise HTTPException(status_code=400, detail="单次最多支持50只股票")
    
    all_data = []
    failed_stocks = []
    
    for code in codes:
        try:
            result = StockService.get_history_kline(
                code, 
                period, 
                start_date=start_date, 
                end_date=end_date
            )
            
            if isinstance(result, dict):
                if result.get("code") != 0:
                    failed_stocks.append({"code": code, "error": result.get("message", "获取数据失败")})
                    continue
                data = result.get("data", [])
            else:
                data = result or []
            
            # 添加股票代码标记
            for row in data:
                if isinstance(row, dict):
                    row["stock_code"] = code
            
            all_data.extend(data)
            
        except Exception as e:
            failed_stocks.append({"code": code, "error": str(e)})
    
    if not all_data:
        raise HTTPException(status_code=404, detail="没有数据可导出")
    
    # 导出格式
    if export_format.lower() == "csv":
        return export_csv_batch(codes, all_data)
    elif export_format.lower() == "json":
        return export_json_batch(codes, all_data)
    else:
        raise HTTPException(status_code=400, detail="不支持的格式，请使用 csv 或 json")


def export_csv_batch(codes: list, data: list):
    """批量导出为CSV格式"""
    output = io.StringIO()
    
    # 写入CSV表头
    fieldnames = ["stock_code", "date", "open", "high", "low", "close", "volume"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    # 写入数据
    for row in data:
        writer.writerow({
            "stock_code": row.get("stock_code", ""),
            "date": row.get("date", ""),
            "open": row.get("open", 0),
            "high": row.get("high", 0),
            "low": row.get("low", 0),
            "close": row.get("close", 0),
            "volume": row.get("volume", 0)
        })
    
    # 生成响应
    output.seek(0)
    filename = f"batch_export_{len(codes)}stocks_{len(data)}rows.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8-sig"
        }
    )


def export_json_batch(codes: list, data: list):
    """批量导出为JSON格式"""
    output = {
        "stocks": codes,
        "total_stocks": len(codes),
        "total_rows": len(data),
        "data": data
    }
    
    json_str = json.dumps(output, ensure_ascii=False, indent=2)
    filename = f"batch_export_{len(codes)}stocks_{len(data)}rows.json"
    
    return StreamingResponse(
        io.BytesIO(json_str.encode("utf-8")),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/json; charset=utf-8"
        }
    )


# ============ 定时任务 ============

@router.get("/scheduler/tasks")
def get_scheduler_tasks():
    """
    获取定时任务列表
    
    Returns:
        定时任务列表信息
    """
    try:
        # 获取调度器状态
        status = get_scheduler_status()
        
        # 获取所有任务详情
        jobs = scheduler.get_jobs()
        
        tasks = []
        for job in jobs:
            task_info = {
                "id": job.id,
                "name": getattr(job, 'name', job.id),
                "next_run": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger) if hasattr(job, 'trigger') else None
            }
            
            # 解析trigger获取更多信息
            if hasattr(job, 'trigger') and job.trigger:
                trigger = job.trigger
                if hasattr(trigger, 'fields'):
                    # CronTrigger
                    fields = trigger.fields
                    cron_info = {}
                    for field in fields:
                        cron_info[field.name] = str(field)
                    task_info["cron"] = cron_info
            
            tasks.append(task_info)
        
        return {
            "code": 0,
            "data": {
                "running": scheduler.running,
                "total_tasks": len(tasks),
                "tasks": tasks
            }
        }
        
    except Exception as e:
        return {
            "code": -1,
            "message": f"获取定时任务失败: {str(e)}",
            "data": None
        }


# 导入StreamingResponse
from fastapi.responses import StreamingResponse
