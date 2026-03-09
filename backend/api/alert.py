# 价格预警API路由
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

# 创建路由
router = APIRouter(prefix="/api/alert", tags=["预警"])

# 内存存储预警数据
alerts_storage = []

# 预警模型
class PriceAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="预警ID")
    code: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")
    alert_type: str = Field("price", description="预警类型")
    condition: str = Field(..., description="触发条件: above/below")
    target_price: float = Field(..., description="目标价格")
    current_price: Optional[float] = Field(None, description="当前价格")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="创建时间")
    enabled: bool = Field(default=True, description="是否启用")

class AlertCreate(BaseModel):
    code: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")
    condition: str = Field(..., description="触发条件: above/below")
    target_price: float = Field(..., description="目标价格")

@router.post("/price", status_code=200)
def create_price_alert(alert: AlertCreate = Body(...)):
    """
    设置价格监控预警
    
    当股票价格达到目标价格时触发预警
    
    Args:
        alert: 预警配置
        
    Returns:
        dict: 统一响应格式，包含创建的预警信息
    """
    # 验证条件
    if alert.condition not in ["above", "below"]:
        raise HTTPException(status_code=400, detail="条件只能是 above(高于) 或 below(低于)")
    
    # 验证价格
    if alert.target_price <= 0:
        raise HTTPException(status_code=400, detail="目标价格必须大于0")
    
    # 创建预警
    new_alert = PriceAlert(
        code=alert.code,
        name=alert.name,
        alert_type="price",
        condition=alert.condition,
        target_price=alert.target_price,
        current_price=None,
        enabled=True
    )
    
    # 存储预警
    alerts_storage.append(new_alert)
    
    return {
        "code": 0,
        "message": "预警创建成功",
        "data": new_alert.model_dump()
    }

@router.get("", status_code=200)
def get_alert_list():
    """
    获取用户预警列表
    
    返回所有已设置的预警列表
    
    Returns:
        dict: 统一响应格式，包含预警列表
    """
    return {
        "code": 0,
        "message": "获取成功",
        "data": [alert.model_dump() for alert in alerts_storage]
    }

@router.delete("/{alert_id}", status_code=200)
def delete_alert(alert_id: str):
    """
    删除预警
    
    根据预警ID删除指定的预警
    
    Args:
        alert_id: 预警ID
        
    Returns:
        dict: 统一响应格式
    """
    global alerts_storage
    
    # 查找预警
    for i, alert in enumerate(alerts_storage):
        if alert.id == alert_id:
            # 删除预警
            alerts_storage.pop(i)
            return {
                "code": 0,
                "message": "预警删除成功",
                "data": None
            }
    
    # 未找到预警
    raise HTTPException(status_code=404, detail="预警不存在")
