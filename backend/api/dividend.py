# 分红送股API路由
from fastapi import APIRouter, Path
from typing import Optional

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票-分红送股"])

# 模拟分红数据
MOCK_DIVIDEND_DATA = {
    "000001": [  # 平安银行
        {"year": 2024, "date": "2024-06-30", "cash_dividend": 0.72, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2023, "date": "2023-06-30", "cash_dividend": 0.65, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2023, "date": "2023-12-31", "cash_dividend": 0.15, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2022, "date": "2022-06-30", "cash_dividend": 0.62, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2022, "date": "2022-12-31", "cash_dividend": 0.12, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
    ],
    "000002": [  # 万科A
        {"year": 2024, "date": "2024-07-15", "cash_dividend": 0.68, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2023, "date": "2023-07-15", "cash_dividend": 0.73, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2022, "date": "2022-07-15", "cash_dividend": 0.97, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
    ],
    "600519": [  # 贵州茅台
        {"year": 2024, "date": "2024-06-20", "cash_dividend": 30.76, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2023, "date": "2023-06-20", "cash_dividend": 25.54, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2023, "date": "2023-12-31", "cash_dividend": 10.73, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2022, "date": "2022-06-20", "cash_dividend": 19.29, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2022, "date": "2022-12-31", "cash_dividend": 8.03, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
    ],
    "600036": [  # 招商银行
        {"year": 2024, "date": "2024-07-10", "cash_dividend": 1.74, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2023, "date": "2023-07-10", "cash_dividend": 1.54, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
        {"year": 2023, "date": "2023-12-31", "cash_dividend": 0.46, "stock_dividend": 0.0, "bonus_shares": 0.0, "dividend_type": "派息"},
    ],
}

# 模拟送转股数据
MOCK_SPLIT_DATA = {
    "000001": [  # 平安银行
        {"year": 2024, "date": "2024-06-30", "bonus_shares": 0.0, "stock_dividend": 0.0, "transfer": 0.0, "split_type": "送转"},
        {"year": 2023, "date": "2023-06-30", "bonus_shares": 0.0, "stock_dividend": 0.0, "transfer": 0.0, "split_type": "送转"},
        {"year": 2022, "date": "2022-06-30", "bonus_shares": 0.0, "stock_dividend": 0.0, "transfer": 0.0, "split_type": "送转"},
    ],
    "000002": [  # 万科A
        {"year": 2022, "date": "2022-07-15", "bonus_shares": 0.0, "stock_dividend": 0.0, "transfer": 0.0, "split_type": "送转"},
    ],
    "600519": [  # 贵州茅台 - 无送转
        {"year": 2024, "date": "2024-06-20", "bonus_shares": 0.0, "stock_dividend": 0.0, "transfer": 0.0, "split_type": "送转"},
    ],
    "300750": [  # 宁德时代
        {"year": 2024, "date": "2024-05-20", "bonus_shares": 0.0, "stock_dividend": 0.0, "transfer": 1.0, "split_type": "转增"},
        {"year": 2023, "date": "2023-05-20", "bonus_shares": 0.0, "stock_dividend": 0.0, "transfer": 0.5, "split_type": "转增"},
        {"year": 2022, "date": "2022-05-20", "bonus_shares": 0.0, "stock_dividend": 0.0, "trasnfer": 0.2, "split_type": "转增"},
    ],
    "000001": [
        {"year": 2024, "date": "2024-06-30", "bonus_shares": 0.0, "stock_dividend": 0.0, "transfer": 0.0, "split_type": "送转"},
    ],
}


@router.get("/{code}/dividend")
def get_dividend(
    code: str = Path(..., description="股票代码", example="000001")
):
    """
    获取股票分红送股列表
    
    返回股票的历史分红送股数据
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含分红送股数据列表
    """
    # 标准化股票代码
    normalized_code = code.upper()
    
    # 获取数据，如果不存在返回空列表
    data = MOCK_DIVIDEND_DATA.get(normalized_code, [])
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": normalized_code,
            "list": data,
            "total": len(data)
        }
    }


@router.get("/{code}/split")
def get_split(
    code: str = Path(..., description="股票代码", example="000001")
):
    """
    获取股票送转股记录
    
    返回股票的历史送转股数据
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含送转股数据列表
    """
    # 标准化股票代码
    normalized_code = code.upper()
    
    # 获取数据，如果不存在返回空列表
    data = MOCK_SPLIT_DATA.get(normalized_code, [])
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": normalized_code,
            "list": data,
            "total": len(data)
        }
    }
