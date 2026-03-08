# 缓存管理 API
from fastapi import APIRouter
from services.cache_service import cache

router = APIRouter(prefix="/api/cache", tags=["缓存管理"])

@router.get("/stats")
def get_cache_stats():
    """获取缓存统计"""
    return {"code": 0, "data": cache.get_stats()}

@router.post("/clear")
def clear_cache():
    """清空所有缓存"""
    success = cache.clear_all()
    return {"code": 0, "success": success, "message": "缓存已清空" if success else "清空失败"}

@router.delete("/clear/{pattern}")
def clear_pattern(pattern: str):
    """清除匹配的缓存"""
    success = cache.delete_pattern(f"*{pattern}*")
    return {"code": 0, "success": success, "pattern": pattern}
