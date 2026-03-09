# 券商API路由
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel

# 创建路由
router = APIRouter(prefix="/api/broker", tags=["券商"])

# 券商数据模型
class Broker(BaseModel):
    id: str
    name: str
    full_name: str
    logo: Optional[str] = None
    description: Optional[str] = None
    rating: float = 0.0
    features: list = []
    commission: Optional[str] = None
    min_deposit: Optional[str] = None
    supported_markets: list = []

# 模拟券商数据
BROKERS = [
    {
        "id": "1",
        "name": "华泰证券",
        "full_name": "华泰证券股份有限公司",
        "logo": "https://example.com/logos/ht.png",
        "description": "中国领先的综合性证券公司",
        "rating": 4.8,
        "features": ["线上开户", "低佣金", "专业研报", "快速交易"],
        "commission": "万1.5",
        "min_deposit": "无要求",
        "supported_markets": ["A股", "港股", "美股"]
    },
    {
        "id": "2",
        "name": "中信证券",
        "full_name": "中信证券股份有限公司",
        "logo": "https://example.com/logos/zx.png",
        "description": "国内规模最大的证券公司",
        "rating": 4.7,
        "features": ["线上开户", "投顾服务", "融资融券", "机构业务"],
        "commission": "万2.0",
        "min_deposit": "无要求",
        "supported_markets": ["A股", "港股", "期权"]
    },
    {
        "id": "3",
        "name": "国泰君安",
        "full_name": "国泰君安证券股份有限公司",
        "logo": "https://example.com/logos/gtja.png",
        "description": "中国证券行业知名券商",
        "rating": 4.6,
        "features": ["线上开户", "智能投顾", "基金理财", "国债逆回购"],
        "commission": "万1.8",
        "min_deposit": "无要求",
        "supported_markets": ["A股", "基金", "债券"]
    },
    {
        "id": "4",
        "name": "银河证券",
        "full_name": "中国银河证券股份有限公司",
        "logo": "https://example.com/logos/yh.png",
        "description": "国内知名综合性券商",
        "rating": 4.5,
        "features": ["线上开户", "股票开户", "基金代销", "融资融券"],
        "commission": "万1.6",
        "min_deposit": "无要求",
        "supported_markets": ["A股", "港股", "基金"]
    },
    {
        "id": "5",
        "name": "海通证券",
        "full_name": "海通证券股份有限公司",
        "logo": "https://example.com/logos/htsec.png",
        "description": "大型综合性券商",
        "rating": 4.4,
        "features": ["线上开户", "新客专享", "专业研报", "融资融券"],
        "commission": "万1.5",
        "min_deposit": "无要求",
        "supported_markets": ["A股", "期权", "期货"]
    },
    {
        "id": "6",
        "name": "广发证券",
        "full_name": "广发证券股份有限公司",
        "logo": "https://example.com/logos/gf.png",
        "description": "国内知名券商",
        "rating": 4.4,
        "features": ["线上开户", "易淘金APP", "基金理财", "财富管理"],
        "commission": "万1.5",
        "min_deposit": "无要求",
        "supported_markets": ["A股", "港股", "基金"]
    },
    {
        "id": "7",
        "name": "招商证券",
        "full_name": "招商证券股份有限公司",
        "logo": "https://example.com/logos/cmb.png",
        "description": "招商银行旗下券商",
        "rating": 4.5,
        "features": ["线上开户", "银行背景", "财富管理", "VIP服务"],
        "commission": "万1.7",
        "min_deposit": "无要求",
        "supported_markets": ["A股", "港股", "美股"]
    },
    {
        "id": "8",
        "name": "申万宏源",
        "full_name": "申万宏源证券有限公司",
        "logo": "https://example.com/logos/swhy.png",
        "description": "大型综合类券商",
        "rating": 4.3,
        "features": ["线上开户", "研究所", "机构业务", "融资融券"],
        "commission": "万1.8",
        "min_deposit": "无要求",
        "supported_markets": ["A股", "期权", "基金"]
    },
    {
        "id": "9",
        "name": "中金公司",
        "full_name": "中国国际金融股份有限公司",
        "logo": "https://example.com/logos/cicc.png",
        "description": "国内顶级投资银行",
        "rating": 4.9,
        "features": ["线上开户", "投行服务", "财富管理", "机构业务"],
        "commission": "万2.5",
        "min_deposit": "50万",
        "supported_markets": ["A股", "港股", "美股", "机构"]
    },
    {
        "id": "10",
        "name": "东方证券",
        "full_name": "东方证券股份有限公司",
        "logo": "https://example.com/logos/dfzq.png",
        "description": "综合性券商",
        "rating": 4.2,
        "features": ["线上开户", "东方财富APP", "基金代销", "投顾服务"],
        "commission": "万1.5",
        "min_deposit": "无要求",
        "supported_markets": ["A股", "基金", "期权"]
    }
]

@router.get("/list")
def get_broker_list():
    """
    获取券商列表
    
    返回所有支持的券商列表
    
    Returns:
        dict: 统一响应格式，包含券商列表
    """
    return {
        "code": 0,
        "message": "success",
        "data": BROKERS
    }

@router.get("/{broker_id}")
def get_broker_detail(broker_id: str):
    """
    获取券商详情
    
    根据券商ID获取券商详细信息
    
    Args:
        broker_id: 券商ID
        
    Returns:
        dict: 统一响应格式，包含券商详情
        
    Raises:
        HTTPException: 券商不存在时抛出404错误
    """
    # 查找券商
    for broker in BROKERS:
        if broker["id"] == broker_id:
            return {
                "code": 0,
                "message": "success",
                "data": broker
            }
    
    # 券商不存在
    raise HTTPException(status_code=404, detail="券商不存在")
