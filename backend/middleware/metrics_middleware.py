# 请求监控中间件
"""
记录请求和响应时间的中间件
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from utils.metrics import metrics
from utils.logger import logger
import time

class MetricsMiddleware(BaseHTTPMiddleware):
    """请求监控中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 跳过健康检查和指标的监控
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            response_time = time.time() - start_time
            
            # 记录指标
            metrics.record_request(
                endpoint=request.url.path,
                response_time=response_time,
                is_error=response.status_code >= 400
            )
            
            logger.info(
                f"{request.method} {request.url.path} - "
                f"status:{response.status_code} time:{response_time*1000:.1f}ms"
            )
            
            return response
        except Exception as e:
            response_time = time.time() - start_time
            metrics.record_request(
                endpoint=request.url.path,
                response_time=response_time,
                is_error=True
            )
            logger.error(f"请求错误: {request.url.path} - {str(e)}")
            raise
