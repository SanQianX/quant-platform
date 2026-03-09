# 简单缓存实现
"""
简单内存缓存模块
用于缓存股票数据，减少重复查询
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import threading

class SimpleCache:
    """简单内存缓存"""
    
    def __init__(self, default_ttl: int = 300):
        """
        初始化缓存
        
        Args:
            default_ttl: 默认过期时间(秒)，默认5分钟
        """
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._lock = threading.Lock()
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或过期返回None
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expire_time = self._cache[key]
            
            # 检查是否过期
            if datetime.now() > expire_time:
                del self._cache[key]
                return None
            
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间(秒)，默认使用配置的default_ttl
        """
        with self._lock:
            expire_time = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
            self._cache[key] = (value, expire_time)
    
    def delete(self, key: str):
        """删除缓存"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """返回缓存数量"""
        with self._lock:
            return len(self._cache)

    def get_stats(self):
        """获取缓存统计"""
        with self._lock:
            return {
                "status": "ok",
                "keys": len(self._cache),
                "backend": "memory"
            }

    def clear_all(self):
        """清空所有缓存"""
        self.clear()
        return True

    def delete_pattern(self, pattern: str):
        """删除匹配的缓存"""
        with self._lock:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for k in keys_to_delete:
                del self._cache[k]
            return True

    def ping(self):
        """检查缓存连接状态"""
        return {"connected": True, "backend": "memory"}


# 创建全局缓存实例
cache = SimpleCache(default_ttl=300)
