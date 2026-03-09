# 股票研报历史数据API路由
from fastapi import APIRouter, Path, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional
import random

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票研报"])

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

# 券商名称
BROKER_NAMES = [
    "中信证券", "华泰证券", "中信建投", "国泰君安", "海通证券",
    "广发证券", "招商证券", "申万宏源", "银河证券", "国信证券",
    "兴业证券", "东方证券", "中金公司", "光大证券", "平安证券",
    "中金公司", "天风证券", "国金证券", "华创证券", "民生证券"
]

# 研报标题模板
RESEARCH_TITLES = [
    "首次覆盖：{rating}目标价{target}元",
    "维持{rating}评级，目标价上调至{target}元",
    "年报点评：业绩{comment}，{rating}",
    "季报点评：Q{quarter}业绩超预期，上调至{rating}",
    "深度报告：{topic}领军者",
    "重大事项点评：{event}，维持{rating}",
    "投资价值分析：{rating}，目标价{target}元",
    "行业专题报告：{industry}行业深度研究",
    "跟踪报告：{event}对公司的影响分析",
    "估值分析：当前估值具备吸引力",
    "业绩预告点评：{comment}，{rating}",
    "重大合同点评：{event}，业绩有望提升",
    "产能扩张点评：{project}助力公司成长",
    "技术突破点评：{tech}取得重大进展",
    "政策影响点评：{policy}带来新机遇",
    "竞争格局分析：龙头地位稳固",
    "成本优势分析：护城河持续加深",
    "下游需求点评：需求旺盛，订单充足",
    "产能利用率分析：满产运行，业绩确定性强",
    "现金流分析：经营质量持续改善",
]

# 评级
RATINGS = ["买入", "增持", "中性", "减持", "卖出"]
RATING_MAP = {"买入": 5, "增持": 4, "中性": 3, "减持": 2, "卖出": 1}

# 评价用语
COMMENTS = [
    "符合预期", "超出预期", "低于预期", "大幅增长", "稳健增长",
    "扭亏为盈", "持续向好", "保持稳定", "承压下行", "触底反弹"
]

# 主题
TOPICS = [
    "新能源龙头", "AI领军者", "半导体龙头", "医疗器械龙头",
    "消费升级", "智能制造", "数字化转型", "绿色低碳",
    "国产替代", "产业链一体化", "平台型公司", "技术迭代"
]

# 事件
EVENTS = [
    "签订重大合同", "获得订单", "产能释放", "技术突破",
    "产品发布", "渠道拓展", "战略合作", "并购重组",
    "股权激励", "股份回购", "定增完成", "资产剥离"
]

# 行业
INDUSTRIES = [
    "新能源", "人工智能", "半导体", "医疗器械", "新材料",
    "消费电子", "数字经济", "智能制造", "生物医药", "云计算"
]

# 项目
PROJECTS = [
    "产能扩张", "研发中心建设", "智能化改造", "产业链",
    "海外延伸布局", "一体化项目", "扩产项目", "新建生产基地"
]

# 技术
TECHS = [
    "新技术研发", "工艺改进", "产品迭代", "技术升级",
    "专利获取", "研发突破", "创新产品", "核心技术"
]

# 政策
POLICIES = [
    "产业政策支持", "税收优惠", "补贴政策", "环保政策",
    "行业标准", "准入政策", "发展规划", "专项资金"
]


def generate_research_data(code: str, days: int = 90) -> List[dict]:
    """
    生成模拟的研报历史数据
    
    Args:
        code: 股票代码
        days: 查询天数，默认90天
        
    Returns:
        list: 历史研报列表
    """
    info = STOCK_INFO.get(code, {"name": f"股票{code}", "industry": "未知"})
    
    records = []
    base_date = datetime.now()
    
    # 生成随机数量的研报 (每天 0-2 份)
    for i in range(days):
        date = base_date - timedelta(days=i)
        
        # 每天随机生成 0-2 份研报
        num_reports = random.randint(0, 2)
        
        for _ in range(num_reports):
            # 随机选择研报标题模板
            title_template = random.choice(RESEARCH_TITLES)
            
            # 填充模板变量
            rating = random.choice(RATINGS)
            target = round(random.uniform(10, 500), 2)
            quarter = random.randint(1, 4)
            
            title = title_template.format(
                rating=rating,
                target=target,
                comment=random.choice(COMMENTS),
                topic=random.choice(TOPICS),
                event=random.choice(EVENTS),
                industry=random.choice(INDUSTRIES),
                project=random.choice(PROJECTS),
                tech=random.choice(TECHS),
                policy=random.choice(POLICIES),
                quarter=quarter
            )
            
            # 随机选择券商
            broker = random.choice(BROKER_NAMES)
            
            # 随机选择分析师
            analysts = [
                f"分析师{random.choice(['张', '李', '王', '刘', '陈', '杨', '赵', '黄'])}{random.choice(['明', '华', '伟', '强', '军', '涛', '波', '飞'])}",
                f"团队"
            ]
            
            # 生成发布时间 (当天的随机时间)
            publish_time = date.replace(
                hour=random.randint(9, 17),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            # 随机选择研报类型
            report_type = random.choice([
                "深度报告", "跟踪报告", "点评报告", "定期报告",
                "事件点评", "估值报告", "行业报告", "投资策略"
            ])
            
            # 随机选择研究评级
            research_rating = rating
            
            # 模拟目标价和涨跌幅
            current_price = round(random.uniform(10, 500), 2)
            target_price = round(target, 2)
            upside = round((target_price - current_price) / current_price * 100, 2)
            
            # 模拟阅读量
            views = random.randint(50, 10000)
            
            # 研报亮点
            highlights = random.sample([
                "业绩增长确定性强",
                "行业地位稳固",
                "护城河持续加深",
                "产能释放带来业绩增量",
                "技术优势明显",
                "估值具备吸引力",
                "政策支持力度大",
                "市场需求旺盛",
                "成本控制优秀",
                "管理层优秀"
            ], k=random.randint(2, 4))
            
            records.append({
                "id": f"research_{code}_{i}_{random.randint(1000, 9999)}",
                "date": date.strftime("%Y-%m-%d"),
                "datetime": publish_time.strftime("%Y-%m-%d %H:%M:%S"),
                "code": code,
                "name": info["name"],
                "title": title,
                "broker": broker,
                "analysts": analysts,
                "report_type": report_type,
                "rating": research_rating,
                "rating_score": RATING_MAP.get(research_rating, 3),
                "current_price": current_price,
                "target_price": target_price,
                "upside": upside,
                "views": views,
                "highlights": highlights,
                "url": f"https://example.com/research/{code}/{random.randint(100000, 999999)}",
                "summary": f"{info['name']}研报摘要：{broker}发布研报，维持{research_rating}评级，目标价{target_price}元。分析师认为公司{random.choice(highlights)}，具备长期投资价值。",
                "industry": info["industry"],
                "related_industries": random.sample(INDUSTRIES, k=random.randint(1, 3)),
                "tags": random.sample(["业绩", "增长", "投资评级", "目标价", "行业", "政策", "技术", "订单"], k=random.randint(2, 4)),
            })
    
    # 按时间排序 (最新的在前)
    records.sort(key=lambda x: x["datetime"], reverse=True)
    
    return records


def generate_summary(code: str, data: List[dict]) -> dict:
    """
    生成研报统计摘要
    
    Args:
        code: 股票代码
        data: 研报数据
        
    Returns:
        dict: 统计摘要
    """
    if not data:
        return {
            "total_count": 0,
            "broker_count": 0,
            "rating_count": {},
            "avg_upside": 0,
            "avg_target_price": 0,
            "type_count": {},
        }
    
    # 统计各评级数量
    rating_count = {}
    for report in data:
        rating = report["rating"]
        rating_count[rating] = rating_count.get(rating, 0) + 1
    
    # 统计各类型研报数量
    type_count = {}
    for report in data:
        report_type = report["report_type"]
        type_count[report_type] = type_count.get(report_type, 0) + 1
    
    # 统计券商数量
    broker_count = len(set(r["broker"] for r in data))
    
    # 计算平均目标价和涨跌幅
    valid_reports = [r for r in data if r.get("target_price")]
    if valid_reports:
        avg_target_price = sum(r["target_price"] for r in valid_reports) / len(valid_reports)
        avg_upside = sum(r["upside"] for r in valid_reports) / len(valid_reports)
    else:
        avg_target_price = 0
        avg_upside = 0
    
    return {
        "total_count": len(data),
        "broker_count": broker_count,
        "rating_count": rating_count,
        "avg_upside": round(avg_upside, 2),
        "avg_target_price": round(avg_target_price, 2),
        "type_count": type_count,
        "total_views": sum(r["views"] for r in data),
    }


@router.get("/{code}/research/history")
def get_research_history(
    code: str = Path(..., description="股票代码"),
    days: int = Query(90, ge=1, le=365, description="查询天数，默认90天，最大365天"),
    rating: Optional[str] = Query(None, description="评级筛选 (买入/增持/中性/减持/卖出)"),
    broker: Optional[str] = Query(None, description="券商筛选"),
    report_type: Optional[str] = Query(None, description="研报类型筛选")
):
    """
    获取股票研报历史数据
    
    返回指定股票的历史研报数据及统计摘要
    
    Args:
        code: 股票代码 (如: 600519, 000001)
        days: 查询天数，默认90天，最大365天
        rating: 评级筛选 (买入/增持/中性/减持/卖出) (可选)
        broker: 券商筛选 (可选)
        report_type: 研报类型筛选 (可选)
        
    Returns:
        dict: 统一响应格式，包含历史研报数据和统计摘要
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
    research_data = generate_research_data(code, days)
    
    # 应用筛选条件
    filtered_data = research_data
    if rating:
        filtered_data = [r for r in filtered_data if r["rating"] == rating]
    if broker:
        filtered_data = [r for r in filtered_data if broker in r["broker"]]
    if report_type:
        filtered_data = [r for r in filtered_data if r["report_type"] == report_type]
    
    # 生成摘要 (基于原始数据)
    summary = generate_summary(code, research_data)
    # 更新筛选后的数量
    summary["filtered_count"] = len(filtered_data)
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": code,
            "name": STOCK_INFO.get(code, {}).get("name", f"股票{code}"),
            "total": len(filtered_data),
            "research": filtered_data,
            "summary": summary
        }
    }
