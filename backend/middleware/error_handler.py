# 错误处理中间件
"""
统一错误处理和异常捕获
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from utils.logger import logger

class ErrorHandler:
    """错误处理器"""
    
    @staticmethod
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """HTTP异常处理"""
        logger.warning(f"HTTP错误: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
                "data": None,
                "path": str(request.url)
            }
        )
    
    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求验证错误处理"""
        logger.warning(f"验证错误: {exc.errors()}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": 422,
                "message": "请求参数验证失败",
                "data": exc.errors(),
                "path": str(request.url)
            }
        )
    
    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理"""
        # 记录完整错误信息
        error_msg = str(exc)
        traceback_str = traceback.format_exc()
        
        logger.error(f"服务器错误: {error_msg}\n{traceback_str}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "data": None,
                "path": str(request.url)
            }
        )


def setup_error_handlers(app):
    """设置错误处理器"""
    from fastapi import FastAPI
    
    # HTTP异常
    app.add_exception_handler(StarletteHTTPException, ErrorHandler.http_exception_handler)
    
    # 验证错误
    app.add_exception_handler(RequestValidationError, ErrorHandler.validation_exception_handler)
    
    # 通用错误
    app.add_exception_handler(Exception, ErrorHandler.general_exception_handler)
