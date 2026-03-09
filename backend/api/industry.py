# 股票所属板块API路由
"""
股票所属板块数据接口

提供股票所属板块查询功能
使用模拟数据
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import random

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票所属板块"])


# 股票所属板块模拟数据
# 包含股票代码、名称、所属板块、板块代码等信息
STOCK_INDUSTRY_DATA = {
    "600000": {"name": "浦发银行", "industry": "银行", "industry_code": "801050", "sector": "金融", "sub_industry": "股份制银行"},
    "600036": {"name": "招商银行", "industry": "银行", "industry_code": "801050", "sector": "金融", "sub_industry": "股份制银行"},
    "600519": {"name": "贵州茅台", "industry": "白酒", "industry_code": "801050", "sector": "食品饮料", "sub_industry": "白酒"},
    "000858": {"name": "五粮液", "industry": "白酒", "industry_code": "801050", "sector": "食品饮料", "sub_industry": "白酒"},
    "600887": {"name": "伊利股份", "industry": "乳制品", "industry_code": "801050", "sector": "食品饮料", "sub_industry": "乳制品"},
    "000333": {"name": "美的集团", "industry": "家电", "industry_code": "801050", "sector": "家用电器", "sub_industry": "白色家电"},
    "000651": {"name": "格力电器", "industry": "家电", "industry_code": "801050", "sector": "家用电器", "sub_industry": "白色家电"},
    "600276": {"name": "恒瑞医药", "industry": "化学制药", "industry_code": "801050", "sector": "医药生物", "sub_industry": "化学制药"},
    "000566": {"name": "海南海药", "industry": "化学制药", "industry_code": "801050", "sector": "医药生物", "sub_industry": "化学制药"},
    "600030": {"name": "中信证券", "industry": "证券", "industry_code": "801050", "sector": "金融", "sub_industry": "券商"},
    "601688": {"name": "中国平安", "industry": "保险", "industry_code": "801050", "sector": "金融", "sub_industry": "保险"},
    "601318": {"name": "中国平安", "industry": "保险", "industry_code": "801050", "sector": "金融", "sub_industry": "保险"},
    "600900": {"name": "长江电力", "industry": "电力", "industry_code": "801050", "sector": "公用事业", "sub_industry": "水电"},
    "600028": {"name": "中国石化", "industry": "石油化工", "industry_code": "801050", "sector": "化工", "sub_industry": "石油化工"},
    "601857": {"name": "中国石油", "industry": "石油开采", "industry_code": "801050", "sector": "采掘", "sub_industry": "石油开采"},
    "600050": {"name": "中国联通", "industry": "通信运营", "industry_code": "801050", "sector": "通信", "sub_industry": "通信运营"},
    "600030": {"name": "中信证券", "industry": "证券", "industry_code": "801050", "sector": "金融", "sub_industry": "券商"},
    "601988": {"name": "中国银行", "industry": "银行", "industry_code": "801050", "sector": "金融", "sub_industry": "国有银行"},
    "601398": {"name": "工商银行", "industry": "银行", "industry_code": "801050", "sector": "金融", "sub_industry": "国有银行"},
    "601939": {"name": "建设银行", "industry": "银行", "industry_code": "801050", "sector": "金融", "sub_industry": "国有银行"},
    "601288": {"name": "农业银行", "industry": "银行", "industry_code": "801050", "sector": "金融", "sub_industry": "国有银行"},
    "600016": {"name": "民生银行", "industry": "银行", "industry_code": "801050", "sector": "金融", "sub_industry": "股份制银行"},
    "600015": {"name": "华夏银行", "industry": "银行", "industry_code": "801050", "sector": "金融", "sub_industry": "股份制银行"},
    "601229": {"name": "上海银行", "industry": "银行", "industry_code": "801050", "sector": "金融", "sub_industry": "城商行"},
    "002594": {"name": "比亚迪", "industry": "汽车整车", "industry_code": "801050", "sector": "汽车", "sub_industry": "新能源汽车"},
    "000002": {"name": "万科A", "industry": "房地产开发", "industry_code": "801050", "sector": "房地产", "sub_industry": "房地产开发"},
    "600048": {"name": "保利发展", "industry": "房地产开发", "industry_code": "801050", "sector": "房地产", "sub_industry": "房地产开发"},
    "600309": {"name": "万华化学", "industry": "化学制品", "industry_code": "801050", "sector": "化工", "sub_industry": "化学制品"},
    "601888": {"name": "中国中免", "industry": "旅游零售", "industry_code": "801050", "sector": "商贸零售", "sub_industry": "免税店"},
    "600009": {"name": "上海机场", "industry": "机场", "industry_code": "801050", "sector": "交通运输", "sub_industry": "机场"},
    "601012": {"name": "隆基绿能", "industry": "光伏", "industry_code": "801050", "sector": "电气设备", "sub_industry": "光伏设备"},
    "600438": {"name": "通威股份", "industry": "光伏", "industry_code": "801050", "sector": "电气设备", "sub_industry": "光伏设备"},
    "002475": {"name": "立讯精密", "industry": "电子制造", "industry_code": "801050", "sector": "电子", "sub_industry": "电子制造"},
    "000725": {"name": "京东方A", "industry": "光学光电子", "industry_code": "801050", "sector": "电子", "sub_industry": "面板"},
    "600703": {"name": "三安光电", "industry": "光学光电子", "industry_code": "801050", "sector": "电子", "sub_industry": "LED"},
    "002230": {"name": "科大讯飞", "industry": "软件开发", "industry_code": "801050", "sector": "计算机", "sub_industry": "人工智能"},
    "300750": {"name": "宁德时代", "industry": "电池", "industry_code": "801050", "sector": "电气设备", "sub_industry": "动力电池"},
    "002466": {"name": "天齐锂业", "industry": "锂矿", "industry_code": "801050", "sector": "有色金属", "sub_industry": "锂矿"},
    "600111": {"name": "北方稀土", "industry": "稀土", "industry_code": "801050", "sector": "有色金属", "sub_industry": "稀土"},
    "600547": {"name": "山东黄金", "industry": "黄金", "industry_code": "801050", "sector": "有色金属", "sub_industry": "黄金"},
    "601899": {"name": "紫金矿业", "industry": "铜矿", "industry_code": "801050", "sector": "有色金属", "sub_industry": "铜矿"},
    "000001": {"name": "平安银行", "industry": "银行", "industry_code": "801050", "sector": "金融", "sub_industry": "股份制银行"},
    "002415": {"name": "海康威视", "industry": "安防", "industry_code": "801050", "sector": "电子", "sub_industry": "安防设备"},
    "002027": {"name": "分众传媒", "industry": "广告营销", "industry_code": "801050", "sector": "传媒", "sub_industry": "广告营销"},
    "300059": {"name": "东方财富", "industry": "证券", "industry_code": "801050", "sector": "金融", "sub_industry": "互联网金融"},
    "688981": {"name": "中芯国际", "industry": "半导体", "industry_code": "801050", "sector": "电子", "sub_industry": "芯片制造"},
    "603259": {"name": "药明康德", "industry": "医疗服务", "industry_code": "801050", "sector": "医药生物", "sub_industry": "CRO"},
    "600690": {"name": "青岛海尔", "industry": "家电", "industry_code": "801050", "sector": "家用电器", "sub_industry": "白色家电"},
    "000063": {"name": "中兴通讯", "industry": "通信设备", "industry_code": "801050", "sector": "通信", "sub_industry": "通信设备"},
    "600570": {"name": "恒生电子", "industry": "软件开发", "industry_code": "801050", "sector": "计算机", "sub_industry": "金融科技"},
    "600031": {"name": "三一重工", "industry": "工程机械", "industry_code": "801050", "sector": "机械设备", "sub_industry": "工程机械"},
    "600585": {"name": "海螺水泥", "industry": "水泥制造", "industry_code": "801050", "sector": "建筑材料", "sub_industry": "水泥制造"},
    "000338": {"name": "潍柴动力", "industry": "汽车零部件", "industry_code": "801050", "sector": "汽车", "sub_industry": "汽车零部件"},
    "601888": {"name": "中国中铁", "industry": "铁路建设", "industry_code": "801050", "sector": "建筑装饰", "sub_industry": "铁路建设"},
    "601390": {"name": "中国中铁", "industry": "铁路建设", "industry_code": "801050", "sector": "建筑装饰", "sub_industry": "铁路建设"},
    "600170": {"name": "上海建工", "industry": "房屋建设", "industry_code": "801050", "sector": "建筑装饰", "sub_industry": "房屋建设"},
    "601668": {"name": "中国建筑", "industry": "房屋建设", "industry_code": "801050", "sector": "建筑装饰", "sub_industry": "房屋建设"},
    "600588": {"name": "用友网络", "industry": "软件开发", "industry_code": "801050", "sector": "计算机", "sub_industry": "SaaS"},
    "600570": {"name": "恒生电子", "industry": "软件开发", "industry_code": "801050", "sector": "计算机", "sub_industry": "金融软件"},
}


def get_mock_industry(code: str) -> dict:
    """
    生成模拟股票所属板块数据
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 模拟板块数据
    """
    # 检查是否在预设数据中
    if code in STOCK_INDUSTRY_DATA:
        return STOCK_INDUSTRY_DATA[code].copy()
    
    # 对于未预设的股票，生成基于代码的稳定随机数据
    seed = int(code) if code.isdigit() else sum(ord(c) for c in code)
    random.seed(seed)
    
    # 随机选择一个行业
    industries = [
        {"industry": "银行", "sector": "金融", "sub_industry": "股份制银行"},
        {"industry": "房地产", "sector": "房地产", "sub_industry": "房地产开发"},
        {"industry": "医药", "sector": "医药生物", "sub_industry": "中药"},
        {"industry": "电子", "sector": "电子", "sub_industry": "半导体"},
        {"industry": "计算机", "sector": "计算机", "sub_industry": "软件服务"},
        {"industry": "化工", "sector": "化工", "sub_industry": "化学制品"},
        {"industry": "机械设备", "sector": "机械设备", "sub_industry": "通用设备"},
        {"industry": "汽车", "sector": "汽车", "sub_industry": "汽车零部件"},
    ]
    
    selected = industries[random.randint(0, len(industries) - 1)]
    
    return {
        "name": f"股票{code}",
        "industry": selected["industry"],
        "industry_code": f"8010{random.randint(100, 999)}",
        "sector": selected["sector"],
        "sub_industry": selected["sub_industry"]
    }


@router.get("/{code}/industry")
def get_stock_industry(code: str):
    """
    获取股票所属板块
    
    获取指定股票代码的所属板块信息
    
    Args:
        code: 股票代码
        
    Returns:
        dict: 统一响应格式，包含股票所属板块信息
    """
    industry_data = get_mock_industry(code)
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": code,
            "name": industry_data["name"],
            "industry": industry_data["industry"],
            "industry_code": industry_data["industry_code"],
            "sector": industry_data["sector"],
            "sub_industry": industry_data["sub_industry"]
        }
    }
