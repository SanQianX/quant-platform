# 缓存管理 API
from fastapi import APIRouter
from utils.cache import cache

router = APIRouter(prefix="/api/cache", tags=["缓存管理"])

@router.get("/stats")
def get_cache_stats():
    """获取缓存统计"""
    return {"code": 0, "data": {"keys": cache.size()}}

@router.post("/clear")
def clear_cache():
    """清空所有缓存"""
    cache.clear()
    return {"code": 0, "success": True, "message": "缓存已清空"}

@router.delete("/clear/{pattern}")
def clear_pattern(pattern: str):
    """清除匹配的缓存（暂不支持pattern，使用clear代替）"""
    cache.clear()
    return {"code": 0, "success": True, "pattern": pattern}
