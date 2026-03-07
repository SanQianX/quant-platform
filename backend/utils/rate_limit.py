# 请求限流中间件
"""
请求限流模块
防止API被恶意请求或过度使用
"""

from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from typing import Dict
import threading

class RateLimiter:
    """简单请求限流器"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        初始化限流器
        
        Args:
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口大小(秒)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = {}
        self._lock = threading.Lock()
    
    def check(self, client_id: str) -> bool:
        """
        检查请求是否允许
        
        Args:
            client_id: 客户端标识
            
        Returns:
            True表示允许，False表示超过限制
        """
        with self._lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            # 初始化客户端记录
            if client_id not in self._requests:
                self._requests[client_id] = []
            
            # 清理过期请求记录
            self._requests[client_id] = [
                t for t in self._requests[client_id]
                if t > window_start
            ]
            
            # 检查是否超过限制
            if len(self._requests[client_id]) >= self.max_requests:
                return False
            
            # 记录本次请求
            self._requests[client_id].append(now)
            return True

# 创建全局限流器实例
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
