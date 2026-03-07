# 数据库配置
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 从环境变量读取数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://quant_user:quant_pass@localhost:5432/quant_platform"
)

# 创建引擎
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
