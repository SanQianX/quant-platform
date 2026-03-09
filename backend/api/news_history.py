# 股票新闻历史数据API路由
from fastapi import APIRouter, Path, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional
import random

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票新闻"])

# 股票信息映射
STOCK_INFO = {
    "000001": {"name": "平安银行", "industry": "银行"},
    "000002": {"name": "万 科A", "industry": "房地产"},
    "600519": {"name": "贵州茅台", "industry": "白酒"},
    "600036": {"name": "招商银行", "industry": "银行"},
    "000858": {"name": "五粮液", "industry": "白酒"},
    "300750": {"name": "宁德时代", "industry": "新能源"},
    "601318": {"name": "中国平安", "industry": "保险"},
    "002594": {"name": "比亚迪", "industry": "汽车"},
    "000333": {"name": "美的集团", "industry": "家电"},
    "600900": {"name": "长江电力", "industry": "电力"},
    "601888": {"name": "中国中免", "industry": "旅游"},
    "600276": {"name": "恒瑞医药", "industry": "医药"},
    "000725": {"name": "京东方A", "industry": "电子"},
    "002415": {"name": "海康威视", "industry": "安防"},
    "601012": {"name": "隆基绿能", "industry": "光伏"},
}


# 新闻标题模板
NEWS_TITLES = [
    "发布2024年年度报告，营收同比增长{percent}%",
    "召开业绩说明会，透露未来发展战略",
    "获得重大合同订单，项目金额超{amount}亿元",
    "宣布股份回购计划，回购金额不超过{amount}亿元",
    "子公司中标重大工程项目",
    "发布新产品线，进军{industry}市场",
    "与{company}达成战略合作协议",
    "获批{amount}亿元银行授信额度",
    "发布季度财报，净利润同比增长{percent}%",
    "董事增持公司股票，合计增持{amount}万股",
    "股东减持计划完成，套现{amount}亿元",
    "重大资产重组事项停牌",
    "披露重大关联交易",
    "收到监管问询函",
    "入选沪深300成分股",
    "发布员工持股计划草案",
    "获得国家级科技奖项",
    "投资{amount}亿元建设{project}",
    "设立产业投资基金",
    "参股设立合资公司",
]

# 行业/公司名称
INDUSTRIES = ["新能源", "人工智能", "半导体", "医疗器械", "新材料", "数字经济", "智能制造"]
COMPANIES = ["华为", "腾讯", "阿里", "百度", "京东", "字节跳动", "美团", "宁德时代", "比亚迪"]
PROJECTS = ["生产基地", "研发中心", "数据中心", "物流中心", "产业园区"]


def generate_news_data(code: str, days: int = 30) -> List[dict]:
    """
    生成模拟的新闻历史数据
    
    Args:
        code: 股票代码
        days: 查询天数，默认30天
        
    Returns:
        list: 历史新闻列表
    """
    info = STOCK_INFO.get(code, {"name": f"股票{code}", "industry": "未知"})
    
    records = []
    base_date = datetime.now()
    
    # 生成随机数量的新闻 (每天 0-3 条)
    for i in range(days):
        date = base_date - timedelta(days=i)
        
        # 每天随机生成 0-3 条新闻
        num_news = random.randint(0, 3)
        
        for _ in range(num_news):
            # 随机选择新闻标题模板
            title_template = random.choice(NEWS_TITLES)
            
            # 填充模板变量
            title = title_template.format(
                percent=round(random.uniform(5, 50), 1),
                amount=round(random.uniform(1, 100), 1),
                industry=random.choice(INDUSTRIES),
                company=random.choice(COMPANIES),
                project=random.choice(PROJECTS)
            )
            
            # 随机选择新闻类型
            news_type = random.choice([
                "业绩公告",
                "重大合同",
                "并购重组",
                "增减持",
                "中标公告",
                "战略合作",
                "监管问询",
                "资本运作",
                "经营动态",
                "风险提示"
            ])
            
            # 随机选择新闻来源
            source = random.choice([
                "证券时报",
                "上海证券报",
                "中国证券报",
                "第一财经",
                "每日经济新闻",
                "财新网",
                "华尔街日报",
                "路透社"
            ])
            
            # 随机选择重要程度
            importance = random.choice(["一般", "重要", "非常重要"])
            
            # 模拟阅读量和评论数
            views = random.randint(100, 50000)
            comments = random.randint(0, 200)
            
            # 生成时间 (当天的随机时间)
            news_time = date.replace(
                hour=random.randint(9, 18),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            records.append({
                "id": f"news_{code}_{i}_{random.randint(1000, 9999)}",
                "date": date.strftime("%Y-%m-%d"),
                "datetime": news_time.strftime("%Y-%m-%d %H:%M:%S"),
                "code": code,
                "name": info["name"],
                "title": title,
                "type": news_type,
                "source": source,
                "importance": importance,
                "views": views,
                "comments": comments,
                "url": f"https://example.com/news/{code}/{random.randint(100000, 999999)}",
                "summary": f"{info['name']}{title}。相关市场分析师表示，此举将对公司未来发展产生积极影响。",
                "related_stocks": [code] + random.sample(list(STOCK_INFO.keys())[:5], k=random.randint(0, 2)),
                "tags": random.sample(["业绩", "增长", "投资", "合作", "风险", "市场", "政策"], k=random.randint(1, 3)),
            })
    
    # 按时间排序 (最新的在前)
    records.sort(key=lambda x: x["datetime"], reverse=True)
    
    return records


def generate_summary(code: str, data: List[dict]) -> dict:
    """
    生成新闻统计摘要
    
    Args:
        code: 股票代码
        data: 新闻数据
        
    Returns:
        dict: 统计摘要
    """
    if not data:
        return {
            "total_count": 0,
            "type_count": {},
            "avg_importance": "无",
            "total_views": 0,
            "total_comments": 0,
        }
    
    # 统计各类型新闻数量
    type_count = {}
    for news in data:
        news_type = news["type"]
        type_count[news_type] = type_count.get(news_type, 0) + 1
    
    # 计算平均重要程度
    importance_map = {"一般": 1, "重要": 2, "非常重要": 3}
    avg_score = sum(importance_map.get(n["importance"], 1) for n in data) / len(data)
    if avg_score >= 2.5:
        avg_importance = "非常重要"
    elif avg_score >= 1.5:
        avg_importance = "重要"
    else:
        avg_importance = "一般"
    
    return {
        "total_count": len(data),
        "type_count": type_count,
        "avg_importance": avg_importance,
        "total_views": sum(n["views"] for n in data),
        "total_comments": sum(n["comments"] for n in data),
        "source_count": len(set(n["source"] for n in data)),
    }


@router.get("/{code}/news/history")
def get_news_history(
    code: str = Path(..., description="股票代码"),
    days: int = Query(30, ge=1, le=365, description="查询天数，默认30天，最大365天"),
    news_type: Optional[str] = Query(None, description="新闻类型筛选"),
    importance: Optional[str] = Query(None, description="重要程度筛选")
):
    """
    获取股票新闻历史数据
    
    返回指定股票的历史新闻数据及统计摘要
    
    Args:
        code: 股票代码 (如: 600519, 000001)
        days: 查询天数，默认30天，最大365天
        news_type: 新闻类型筛选 (可选)
        importance: 重要程度筛选 (可选)
        
    Returns:
        dict: 统一响应格式，包含历史新闻数据和统计摘要
    """
    # 验证股票代码格式
    if not code or len(code) < 6:
        raise HTTPException(status_code=400, detail="无效的股票代码")
    
    # 限制查询天数
    if days > 365:
        days = 365
    elif days < 1:
        days = 1
    
    # 生成模拟数据
    news_data = generate_news_data(code, days)
    
    # 应用筛选条件
    filtered_data = news_data
    if news_type:
        filtered_data = [n for n in filtered_data if n["type"] == news_type]
    if importance:
        filtered_data = [n for n in filtered_data if n["importance"] == importance]
    
    # 生成摘要 (基于原始数据)
    summary = generate_summary(code, news_data)
    # 更新筛选后的数量
    summary["filtered_count"] = len(filtered_data)
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": code,
            "name": STOCK_INFO.get(code, {}).get("name", f"股票{code}"),
            "total": len(filtered_data),
            "news": filtered_data,
            "summary": summary
        }
    }
