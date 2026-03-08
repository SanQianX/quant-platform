# 监控指标模块
"""
性能监控和指标统计
"""

import time
from typing import Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
from threading import Lock

class Metrics:
    """性能指标收集器"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance
    
    def _init(self):
        """初始化"""
        self._request_count = 0
        self._error_count = 0
        self._total_response_time = 0.0
        self._response_times = []
        self._endpoint_stats = defaultdict(lambda: {"count": 0, "errors": 0, "total_time": 0.0})
        self._cache_hits = 0
        self._cache_misses = 0
        self._start_time = datetime.now()
    
    def record_request(self, endpoint: str, response_time: float, is_error: bool = False):
        """记录请求"""
        with self._lock:
            self._request_count += 1
            self._total_response_time += response_time
            self._response_times.append(response_time)
            
            # 保留最近1000条响应时间
            if len(self._response_times) > 1000:
                self._response_times = self._response_times[-1000:]
            
            # 端点统计
            self._endpoint_stats[endpoint]["count"] += 1
            self._endpoint_stats[endpoint]["total_time"] += response_time
            if is_error:
                self._error_count += 1
                self._endpoint_stats[endpoint]["errors"] += 1
    
    def record_cache(self, is_hit: bool):
        """记录缓存命中/未命中"""
        with self._lock:
            if is_hit:
                self._cache_hits += 1
            else:
                self._cache_misses += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        with self._lock:
            # 计算平均响应时间
            avg_response_time = (
                self._total_response_time / self._request_count 
                if self._request_count > 0 else 0
            )
            
            # 计算缓存命中率
            cache_total = self._cache_hits + self._cache_misses
            cache_hit_rate = (
                self._cache_hits / cache_total 
                if cache_total > 0 else 0
            )
            
            # 计算错误率
            error_rate = (
                self._error_count / self._request_count 
                if self._request_count > 0 else 0
            )
            
            # 计算P95响应时间
            sorted_times = sorted(self._response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_response_time = sorted_times[p95_index] if sorted_times else 0
            
            # 运行时间
            uptime = (datetime.now() - self._start_time).total_seconds()
            
            return {
                "requests": {
                    "total": self._request_count,
                    "errors": self._error_count,
                    "error_rate": round(error_rate * 100, 2),
                },
                "response_time": {
                    "avg_ms": round(avg_response_time * 1000, 2),
                    "p95_ms": round(p95_response_time * 1000, 2),
                },
                "cache": {
                    "hits": self._cache_hits,
                    "misses": self._cache_misses,
                    "hit_rate": round(cache_hit_rate * 100, 2),
                },
                "uptime_seconds": int(uptime),
                "endpoints": [
                    {
                        "path": path,
                        "count": stats["count"],
                        "errors": stats["errors"],
                        "avg_ms": round((stats["total_time"] / stats["count"] * 1000), 2) if stats["count"] > 0 else 0
                    }
                    for path, stats in self._endpoint_stats.items()
                ]
            }
    
    def reset(self):
        """重置指标"""
        with self._lock:
            self._init()


# 全局指标实例
metrics = Metrics()
