# 缓存管理 API
"""
缓存管理接口
支持Redis和内存缓存
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# 尝试导入Redis缓存，如果失败则使用默认缓存
try:
    from services.redis_cache import cache as redis_cache
    cache = redis_cache
except ImportError:
    from utils.cache import cache

router = APIRouter(prefix="/api/cache", tags=["缓存管理"])

class CacheStatsResponse(BaseModel):
    status: str
    keys: int
    backend: Optional[str] = "memory"
    hits: Optional[int] = 0
    misses: Optional[int] = 0

@router.get("/stats", response_model=CacheStatsResponse)
def get_cache_stats():
    """
    获取缓存统计信息
    
    返回缓存状态、键数量、命中率等
    """
    stats = cache.get_stats()
    return {
        "status": stats.get("status", "unknown"),
        "keys": stats.get("keys", 0),
        "backend": stats.get("backend", "memory"),
        "hits": stats.get("hits", 0),
        "misses": stats.get("misses", 0)
    }

@router.post("/clear")
def clear_cache():
    """
    清空所有缓存
    """
    success = cache.clear_all()
    return {
        "code": 0,
        "success": success,
        "message": "缓存已清空" if success else "清空失败"
    }

@router.delete("/clear/{pattern}")
def clear_pattern(pattern: str):
    """
    清除匹配的缓存
    
    Args:
        pattern: 匹配模式，如 "stock" 清除所有包含 stock 的键
    """
    success = cache.delete_pattern(pattern)
    return {
        "code": 0,
        "success": success,
        "pattern": pattern,
        "message": f"已清除匹配的缓存: {pattern}"
    }

@router.get("/ping")
def ping_cache():
    """
    检查缓存连接状态
    """
    is_connected = cache.ping()
    return {
        "code": 0,
        "connected": is_connected,
        "backend": "redis" if is_connected else "memory"
    }

@router.post("/set")
def set_cache_value(
    key: str,
    value: str,
    ttl: int = 300
):
    """
    手动设置缓存值（仅用于调试）
    """
    cache.set(key, value, cache_type="default")
    return {
        "code": 0,
        "message": f"缓存已设置: {key}",
        "ttl": ttl
    }

@router.get("/get/{key}")
def get_cache_value(key: str):
    """
    获取缓存值（仅用于调试）
    """
    value = cache.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="缓存键不存在")
    return {
        "code": 0,
        "key": key,
        "value": value
    }
