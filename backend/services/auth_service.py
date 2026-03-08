# 认证模块
"""
JWT认证和用户管理
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# JWT配置
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "quant-platform-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """认证服务"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """解码令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def verify_token(token: str) -> bool:
        """验证令牌是否有效"""
        payload = AuthService.decode_token(token)
        return payload is not None


# 模拟用户数据（生产环境应从数据库获取）
MOCK_USERS = {
    "admin": {
        "username": "admin",
        "password": AuthService.get_password_hash("admin123"),
        "role": "admin",
        "email": "admin@quant.local"
    },
    "user": {
        "username": "user",
        "password": AuthService.get_password_hash("user123"),
        "role": "user",
        "email": "user@quant.local"
    }
}

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """认证用户"""
    user = MOCK_USERS.get(username)
    if not user:
        return None
    if not AuthService.verify_password(password, user["password"]):
        return None
    
    # 返回用户信息（不包含密码）
    return {
        "username": user["username"],
        "role": user["role"],
        "email": user["email"]
    }

def get_current_user(token: str) -> Optional[dict]:
    """获取当前用户"""
    payload = AuthService.decode_token(token)
    if not payload:
        return None
    
    username = payload.get("sub")
    if not username:
        return None
    
    user = MOCK_USERS.get(username)
    if not user:
        return None
    
    return {
        "username": user["username"],
        "role": user["role"],
        "email": user["email"]
    }
