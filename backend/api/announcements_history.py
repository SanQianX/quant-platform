# 股票公告历史数据API路由
from fastapi import APIRouter, Path, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional
import random

# 创建路由
router = APIRouter(prefix="/api/stock", tags=["股票公告"])

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


# 公告类型
ANNOUNCEMENT_TYPES = [
    {"type": "年度报告", "code": "annual"},
    {"type": "一季度报告", "code": "q1"},
    {"type": "半年度报告", "code": "midyear"},
    {"type": "三季度报告", "code": "q3"},
    {"type": "业绩预告", "code": "forecast"},
    {"type": "业绩快报", "code": "express"},
    {"type": "分红送转", "code": "dividend"},
    {"type": "配股增发", "code": "spo"},
    {"type": "增减持公告", "code": "holding"},
    {"type": "停牌复牌", "code": "suspension"},
    {"type": "重大合同", "code": "contract"},
    {"type": "资产重组", "code": "restructure"},
    {"type": "股权激励", "code": "equity"},
    {"type": "关联交易", "code": "related"},
    {"type": "风险提示", "code": "risk"},
    {"type": "监管问询", "code": "inquiry"},
    {"type": "募集资金", "code": "funds"},
    {"type": "对外投资", "code": "investment"},
    {"type": "担保事项", "code": "guarantee"},
    {"type": "诉讼仲裁", "code": "lawsuit"},
]


# 公告标题模板
ANNOUNCEMENT_TITLES = {
    "annual": [
        "关于{year}年年度报告的公告",
        "{year}年年度报告摘要",
        "{year}年度报告补充公告",
    ],
    "q1": [
        "关于{year}年一季度报告的公告",
        "{year}年第一季度报告正文",
        "{year}一季度业绩预告",
    ],
    "midyear": [
        "关于{year}年半年度报告的公告",
        "{year}年中期报告摘要",
        "{year}半年度报告补充公告",
    ],
    "q3": [
        "关于{year}年三季度报告的公告",
        "{year}年第三季度报告正文",
        "{year}三季度业绩预告",
    ],
    "forecast": [
        "{year}年度业绩预告公告",
        "关于{year}年业绩预告的公告",
        "业绩预增公告",
        "业绩预亏公告",
    ],
    "express": [
        "{year}年度业绩快报",
        "{year}年业绩快报补充公告",
    ],
    "dividend": [
        "关于{year}年度利润分配方案的公告",
        "分红派息实施公告",
        "送转股实施公告",
        "资本公积金转增股本预案",
    ],
    "spo": [
        "配股发行公告",
        "增发A股股票发行结果公告",
        "关于配股申请获批的公告",
        "增发股票上市公告书",
    ],
    "holding": [
        "关于持股5%以上股东增持股份的公告",
        "关于控股股东减持股份的预披露公告",
        "股东增持/减持股份计划完成公告",
        "持股5%以下股东减持股份提示性公告",
    ],
    "suspension": [
        "股票停牌公告",
        "股票复牌公告",
        "重大事项停牌公告",
        "停牌进展公告",
    ],
    "contract": [
        "关于签订重大合同的公告",
        "中标候选公示",
        "日常经营合同签订公告",
        "重大合同进展公告",
    ],
    "restructure": [
        "重大资产重组停牌公告",
        "关于重大资产重组进展的公告",
        "资产购买暨关联交易报告书",
        "重大资产重组预案",
    ],
    "equity": [
        "股权激励计划草案",
        "关于股权激励授予登记完成的公告",
        "股权激励计划调整公告",
        "限制性股票激励计划",
    ],
    "related": [
        "关联交易公告",
        "关于日常关联交易的公告",
        "关联担保公告",
        "关联资产转让公告",
    ],
    "risk": [
        "风险提示公告",
        "关于公司股票可能被实施退市风险警示的提示性公告",
        "重大风险提示公告",
        "关于诉讼风险的提示性公告",
    ],
    "inquiry": [
        "关于收到问询函的公告",
        "问询函回复公告",
        "监管函回复公告",
    ],
    "funds": [
        "募集资金存放与使用情况的专项报告",
        "募集资金使用完毕注销账户公告",
        "变更募集资金用途公告",
    ],
    "investment": [
        "对外投资设立子公司的公告",
        "关于参与设立产业基金的公告",
        "对外投资进展公告",
        "收购资产公告",
    ],
    "guarantee": [
        "对外担保事项公告",
        "关联担保事项公告",
        "解除担保责任公告",
        "担保逾期公告",
    ],
    "lawsuit": [
        "诉讼事项公告",
        "仲裁事项公告",
        "重大诉讼进展公告",
        "关于诉讼终结的公告",
    ],
}


def generate_announcement_data(code: str, days: int = 90) -> List[dict]:
    """
    生成模拟的公告历史数据
    
    Args:
        code: 股票代码
        days: 查询天数，默认90天
        
    Returns:
        list: 历史公告列表
    """
    info = STOCK_INFO.get(code, {"name": f"股票{code}", "industry": "未知"})
    current_year = datetime.now().year
    
    records = []
    base_date = datetime.now()
    
    # 每月至少生成1-2条公告
    months = days // 30 + 1
    
    for month in range(months):
        # 每月生成1-4条公告
        num_announcements = random.randint(1, 4)
        
        for _ in range(num_announcements):
            # 随机选择公告类型
            ann_type = random.choice(ANNOUNCEMENT_TYPES)
            
            # 生成日期
            days_ago = random.randint(month * 30, (month + 1) * 30)
            ann_date = base_date - timedelta(days=days_ago)
            
            # 生成年份
            year = current_year if days_ago < 180 else current_year - 1
            
            # 生成标题
            title_templates = ANNOUNCEMENT_TITLES.get(ann_type["code"], ["关于公司事项的公告"])
            title = random.choice(title_templates)
            if "{year}" in title:
                title = title.format(year=year)
            
            # 随机选择公告来源
            source = random.choice([
                "公司公告",
                "证券时报",
                "上海证券报",
                "中国证券报",
                "巨潮资讯网",
                "交易所公告",
            ])
            
            # 随机选择重要程度
            importance = random.choice(["一般", "重要", "非常重要"])
            
            # 随机选择披露状态
            disclosure_status = random.choice([
                "已披露",
                "已取消",
                "延期披露",
            ])
            
            # 生成模拟数据
            record = {
                "id": f"ann_{code}_{ann_date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}",
                "announcement_id": f"{code}{ann_date.strftime('%Y%m%d')}{random.randint(1000, 9999)}",
                "date": ann_date.strftime("%Y-%m-%d"),
                "datetime": ann_date.strftime("%Y-%m-%d %H:%M:%S"),
                "code": code,
                "name": info["name"],
                "title": title,
                "type": ann_type["type"],
                "type_code": ann_type["code"],
                "source": source,
                "importance": importance,
                "disclosure_status": disclosure_status,
                "url": f"https://example.com/announcement/{code}/{ann_date.strftime('%Y%m%d')}/{random.randint(100000, 999999)}",
                "pdf_url": f"https://example.com/announcement/pdf/{code}/{ann_date.strftime('%Y%m%d')}/{random.randint(100000, 999999)}.pdf",
                "summary": f"{info['name']}{ann_date.strftime('%Y年%m月%d日')}发布公告：{title}。该公告对公司经营可能产生一定影响。",
                "industry": info["industry"],
                "market": "A股",
                "exchange": "上交所" if code.startswith("6") else "深交所",
            }
            
            # 根据公告类型添加特定字段
            if ann_type["code"] in ["annual", "q1", "midyear", "q3"]:
                record["revenue"] = round(random.uniform(10, 1000), 2)
                record["revenue_yoy"] = round(random.uniform(-20, 50), 2)
                record["profit"] = round(random.uniform(1, 200), 2)
                record["profit_yoy"] = round(random.uniform(-30, 60), 2)
                record["eps"] = round(random.uniform(0.1, 10), 2)
            
            if ann_type["code"] == "dividend":
                record["dividend_per_share"] = round(random.uniform(0.1, 5), 2)
                record["bonus_share_ratio"] = round(random.uniform(0, 10), 2)
                record["dividend_date"] = (ann_date + timedelta(days=30)).strftime("%Y-%m-%d")
            
            if ann_type["code"] == "spo":
                record["issue_price"] = round(random.uniform(5, 100), 2)
                record["issue_size"] = round(random.uniform(1, 100), 2)
                record["raising_funds"] = round(random.uniform(1, 50), 2)
            
            if ann_type["code"] == "holding":
                record["shareholder_name"] = f"股东-{random.randint(1, 10)}"
                record["change_ratio"] = round(random.uniform(0.1, 5), 2)
                record["before_holding"] = round(random.uniform(1, 30), 2)
                record["after_holding"] = round(random.uniform(1, 30), 2)
            
            if ann_type["code"] == "contract":
                record["contract_amount"] = round(random.uniform(0.5, 50), 2)
                record["contract_type"] = random.choice(["采购合同", "销售合同", "工程合同", "服务合同"])
            
            if ann_type["code"] == "equity":
                record["激励数量"] = round(random.uniform(0.1, 5), 2)
                record["行权价格"] = round(random.uniform(5, 100), 2)
                record["激励对象人数"] = random.randint(10, 500)
            
            records.append(record)
    
    # 按时间排序 (最新的在前)
    records.sort(key=lambda x: x["datetime"], reverse=True)
    
    return records


def generate_summary(code: str, data: List[dict]) -> dict:
    """
    生成公告统计摘要
    
    Args:
        code: 股票代码
        data: 公告数据
        
    Returns:
        dict: 统计摘要
    """
    if not data:
        return {
            "total_count": 0,
            "type_count": {},
            "importance_count": {},
            "monthly_count": {},
        }
    
    # 统计各类型公告数量
    type_count = {}
    for ann in data:
        ann_type = ann["type"]
        type_count[ann_type] = type_count.get(ann_type, 0) + 1
    
    # 统计各重要程度数量
    importance_count = {}
    for ann in data:
        imp = ann["importance"]
        importance_count[imp] = importance_count.get(imp, 0) + 1
    
    # 按月统计
    monthly_count = {}
    for ann in data:
        month = ann["date"][:7]  # YYYY-MM
        monthly_count[month] = monthly_count.get(month, 0) + 1
    
    return {
        "total_count": len(data),
        "type_count": type_count,
        "importance_count": importance_count,
        "monthly_count": monthly_count,
    }


@router.get("/{code}/announcements/history")
def get_announcements_history(
    code: str = Path(..., description="股票代码"),
    days: int = Query(90, ge=1, le=365, description="查询天数，默认90天，最大365天"),
    ann_type: Optional[str] = Query(None, description="公告类型筛选"),
    importance: Optional[str] = Query(None, description="重要程度筛选")
):
    """
    获取股票公告历史数据
    
    返回指定股票的历史公告数据及统计摘要
    
    Args:
        code: 股票代码 (如: 600519, 000001)
        days: 查询天数，默认90天，最大365天
        ann_type: 公告类型筛选 (可选)
        importance: 重要程度筛选 (可选)
        
    Returns:
        dict: 统一响应格式，包含历史公告数据和统计摘要
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
    announcement_data = generate_announcement_data(code, days)
    
    # 应用筛选条件
    filtered_data = announcement_data
    if ann_type:
        filtered_data = [a for a in filtered_data if a["type"] == ann_type]
    if importance:
        filtered_data = [a for a in filtered_data if a["importance"] == importance]
    
    # 生成摘要 (基于原始数据)
    summary = generate_summary(code, announcement_data)
    # 更新筛选后的数量
    summary["filtered_count"] = len(filtered_data)
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "code": code,
            "name": STOCK_INFO.get(code, {}).get("name", f"股票{code}"),
            "total": len(filtered_data),
            "announcements": filtered_data,
            "summary": summary
        }
    }
