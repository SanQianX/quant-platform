# 配股API路由
from fastapi import APIRouter, Path
from typing import Optional

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票-配股"])

# 模拟配股数据
MOCK_RIGHTS_ISSUE_DATA = {
    "000001": [  # 平安银行
        {
            "year": 2023,
            "date": "2023-11-15",
            "rights_issue_price": 11.35,
            "rights_issue_ratio": 0.3,
            "shares_per_10": 3,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
        {
            "year": 2020,
            "date": "2020-10-20",
            "rights_issue_price": 12.87,
            "rights_issue_ratio": 0.25,
            "shares_per_10": 2.5,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
    ],
    "600519": [  # 贵州茅台
        {
            "year": 2024,
            "date": "2024-11-28",
            "rights_issue_price": 1269.99,
            "rights_issue_ratio": 0.15,
            "shares_per_10": 1.5,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
    ],
    "600036": [  # 招商银行
        {
            "year": 2023,
            "date": "2023-07-12",
            "rights_issue_price": 9.41,
            "rights_issue_ratio": 0.28,
            "shares_per_10": 2.8,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
        {
            "year": 2020,
            "date": "2020-07-10",
            "rights_issue_price": 7.35,
            "rights_issue_ratio": 0.22,
            "shares_per_10": 2.2,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
    ],
    "000002": [  # 万科A
        {
            "year": 2021,
            "date": "2021-07-15",
            "rights_issue_price": 6.92,
            "rights_issue_ratio": 0.2,
            "shares_per_10": 2.0,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
    ],
    "601318": [  # 中国平安
        {
            "year": 2022,
            "date": "2022-05-20",
            "rights_issue_price": 38.96,
            "rights_issue_ratio": 0.18,
            "shares_per_10": 1.8,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
        {
            "year": 2019,
            "date": "2019-05-23",
            "rights_issue_price": 31.22,
            "rights_issue_ratio": 0.15,
            "shares_per_10": 1.5,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
    ],
    "601398": [  # 工商银行
        {
            "year": 2023,
            "date": "2023-12-20",
            "rights_issue_price": 4.68,
            "rights_issue_ratio": 0.12,
            "shares_per_10": 1.2,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
    ],
    "601166": [  # 兴业银行
        {
            "year": 2022,
            "date": "2022-06-28",
            "rights_issue_price": 17.77,
            "rights_issue_ratio": 0.25,
            "shares_per_10": 2.5,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
    ],
    "300750": [  # 宁德时代
        {
            "year": 2024,
            "date": "2024-07-18",
            "rights_issue_price": 118.63,
            "rights_issue_ratio": 0.2,
            "shares_per_10": 2.0,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
    ],
    "002594": [  # 比亚迪
        {
            "year": 2023,
            "date": "2023-11-22",
            "rights_issue_price": 268.36,
            "rights_issue_ratio": 0.17,
            "shares_per_10": 1.7,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
    ],
    "000858": [  # 五粮液
        {
            "year": 2021,
            "date": "2021-07-05",
            "rights_issue_price": 25.57,
            "rights_issue_ratio": 0.22,
            "shares_per_10": 2.2,
            "bonus_shares": 0.0,
            "cash_dividend": 0.0,
            "rights_issue_type": "配股"
        },
    ],
}


@router.get("/{code}/rights-issue")
def get_rights_issue(
    code: str = Path(..., description="股票代码", example="000001")
):
    """
    获取股票配股列表
    
    返回股票的历史配股数据
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含配股数据列表
    """
    # 标准化股票代码
    normalized_code = code.upper()
    
    # 获取数据，如果不存在返回空列表
    data = MOCK_RIGHTS_ISSUE_DATA.get(normalized_code, [])
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": normalized_code,
            "list": data,
            "total": len(data)
        }
    }
