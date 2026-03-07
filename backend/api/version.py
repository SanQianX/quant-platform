# API版本控制
"""
API版本控制模块
支持多版本共存
"""

from fastapi import APIRouter

# 创建版本路由
v1_router = APIRouter(prefix="/v1")

# V1版本的路由组
@v1_router.get("/version")
def get_api_version():
    """获取API版本信息"""
    return {
        "version": "1.0.0",
        "name": "quant-platform-api",
        "status": "active"
    }
