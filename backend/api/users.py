# 用户管理 API
"""
完整的用户CRUD功能
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from services.auth_service import AuthService
import uuid
from api.auth import get_current_user_dep, get_admin_user

router = APIRouter(prefix="/api/users", tags=["用户管理"])

# 内存存储（生产环境应使用数据库）
users_db = {
    "admin": {
        "id": "1",
        "username": "admin",
        "email": "admin@quant.local",
        "role": "admin",
        "is_active": True,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00"
    },
    "user": {
        "id": "2",
        "username": "user",
        "email": "user@quant.local",
        "role": "user",
        "is_active": True,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00"
    }
}

# 请求模型
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str
    updated_at: str


@router.get("", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user_dep)
):
    """
    获取用户列表
    
    需要认证
    返回所有用户（不包含密码）
    """
    users = list(users_db.values())
    return users[skip:skip+limit]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, current_user: dict = Depends(get_current_user_dep)):
    """
    获取用户详情
    
    需要认证
    返回指定用户信息
    """
    user = next((u for u in users_db.values() if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_admin_user)
):
    """
    创建新用户
    
    需要管理员权限
    """
    # 检查用户名是否已存在
    if user_data.username in users_db:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已使用
    for u in users_db.values():
        if u["email"] == user_data.email:
            raise HTTPException(status_code=400, detail="邮箱已被使用")
    
    # 生成用户ID
    user_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    # 创建用户
    new_user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": AuthService.get_password_hash(user_data.password),
        "role": user_data.role,
        "is_active": True,
        "created_at": now,
        "updated_at": now
    }
    
    users_db[user_data.username] = new_user
    
    # 返回不包含密码的信息
    return {
        "id": new_user["id"],
        "username": new_user["username"],
        "email": new_user["email"],
        "role": new_user["role"],
        "is_active": new_user["is_active"],
        "created_at": new_user["created_at"],
        "updated_at": new_user["updated_at"]
    }


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: dict = Depends(get_admin_user)
):
    """
    更新用户信息
    
    需要管理员权限
    """
    # 找到用户
    user = None
    username = None
    for uname, u in users_db.items():
        if u["id"] == user_id:
            user = u
            username = uname
            break
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新字段
    now = datetime.now().isoformat()
    
    if user_data.email is not None:
        user["email"] = user_data.email
    if user_data.role is not None:
        user["role"] = user_data.role
    if user_data.is_active is not None:
        user["is_active"] = user_data.is_active
    if user_data.password is not None:
        user["password_hash"] = AuthService.get_password_hash(user_data.password)
    
    user["updated_at"] = now
    
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "is_active": user["is_active"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }


@router.delete("/{user_id}")
def delete_user(user_id: str, current_user: dict = Depends(get_admin_user)):
    """
    删除用户
    
    需要管理员权限
    """
    # 找到用户
    username = None
    for uname, u in users_db.items():
        if u["id"] == user_id:
            username = uname
            break
    
    if not username:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能删除自己
    if current_user["username"] == username:
        raise HTTPException(status_code=400, detail="不能删除当前登录用户")
    
    # 删除用户
    del users_db[username]
    
    return {"message": "用户删除成功", "user_id": user_id}


@router.get("/me/profile")
def get_my_profile(current_user: dict = Depends(get_current_user_dep)):
    """
    获取当前用户详细信息
    """
    username = current_user["username"]
    user = users_db.get(username)
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "is_active": user["is_active"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }


@router.put("/me/password")
def change_password(
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user_dep)
):
    """
    修改当前用户密码
    """
    username = current_user["username"]
    user = users_db.get(username)
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证旧密码
    if not AuthService.verify_password(old_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="原密码错误")
    
    # 更新密码
    user["password_hash"] = AuthService.get_password_hash(new_password)
    user["updated_at"] = datetime.now().isoformat()
    
    return {"message": "密码修改成功"}
