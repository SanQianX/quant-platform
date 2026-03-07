# 请求日志中间件
"""
请求日志中间件
记录所有API请求
"""

import time
from fastapi import Request
from utils.logger import logger
import uuid

async def log_requests(request: Request, call_next):
    """
    请求日志中间件
    
    记录请求方法、路径、耗时等信息
    """
    # 生成请求ID
    request_id = str(uuid.uuid4())[:8]
    
    # 记录请求开始
    start_time = time.time()
    
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    # 处理请求
    try:
        response = await call_next(request)
        
        # 计算耗时
        duration = time.time() - start_time
        
        # 记录响应
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"- {response.status_code} - {duration:.3f}s"
        )
        
        # 添加请求ID到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} "
            f"- ERROR - {duration:.3f}s - {str(e)}"
        )
        raise
