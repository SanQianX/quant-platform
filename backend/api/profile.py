# 股票基本面概况API
from fastapi import APIRouter, HTTPException
from typing import Optional

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票基本面"])

# 模拟基本面数据
MOCK_PROFILE_DATA = {
    "000001": {
        "code": "000001",
        "name": "平安银行",
        "industry": "银行",
        "market": "深圳主板",
        "list_date": "1991-04-03",
        "exchange": "SZSE",
        "currency": "CNY",
        "status": "上市",
        "area": "广东",
        "province": "广东省",
        "city": "深圳市",
        "address": "深圳市深南东路5047号",
        "website": "http://www.bank.pingan.com",
        "introduction": "平安银行是中国平安保险集团旗下的商业银行",
        "chairman": "谢永林",
        "manager": "王伟",
        "reg_capital": 1940591,  # 万元
        "setup_date": "1987-12-22",
        "employees": 34861,
        "main_business": "吸收公众存款；发放短期和中长期贷款；办理国内外结算等",
        "business_scope": "吸收公众存款；发放短期和中长期贷款；办理国内外结算；办理票据承兑与贴现；发行金融债券；代理发行、代理兑付、承销政府债券；买卖政府债券、金融债券；从事同业拆借；买卖、代理买卖外汇；从事银行卡业务；提供信用证服务及担保；代理收付款项及代理保险业务；提供保管箱服务；经中国银行业监督管理委员会批准的其他业务。"
    },
    "600519": {
        "code": "600519",
        "name": "贵州茅台",
        "industry": "白酒",
        "market": "上海主板",
        "list_date": "2001-08-27",
        "exchange": "SSE",
        "currency": "CNY",
        "status": "上市",
        "area": "贵州",
        "province": "贵州省",
        "city": "仁怀市",
        "address": "贵州省仁怀市茅台镇",
        "website": "http://www.moutai.com.cn",
        "introduction": "贵州茅台是中国著名的白酒生产企业",
        "chairman": "丁雄军",
        "manager": "李静仁",
        "reg_capital": 250619,  # 万元
        "setup_date": "1999-11-20",
        "employees": 31513,
        "main_business": "茅台酒系列产品的生产与销售",
        "business_scope": "茅台酒系列产品的生产与销售；饮料、药品、服装、包装物的生产和销售"
    },
    "000002": {
        "code": "000002",
        "name": "万 科A",
        "industry": "房地产",
        "market": "深圳主板",
        "list_date": "1991-01-29",
        "exchange": "SZSE",
        "currency": "CNY",
        "status": "上市",
        "area": "广东",
        "province": "广东省",
        "city": "深圳市",
        "address": "深圳市盐田区大梅沙环梅路33号万科中心",
        "website": "http://www.vanke.com",
        "introduction": "万科企业股份有限公司是中国最大的房地产开发企业之一",
        "chairman": "祝九胜",
        "manager": "张海",
        "reg_capital": 1099521,  # 万元
        "setup_date": "1984-05-21",
        "employees": 138817,
        "main_business": "房地产开发、物业服务、租赁住房",
        "business_scope": "房地产开发、物业服务、租赁住房、产业城镇、冰雪度假、物流仓储"
    }
}

def get_mock_profile(code: str) -> dict:
    """
    获取模拟基本面概况数据
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 基本面概况数据
    """
    # 如果有模拟数据则返回
    if code in MOCK_PROFILE_DATA:
        return {
            "code": 0,
            "message": "success",
            "data": MOCK_PROFILE_DATA[code]
        }
    
    # 返回默认模拟数据
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": code,
            "name": f"股票{code}",
            "industry": "未知",
            "market": "深圳主板",
            "list_date": "2020-01-01",
            "exchange": "SZSE",
            "currency": "CNY",
            "status": "上市",
            "area": "未知",
            "province": "未知",
            "city": "未知",
            "address": "",
            "website": "",
            "introduction": "这是股票的基本面介绍（模拟数据）",
            "chairman": "",
            "manager": "",
            "reg_capital": 0,
            "setup_date": "",
            "employees": 0,
            "main_business": "",
            "business_scope": ""
        }
    }


@router.get("/{code}/profile")
def get_stock_profile(code: str):
    """
    获取股票基本面概况
    
    获取指定股票的基本面概况信息，包括公司基本信息、注册资本、主营业务等
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含基本面概况数据
    """
    return get_mock_profile(code)
