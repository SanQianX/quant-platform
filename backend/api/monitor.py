# 监控指标 API
from fastapi import APIRouter
from utils.metrics import metrics
from utils.cache import cache

router = APIRouter(prefix="/api/monitor", tags=["监控"])

@router.get("/metrics")
def get_metrics():
    """
    获取性能指标
    
    返回:
    - 请求统计（总数、错误数、错误率）
    - 响应时间（平均、P95）
    - 缓存统计（命中、未命中、命中率）
    - 各端点统计
    """
    return {
        "code": 0,
        "data": metrics.get_metrics()
    }

@router.post("/metrics/reset")
def reset_metrics():
    """重置所有指标"""
    metrics.reset()
    return {
        "code": 0,
        "message": "指标已重置"
    }

@router.get("/health/detailed")
def detailed_health():
    """详细健康检查"""
    import os
    import sys
    
    # 检查各项依赖
    checks = {
        "status": "healthy",
        "checks": []
    }
    
    # 1. 数据库检查
    try:
        from database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["checks"].append({"name": "database", "status": "ok"})
    except Exception as e:
        checks["checks"].append({"name": "database", "status": "error", "message": str(e)})
        checks["status"] = "unhealthy"
    
    # 2. 缓存检查
    try:
        cache_size = cache.size()
        checks["checks"].append({"name": "cache", "status": "ok", "keys": cache_size})
    except Exception as e:
        checks["checks"].append({"name": "cache", "status": "error", "message": str(e)})
    
    # 3. Tushare 检查
    try:
        from services.stock_service import _tushare_initialized
        if _tushare_initialized:
            checks["checks"].append({"name": "tushare", "status": "ok"})
        else:
            checks["checks"].append({"name": "tushare", "status": "warning", "message": "未初始化"})
    except Exception as e:
        checks["checks"].append({"name": "tushare", "status": "error", "message": str(e)})
    
    # 4. 系统信息
    checks["system"] = {
        "python_version": sys.version,
        "platform": os.name
    }
    
    return {
        "code": 0 if checks["status"] == "healthy" else 1,
        "data": checks
    }
