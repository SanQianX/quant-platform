# Redis缓存服务
"""
Redis缓存集成
支持内存缓存降级
"""

import json
import hashlib
from typing import Any, Optional
import os

# Redis配置
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
    "default": 300,         # 默认: 5分钟
}

class RedisCache:
    """Redis缓存服务"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        """初始化"""
        self._client = None
        self._use_memory = False
        self._memory_cache = {}
    
    def _get_client(self):
        """获取Redis客户端"""
        if self._client is None and not self._use_memory:
            try:
                import redis
                self._client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    password=REDIS_PASSWORD,
                    decode_responses=True,
                    socket_connect_timeout=3,
                    socket_timeout=3,
                    socket_keepalive=True
                )
                # 测试连接
                self._client.ping()
                print(f"Redis连接成功: {REDIS_HOST}:{REDIS_PORT}")
            except Exception as e:
                print(f"Redis连接失败，使用内存缓存: {e}")
                self._use_memory = True
                self._client = None
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
        client = self._get_client()
        
        if self._use_memory or not client:
            # 使用内存缓存
            key = self._generate_key(prefix, *args)
            return self._memory_cache.get(key)
        
        try:
            key = self._generate_key(prefix, *args)
            value = client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Redis读取失败: {e}")
            # 降级到内存
            key = self._generate_key(prefix, *args)
            return self._memory_cache.get(key)
        return None
    
    def set(self, prefix: str, value: Any, cache_type: str = "default", *args):
        """设置缓存"""
        client = self._get_client()
        key = self._generate_key(prefix, *args)
        ttl = CACHE_TTL.get(cache_type, CACHE_TTL["default"])
        
        # 同时写入内存缓存（备用）
        self._memory_cache[key] = value
        
        if self._use_memory or not client:
            return True
        
        try:
            serialized = json.dumps(value, default=str)
            client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Redis写入失败: {e}")
            return False
    
    def delete(self, prefix: str, *args):
        """删除缓存"""
        client = self._get_client()
        key = self._generate_key(prefix, *args)
        
        # 删除内存缓存
        self._memory_cache.pop(key, None)
        
        if self._use_memory or not client:
            return True
        
        try:
            client.delete(key)
            return True
        except Exception as e:
            print(f"Redis删除失败: {e}")
            return False
    
    def delete_pattern(self, pattern: str):
        """删除匹配的所有缓存"""
        client = self._get_client()
        
        if self._use_memory or not client:
            # 内存缓存模式
            keys_to_delete = [k for k in self._memory_cache.keys() if pattern.replace("*", "") in k]
            for key in keys_to_delete:
                del self._memory_cache[key]
            return True
        
        try:
            # 使用scan避免阻塞
            cursor = 0
            while True:
                cursor, keys = client.scan(cursor, match=f"*{pattern}*", count=100)
                if keys:
                    client.delete(*keys)
                if cursor == 0:
                    break
            return True
        except Exception as e:
            print(f"Redis批量删除失败: {e}")
            return False
    
    def clear_all(self):
        """清空所有缓存"""
        client = self._get_client()
        
        # 清空内存缓存
        self._memory_cache.clear()
        
        if self._use_memory or not client:
            return True
        
        try:
            client.flushdb()
            return True
        except Exception as e:
            print(f"Redis清空失败: {e}")
            return False
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        client = self._get_client()
        
        if self._use_memory or not client:
            return {
                "status": "memory",
                "keys": len(self._memory_cache),
                "backend": "memory"
            }
        
        try:
            info = client.info("stats")
            return {
                "status": "redis",
                "keys": client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "backend": "redis",
                "host": REDIS_HOST,
                "port": REDIS_PORT
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def size(self) -> int:
        """获取缓存大小"""
        client = self._get_client()
        
        if self._use_memory or not client:
            return len(self._memory_cache)
        
        try:
            return client.dbsize()
        except:
            return len(self._memory_cache)
    
    def ping(self) -> bool:
        """检查Redis连接"""
        client = self._get_client()
        
        if self._use_memory or not client:
            return True
        
        try:
            return client.ping()
        except:
            return False


# 全局缓存实例
cache = RedisCache()
