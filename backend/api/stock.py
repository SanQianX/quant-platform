# 股票API路由
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
import io
import csv
import json
from services.stock_service import StockService

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票"])

@router.get("/list")
def get_stock_list():
    """
    获取股票列表
    
    返回所有支持的股票和指数列表
    
    Returns:
        dict: 统一响应格式，包含股票列表
    """
    return StockService.get_stock_list()

@router.get("/search")
def search_stocks(keyword: str = Query(..., min_length=1, description="搜索关键词（股票代码或名称）")):
    """
    搜索股票
    
    根据关键词搜索股票，支持代码和名称模糊匹配
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        dict: 统一响应格式，包含匹配的股票列表
    """
    return StockService.search_stocks(keyword)

@router.get("/{code}/export")
def export_stock_kline(code: str, format: str = Query("csv", regex="^(csv|json)$", description="导出格式: csv 或 json")):
    """
    导出股票K线数据
    
    将指定股票的K线数据导出为CSV或JSON格式
    
    Args:
        code: 股票代码
        format: 导出格式 (csv/json)
        
    Returns:
        StreamingResponse: 文件下载响应
    """
    # 验证格式
    if format not in ["csv", "json"]:
        raise HTTPException(status_code=400, detail="格式只能是 csv 或 json")
    
    # 获取数据
    response = StockService.get_kline_data(code)
    
    # 检查是否成功
    if response.get("code") != 0:
        raise HTTPException(status_code=404, detail=response.get("message", "获取数据失败"))
    
    klines = response.get("data", [])
    
    # 根据格式导出
    if format == "json":
        json_str = json.dumps(klines, ensure_ascii=False, indent=2)
        return StreamingResponse(
            io.BytesIO(json_str.encode('utf-8')),
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
    """
    获取股票K线数据
    
    获取指定股票的日K线数据（开盘、收盘、最高、最低、成交量）
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含K线数据列表
    """
    return StockService.get_kline_data(code)
