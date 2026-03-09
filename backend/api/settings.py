# 用户偏好设置 API
"""
用户偏好设置功能
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from api.auth import get_current_user_dep

router = APIRouter(prefix="/api/settings", tags=["用户设置"])

# 内存存储 - 用户偏好设置（生产环境应使用数据库）
user_settings_db = {}

# 默认设置
DEFAULT_SETTINGS = {
    "theme": "light",
    "language": "zh-CN",
    "timezone": "Asia/Shanghai",
    "currency": "CNY",
    "notification_enabled": True,
    "email_notification": False,
    "display_mode": "grid",
    "page_size": 20,
    "chart_type": "candlestick",
    "default_indicator": "ma",
    "auto_refresh": True,
    "refresh_interval": 60
}

# 请求/响应模型
class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    notification_enabled: Optional[bool] = None
    email_notification: Optional[bool] = None
    display_mode: Optional[str] = None
    page_size: Optional[int] = None
    chart_type: Optional[str] = None
    default_indicator: Optional[str] = None
    auto_refresh: Optional[bool] = None
    refresh_interval: Optional[int] = None

class ThemeUpdate(BaseModel):
    theme: str

class SettingsResponse(BaseModel):
    theme: str
    language: str
    timezone: str
    currency: str
    notification_enabled: bool
    email_notification: bool
    display_mode: str
    page_size: int
    chart_type: str
    default_indicator: str
    auto_refresh: bool
    refresh_interval: int
    updated_at: str


def get_user_settings(username: str) -> dict:
    """获取用户设置，如果不存在则返回默认设置"""
    if username not in user_settings_db:
        user_settings_db[username] = DEFAULT_SETTINGS.copy()
        user_settings_db[username]["updated_at"] = datetime.now().isoformat()
    return user_settings_db[username]


@router.get("", response_model=SettingsResponse)
def get_settings(current_user: dict = Depends(get_current_user_dep)):
    """
    获取用户偏好设置
    
    需要认证
    返回当前用户的偏好设置
    """
    username = current_user["username"]
    settings = get_user_settings(username)
    return settings


@router.put("", response_model=SettingsResponse)
def update_settings(
    settings_data: SettingsUpdate,
    current_user: dict = Depends(get_current_user_dep)
):
    """
    更新用户偏好设置
    
    需要认证
    可以部分更新，只传入需要修改的字段
    """
    username = current_user["username"]
    settings = get_user_settings(username)
    
    # 更新非空字段
    update_data = settings_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            settings[key] = value
    
    # 更新时间戳
    settings["updated_at"] = datetime.now().isoformat()
    
    return settings


@router.put("/theme", response_model=SettingsResponse)
def set_theme(
    theme_data: ThemeUpdate,
    current_user: dict = Depends(get_current_user_dep)
):
    """
    设置界面主题
    
    需要认证
    可选主题: light, dark, auto
    """
    valid_themes = ["light", "dark", "auto"]
    
    if theme_data.theme not in valid_themes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的主题，必须是以下之一: {', '.join(valid_themes)}"
        )
    
    username = current_user["username"]
    settings = get_user_settings(username)
    
    # 更新主题
    settings["theme"] = theme_data.theme
    settings["updated_at"] = datetime.now().isoformat()
    
    return settings
