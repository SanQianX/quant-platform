# 数据库配置
"""
数据库配置模块
支持SQLite(开发)和PostgreSQL(生产)
"""

import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 环境配置
ENV: str = os.getenv("ENV", "development")

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self.database_url: str = self._get_database_url()
        self._engine = None
        self._session_factory = None
    
    def _get_database_url(self) -> str:
        """获取数据库URL"""
        if ENV == "production":
            return os.getenv(
                "DATABASE_URL", 
                "postgresql://quant_user:quant_pass@localhost:5432/quant_platform"
            )
        else:
            # 开发环境使用SQLite
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "data", "quant.db")
            return f"sqlite:///{db_path}"
    
    @property
    def engine(self):
        """获取数据库引擎"""
        if self._engine is None:
            connect_args = {"check_same_thread": False} if "sqlite" in self.database_url else {}
            self._engine = create_engine(
                self.database_url, 
                connect_args=connect_args,
                pool_pre_ping=True
            )
        return self._engine
    
    @property
    def session_factory(self):
        """获取会话工厂"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=self.engine
            )
        return self._session_factory
    
    def get_session(self):
        """获取数据库会话"""
        return self.session_factory()
    
    def create_all(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)

# 创建全局数据库配置实例
db_config = DatabaseConfig()

# 导出兼容性
engine = db_config.engine
SessionLocal = db_config.session_factory

# 创建基类
Base = declarative_base()

def get_db():
    """获取数据库会话（兼容旧代码）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
