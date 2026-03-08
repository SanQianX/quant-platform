# 认证 API
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from services.auth_service import (
    authenticate_user, 
    AuthService, 
    get_current_user,
    MOCK_USERS
)

router = APIRouter(prefix="/api/auth", tags=["认证"])

# OAuth2 依赖
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 请求模型
class UserLogin(BaseModel):
    username: str
    password: str

class UserInfo(BaseModel):
    username: str
    role: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

# 依赖：获取当前用户
async def get_current_user_dep(token: str = Depends(oauth2_scheme)) -> dict:
    """获取当前登录用户"""
    user = get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# 依赖：获取管理员用户
async def get_admin_user(current_user: dict = Depends(get_current_user_dep)) -> dict:
    """确保用户是管理员"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录
    
    使用OAuth2表单格式，用户名和密码
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建令牌
    access_token = AuthService.create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserInfo)
def get_me(current_user: dict = Depends(get_current_user_dep)):
    """
    获取当前用户信息
    
    需要Bearer token认证
    """
    return current_user

@router.get("/users", response_model=list)
def list_users(current_user: dict = Depends(get_admin_user)):
    """
    获取用户列表（仅管理员）
    
    需要管理员权限
    """
    return [
        {"username": u["username"], "role": u["role"], "email": u["email"]}
        for u in MOCK_USERS.values()
    ]

@router.post("/register")
def register(username: str, password: str, email: str, role: str = "user"):
    """
    注册新用户（演示用，生产环境应限制）
    """
    if username in MOCK_USERS:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    
    MOCK_USERS[username] = {
        "username": username,
        "password": AuthService.get_password_hash(password),
        "role": role,
        "email": email
    }
    
    return {"message": "用户注册成功", "username": username}
