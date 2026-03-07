# 系统健康检查
"""
系统健康检查接口
"""

from fastapi import APIRouter
from datetime import datetime
import psutil
import os

router = APIRouter(prefix="/api", tags=["系统"])

@router.get("/health/detailed")
def detailed_health_check():
    """
    详细健康检查
    
    返回系统资源使用情况
    """
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # 内存使用
        memory = psutil.virtual_memory()
        
        # 磁盘使用
        disk = psutil.disk_usage('/')
        
        # 进程信息
        process = psutil.Process(os.getpid())
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": round(memory.used / 1024 / 1024, 2),
                "disk_percent": disk.percent
            },
            "process": {
                "threads": process.num_threads(),
                "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2)
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/health/ready")
def readiness_check():
    """
    就绪检查
    
    用于Kubernetes就绪探针
    """
    return {"ready": True}

@router.get("/health/live")
def liveness_check():
    """
    存活检查
    
    用于Kubernetes存活探针
    """
    return {"alive": True}
