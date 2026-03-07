# 日志配置
"""
日志配置模块
"""

import logging
import sys
from datetime import datetime

# 日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logger(name: str = "quant_platform", level: int = logging.INFO):
    """
    设置日志器
    
    Args:
        name: 日志器名称
        level: 日志级别
        
    Returns:
        Logger: 配置好的日志器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if not logger.handlers:
        # 控制台handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(
            logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        )
        logger.addHandler(console_handler)
    
    return logger

# 创建默认日志器
logger = setup_logger()
