# 数据验证器
"""
数据验证模块
提供各种业务数据验证函数
"""

import re
from typing import Optional
from datetime import datetime, timedelta

class StockValidator:
    """股票数据验证器"""
    
    # 股票代码正则
    STOCK_CODE_PATTERN = re.compile(r"^\d{6}(_sh)?$")
    
    # 指数代码
    INDEX_CODES = {"000001_sh", "399001", "399006"}
    
    @classmethod
    def validate_code(cls, code: str) -> tuple[bool, str]:
        """验证股票代码"""
        if not code:
            return False, "股票代码不能为空"
        
        if not cls.STOCK_CODE_PATTERN.match(code):
            return False, "股票代码格式错误"
        
        return True, ""
    
    @classmethod
    def is_index(cls, code: str) -> bool:
        """判断是否为指数"""
        return code in cls.INDEX_CODES
    
    @classmethod
    def normalize_code(cls, code: str) -> str:
        """标准化股票代码"""
        return code.strip().upper()

class DateValidator:
    """日期验证器"""
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> tuple[bool, str]:
        """验证日期范围"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start > end:
                return False, "开始日期不能晚于结束日期"
            
            if (end - start).days > 365:
                return False, "日期范围不能超过365天"
            
            return True, ""
        except ValueError:
            return False, "日期格式错误，应为YYYY-MM-DD"
    
    @staticmethod
    def get_default_date_range() -> tuple[str, str]:
        """获取默认日期范围"""
        end = datetime.now()
        start = end - timedelta(days=90)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

class ExportValidator:
    """导出验证器"""
    
    SUPPORTED_FORMATS = {"csv", "json", "xlsx"}
    
    @classmethod
    def validate_format(cls, format: str) -> tuple[bool, str]:
        """验证导出格式"""
        if not format:
            return False, "导出格式不能为空"
        
        if format.lower() not in cls.SUPPORTED_FORMATS:
            return False, f"不支持的格式，支持: {', '.join(cls.SUPPORTED_FORMATS)}"
        
        return True, ""
