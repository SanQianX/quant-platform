# 统一响应模型
from pydantic import BaseModel
from typing import Any, Optional, List

class ResponseModel(BaseModel):
    """统一响应模型"""
    code: int = 0
    message: str = "success"
    data: Any = None

class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int = -1
    message: str = "服务器错误"
    data: Optional[Any] = None

def success_response(data: Any = None, message: str = "success") -> dict:
    """成功响应"""
    return {
        "code": 0,
        "message": message,
        "data": data
    }

def error_response(message: str, code: int = -1) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": None
    }
