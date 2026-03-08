# 缓存服务
import json
import hashlib
import os
from datetime import timedelta
from typing import Any, Optional

# 尝试导入 Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# 内存缓存后备
class MemoryCache:
    """内存缓存（Redis 不可用时使用）"""
    def __init__(self):
        self._cache = {}
    
    def get(self, key):
        return self._cache.get(key)
    
    def setex(self, key, ttl, value):
        self._cache[key] = value
    
    def delete(self, *keys):
        for key in keys:
            self._cache.pop(key, None)
    
    def keys(self, pattern):
        import fnmatch
        return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
    
    def flushdb(self):
        self._cache.clear()
    
    def dbsize(self):
        return len(self._cache)
    
    def ping(self):
        return True

# Redis 配置
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

# 缓存配置
CACHE_TTL = {
    "stock_list": 3600,      # 股票列表: 1小时
    "stock_info": 7200,      # 股票信息: 2小时
    "kline_daily": 300,      # 日K线: 5分钟
    "kline_weekly": 1800,   # 周K线: 30分钟
    "kline_monthly": 3600,  # 月K线: 1小时
    "search": 600,          # 搜索结果: 10分钟
}

class CacheService:
    """缓存服务"""
    
    def __init__(self):
        self._client = None
        self._memory_cache = MemoryCache()
        self._use_memory = False
    
    @property
    def client(self):
        """延迟初始化 Redis 连接"""
        if self._client is None and not self._use_memory:
            try:
                self._client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    password=REDIS_PASSWORD,
                    decode_responses=True,
                    socket_connect_timeout=3,
                    socket_timeout=3
                )
                # 测试连接
                self._client.ping()
                print("Redis 连接成功")
            except Exception as e:
                print(f"Redis 连接失败，使用内存缓存: {e}")
                self._use_memory = True
                self._client = self._memory_cache
        return self._client
    
    def _generate_key(self, prefix: str, *args) -> str:
        """生成缓存键"""
        key_parts = [prefix] + [str(arg) for arg in args]
        key_str = ":".join(key_parts)
        # 哈希处理长键
        if len(key_str) > 200:
            hash_suffix = hashlib.md5(key_str.encode()).hexdigest()[:8]
            return f"{prefix}:{hash_suffix}"
        return key_str
    
    def get(self, prefix: str, *args) -> Optional[Any]:
        """获取缓存"""
        try:
            key = self._generate_key(prefix, *args)
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"缓存读取失败: {e}")
        return None
    
    def set(self, prefix: str, value: Any, cache_type: str = "default", *args):
        """设置缓存"""
        try:
            key = self._generate_key(prefix, *args)
            ttl = CACHE_TTL.get(cache_type, 300)
            serialized = json.dumps(value, default=str)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"缓存写入失败: {e}")
            return False
    
    def delete(self, prefix: str, *args):
        """删除缓存"""
        try:
            key = self._generate_key(prefix, *args)
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"缓存删除失败: {e}")
            return False
    
    def delete_pattern(self, pattern: str):
        """删除匹配的所有缓存"""
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
            return True
        except Exception as e:
            print(f"缓存批量删除失败: {e}")
            return False
    
    def clear_all(self):
        """清空所有缓存"""
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            print(f"清空缓存失败: {e}")
            return False
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        try:
            if self._use_memory:
                return {
                    "status": "memory",
                    "keys": self.client.dbsize(),
                }
            info = self.client.info("stats")
            return {
                "status": "redis",
                "keys": self.client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


# 全局缓存实例
cache = CacheService()


# 缓存装饰器
def cached(prefix: str, cache_type: str = "default"):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 尝试从缓存获取
            cache_key = args if args else ()
            cached_value = cache.get(prefix, *cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 写入缓存
            if result:
                cache.set(prefix, result, cache_type, *cache_key)
            
            return result
        return wrapper
    return decorator
