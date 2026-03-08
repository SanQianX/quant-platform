# 数据导出 API
"""
股票数据导出功能
支持 CSV 和 JSON 格式
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from services.stock_service import StockService
from models.response import success_response, error_response
import io
import csv
import json

router = APIRouter(prefix="/api/stock", tags=["股票导出"])

@router.get("/{code}/export")
def export_stock_data(
    code: str,
    format: str = Query("csv", description="导出格式: csv/json"),
    period: str = Query("daily", description="K线周期: daily/weekly/monthly"),
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD")
):
    """
    导出股票数据
    
    Args:
        code: 股票代码
        format: 导出格式 (csv/json)
        period: K线周期
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        文件下载响应
    """
    # 获取数据
    result = StockService.get_history_kline(code, period, start_date, end_date)
    
    # 检查返回格式
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message", "获取数据失败"))
        data = result.get("data", [])
    else:
        data = result
    
    if not data:
        raise HTTPException(status_code=404, detail="没有数据可导出")
    
    # 导出格式
    if format.lower() == "csv":
        return export_csv(code, data)
    elif format.lower() == "json":
        return export_json(code, data)
    else:
        raise HTTPException(status_code=400, detail="不支持的格式，请使用 csv 或 json")


def export_csv(code: str, data: list):
    """导出为CSV格式"""
    output = io.StringIO()
    
    # 写入CSV表头
    fieldnames = ["date", "open", "high", "low", "close", "volume"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    # 写入数据
    for row in data:
        writer.writerow({
            "date": row.get("date", ""),
            "open": row.get("open", 0),
            "high": row.get("high", 0),
            "low": row.get("low", 0),
            "close": row.get("close", 0),
            "volume": row.get("volume", 0)
        })
    
    # 生成响应
    output.seek(0)
    filename = f"stock_{code}_{len(data)}rows.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8-sig"
        }
    )


def export_json(code: str, data: list):
    """导出为JSON格式"""
    output = {
        "stock_code": code,
        "total_rows": len(data),
        "data": data
    }
    
    json_str = json.dumps(output, ensure_ascii=False, indent=2)
    filename = f"stock_{code}_{len(data)}rows.json"
    
    return StreamingResponse(
        io.BytesIO(json_str.encode("utf-8")),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/json; charset=utf-8"
        }
    )


@router.post("/export/batch")
def export_batch_data(
    codes: list[str] = Query(..., description="股票代码列表"),
    format: str = Query("csv", description="导出格式: csv/json"),
    period: str = Query("daily", description="K线周期")
):
    """
    批量导出多只股票数据
    
    Args:
        codes: 股票代码列表
        format: 导出格式
        period: K线周期
        
    Returns:
        合并的导出文件
    """
    all_data = []
    
    for code in codes:
        result = StockService.get_history_kline(code, period)
        
        if isinstance(result, dict) and result.get("code") == 0:
            data = result.get("data", [])
            for row in data:
                row["stock_code"] = code
            all_data.extend(data)
    
    if not all_data:
        raise HTTPException(status_code=404, detail="没有数据可导出")
    
    if format.lower() == "csv":
        return export_csv("batch", all_data)
    else:
        return export_json("batch", all_data)
