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
    
    # 2. 缓存检查（Redis + 内存缓存）
    try:
        # 尝试导入Redis缓存
        try:
            from services.redis_cache import cache as redis_cache
            cache_to_check = redis_cache
            cache_stats = cache_to_check.get_stats()
            cache_status = "ok"
            cache_backend = cache_stats.get("backend", "unknown")
        except ImportError:
            from utils.cache import cache as memory_cache
            cache_to_check = memory_cache
            cache_stats = {"keys": cache_to_check.size()}
            cache_status = "ok"
            cache_backend = "memory"
        
        checks["checks"].append({
            "name": "cache", 
            "status": cache_status, 
            "keys": cache_stats.get("keys", 0),
            "backend": cache_backend
        })
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
