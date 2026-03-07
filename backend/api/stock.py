# 股票API路由
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
import io
import csv
import json
from services.stock_service import StockService

router = APIRouter(prefix="/api/stock", tags=["股票"])

@router.get("/list")
def get_stock_list():
    """获取股票列表"""
    stocks = StockService.get_stock_list()
    return {"code": 0, "data": stocks}

@router.get("/search")
def search_stocks(keyword: str = Query(..., description="搜索关键词")):
    """搜索股票"""
    stocks = StockService.search_stocks(keyword)
    return {"code": 0, "data": stocks}

# 导出接口必须在/{code}之前定义
@router.get("/{code}/export")
def export_stock_kline(code: str, format: str = Query("csv", description="导出格式: csv/json")):
    """导出股票K线数据"""
    klines = StockService.get_kline_data(code)
    
    if format == "json":
        return StreamingResponse(
            io.BytesIO(json.dumps(klines, ensure_ascii=False).encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={code}_kline.json"}
        )
    
    # CSV格式
    output = io.StringIO()
    if klines:
        writer = csv.DictWriter(output, fieldnames=klines[0].keys())
        writer.writeheader()
        writer.writerows(klines)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={code}_kline.csv"}
    )

@router.get("/{code}")
def get_stock_kline(code: str):
    """获取股票K线数据"""
    klines = StockService.get_kline_data(code)
    return {"code": 0, "data": klines}
