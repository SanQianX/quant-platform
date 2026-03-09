# 投资组合管理 API
"""
投资组合管理接口
提供组合列表、持仓管理、绩效分析等功能
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
import uuid
import math

from api.auth import get_current_user_dep, get_admin_user

router = APIRouter(prefix="/api/portfolio", tags=["投资组合"])

# ==================== 数据模型 ====================

# 内存存储（生产环境应使用数据库）
# 投资组合数据
portfolios_db = {}
# 持仓数据: {portfolio_id: [holdings]}
holdings_db = {}

# 组合基础模型
class PortfolioBase(BaseModel):
    name: str = Field(..., description="组合名称")
    description: Optional[str] = Field(None, description="组合描述")
    initial_capital: float = Field(1000000, description="初始资金")

# 创建组合请求
class PortfolioCreate(PortfolioBase):
    pass

# 更新组合请求
class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# 组合响应
class PortfolioResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    initial_capital: float
    current_value: float
    total_return: float
    total_return_pct: float
    created_at: str
    updated_at: str

# 持仓基础模型
class HoldingBase(BaseModel):
    stock_code: str = Field(..., description="股票代码")
    stock_name: str = Field(..., description="股票名称")
    shares: int = Field(..., description="持股数量")
    avg_cost: float = Field(..., description="平均成本价")

# 添加持仓请求
class HoldingCreate(HoldingBase):
    pass

# 持仓响应
class HoldingResponse(BaseModel):
    id: str
    stock_code: str
    stock_name: str
    shares: int
    avg_cost: float
    current_price: float
    market_value: float
    profit_loss: float
    profit_loss_pct: float

# 绩效指标响应
class PerformanceResponse(BaseModel):
    portfolio_id: str
    total_return: float
    total_return_pct: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    holdings_count: int
    last_updated: str

# ==================== 辅助函数 ====================

def calculate_performance(portfolio_id: str) -> dict:
    """计算投资组合绩效"""
    portfolio = portfolios_db.get(portfolio_id)
    if not portfolio:
        return None
    
    holdings = holdings_db.get(portfolio_id, [])
    
    # 模拟计算（实际应从数据库获取历史数据）
    total_return = portfolio["current_value"] - portfolio["initial_capital"]
    total_return_pct = (total_return / portfolio["initial_capital"]) * 100 if portfolio["initial_capital"] > 0 else 0
    
    # 简化夏普比率计算（假设无风险利率为3%）
    risk_free_rate = 3.0
    if total_return_pct > 0:
        # 模拟波动率
        volatility = abs(total_return_pct) * 0.5
        sharpe_ratio = (total_return_pct - risk_free_rate) / volatility if volatility > 0 else 0
    else:
        sharpe_ratio = 0
    
    # 模拟最大回撤
    max_drawdown = abs(total_return_pct) * 0.3 if total_return_pct < 0 else 0
    
    # 胜率（简化计算）
    win_rate = 60.0 if total_return_pct > 0 else 40.0
    
    # 交易次数
    total_trades = len(holdings) * 2
    
    return {
        "portfolio_id": portfolio_id,
        "total_return": round(total_return, 2),
        "total_return_pct": round(total_return_pct, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "max_drawdown": round(max_drawdown, 2),
        "win_rate": round(win_rate, 2),
        "total_trades": total_trades,
        "holdings_count": len(holdings),
        "last_updated": datetime.now().isoformat()
    }

def update_portfolio_value(portfolio_id: str):
    """更新组合当前市值"""
    holdings = holdings_db.get(portfolio_id, [])
    total_value = 0
    
    for holding in holdings:
        # 简化：假设当前价格等于成本价（实际应调用实时行情API）
        current_price = holding["avg_cost"] * 1.1  # 模拟10%上涨
        holding["current_price"] = current_price
        holding["market_value"] = current_price * holding["shares"]
        holding["profit_loss"] = (current_price - holding["avg_cost"]) * holding["shares"]
        holding["profit_loss_pct"] = ((current_price - holding["avg_cost"]) / holding["avg_cost"]) * 100 if holding["avg_cost"] > 0 else 0
        total_value += holding["market_value"]
    
    # 如果没有持仓，使用初始资金
    if total_value == 0:
        portfolio = portfolios_db.get(portfolio_id)
        if portfolio:
            total_value = portfolio["initial_capital"]
    
    return total_value

# ==================== 投资组合 API ====================

@router.get("", response_model=List[PortfolioResponse])
def get_portfolios(current_user: dict = Depends(get_current_user_dep)):
    """
    获取用户投资组合列表
    
    需要认证
    返回用户的所有投资组合
    """
    username = current_user["username"]
    
    # 过滤属于当前用户的组合
    user_portfolios = [
        p for p in portfolios_db.values() 
        if p.get("owner") == username
    ]
    
    result = []
    for p in user_portfolios:
        current_value = update_portfolio_value(p["id"])
        p["current_value"] = current_value
        total_return = current_value - p["initial_capital"]
        total_return_pct = (total_return / p["initial_capital"]) * 100 if p["initial_capital"] > 0 else 0
        
        result.append({
            "id": p["id"],
            "name": p["name"],
            "description": p.get("description"),
            "initial_capital": p["initial_capital"],
            "current_value": round(current_value, 2),
            "total_return": round(total_return, 2),
            "total_return_pct": round(total_return_pct, 2),
            "created_at": p["created_at"],
            "updated_at": p["updated_at"]
        })
    
    return result


@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: dict = Depends(get_current_user_dep)
):
    """
    创建新投资组合
    
    需要认证
    """
    portfolio_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    username = current_user["username"]
    
    new_portfolio = {
        "id": portfolio_id,
        "name": portfolio_data.name,
        "description": portfolio_data.description,
        "initial_capital": portfolio_data.initial_capital,
        "current_value": portfolio_data.initial_capital,
        "owner": username,
        "created_at": now,
        "updated_at": now
    }
    
    portfolios_db[portfolio_id] = new_portfolio
    holdings_db[portfolio_id] = []
    
    return {
        "id": new_portfolio["id"],
        "name": new_portfolio["name"],
        "description": new_portfolio.get("description"),
        "initial_capital": new_portfolio["initial_capital"],
        "current_value": new_portfolio["current_value"],
        "total_return": 0,
        "total_return_pct": 0,
        "created_at": new_portfolio["created_at"],
        "updated_at": new_portfolio["updated_at"]
    }


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio(portfolio_id: str, current_user: dict = Depends(get_current_user_dep)):
    """
    获取投资组合详情
    
    需要认证
    返回组合信息和持仓列表
    """
    portfolio = portfolios_db.get(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在")
    
    # 验证所有权
    username = current_user["username"]
    if portfolio.get("owner") != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权访问此投资组合")
    
    # 更新市值
    current_value = update_portfolio_value(portfolio_id)
    portfolio["current_value"] = current_value
    
    total_return = current_value - portfolio["initial_capital"]
    total_return_pct = (total_return / portfolio["initial_capital"]) * 100 if portfolio["initial_capital"] > 0 else 0
    
    return {
        "id": portfolio["id"],
        "name": portfolio["name"],
        "description": portfolio.get("description"),
        "initial_capital": portfolio["initial_capital"],
        "current_value": round(current_value, 2),
        "total_return": round(total_return, 2),
        "total_return_pct": round(total_return_pct, 2),
        "created_at": portfolio["created_at"],
        "updated_at": portfolio["updated_at"]
    }


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: str,
    portfolio_data: PortfolioUpdate,
    current_user: dict = Depends(get_current_user_dep)
):
    """
    更新投资组合信息
    
    需要认证
    """
    portfolio = portfolios_db.get(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在")
    
    # 验证所有权
    username = current_user["username"]
    if portfolio.get("owner") != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权修改此投资组合")
    
    # 更新字段
    now = datetime.now().isoformat()
    if portfolio_data.name is not None:
        portfolio["name"] = portfolio_data.name
    if portfolio_data.description is not None:
        portfolio["description"] = portfolio_data.description
    
    portfolio["updated_at"] = now
    
    # 重新计算市值
    current_value = update_portfolio_value(portfolio_id)
    portfolio["current_value"] = current_value
    total_return = current_value - portfolio["initial_capital"]
    total_return_pct = (total_return / portfolio["initial_capital"]) * 100 if portfolio["initial_capital"] > 0 else 0
    
    return {
        "id": portfolio["id"],
        "name": portfolio["name"],
        "description": portfolio.get("description"),
        "initial_capital": portfolio["initial_capital"],
        "current_value": round(current_value, 2),
        "total_return": round(total_return, 2),
        "total_return_pct": round(total_return_pct, 2),
        "created_at": portfolio["created_at"],
        "updated_at": portfolio["updated_at"]
    }


@router.delete("/{portfolio_id}")
def delete_portfolio(portfolio_id: str, current_user: dict = Depends(get_current_user_dep)):
    """
    删除投资组合
    
    需要认证
    """
    portfolio = portfolios_db.get(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在")
    
    # 验证所有权
    username = current_user["username"]
    if portfolio.get("owner") != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权删除此投资组合")
    
    # 删除组合和持仓
    del portfolios_db[portfolio_id]
    if portfolio_id in holdings_db:
        del holdings_db[portfolio_id]
    
    return {"message": "投资组合删除成功", "portfolio_id": portfolio_id}


# ==================== 持仓管理 API ====================

@router.get("/{portfolio_id}/holdings", response_model=List[HoldingResponse])
def get_holdings(portfolio_id: str, current_user: dict = Depends(get_current_user_dep)):
    """
    获取投资组合持仓
    
    需要认证
    """
    portfolio = portfolios_db.get(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在")
    
    # 验证所有权
    username = current_user["username"]
    if portfolio.get("owner") != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权访问此投资组合")
    
    # 更新市值
    update_portfolio_value(portfolio_id)
    
    holdings = holdings_db.get(portfolio_id, [])
    result = []
    for h in holdings:
        result.append({
            "id": h["id"],
            "stock_code": h["stock_code"],
            "stock_name": h["stock_name"],
            "shares": h["shares"],
            "avg_cost": h["avg_cost"],
            "current_price": round(h.get("current_price", h["avg_cost"]), 2),
            "market_value": round(h.get("market_value", 0), 2),
            "profit_loss": round(h.get("profit_loss", 0), 2),
            "profit_loss_pct": round(h.get("profit_loss_pct", 0), 2)
        })
    
    return result


@router.post("/{portfolio_id}/holdings", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
def add_holding(
    portfolio_id: str,
    holding_data: HoldingCreate,
    current_user: dict = Depends(get_current_user_dep)
):
    """
    添加持仓
    
    需要认证
    添加股票到投资组合
    """
    portfolio = portfolios_db.get(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在")
    
    # 验证所有权
    username = current_user["username"]
    if portfolio.get("owner") != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权修改此投资组合")
    
    holding_id = str(uuid.uuid4())[:8]
    
    # 检查是否已存在该股票持仓
    holdings = holdings_db.get(portfolio_id, [])
    existing = next((h for h in holdings if h["stock_code"] == holding_data.stock_code), None)
    
    if existing:
        # 更新现有持仓
        total_shares = existing["shares"] + holding_data.shares
        total_cost = (existing["avg_cost"] * existing["shares"]) + (holding_data.avg_cost * holding_data.shares)
        new_avg_cost = total_cost / total_shares
        
        existing["shares"] = total_shares
        existing["avg_cost"] = new_avg_cost
        existing["id"] = existing.get("id", holding_id)
        
        # 更新市值
        current_price = existing["avg_cost"] * 1.1
        existing["current_price"] = current_price
        existing["market_value"] = current_price * total_shares
        existing["profit_loss"] = (current_price - new_avg_cost) * total_shares
        existing["profit_loss_pct"] = ((current_price - new_avg_cost) / new_avg_cost) * 100
        
        return {
            "id": existing["id"],
            "stock_code": existing["stock_code"],
            "stock_name": existing["stock_name"],
            "shares": existing["shares"],
            "avg_cost": round(existing["avg_cost"], 2),
            "current_price": round(current_price, 2),
            "market_value": round(existing["market_value"], 2),
            "profit_loss": round(existing["profit_loss"], 2),
            "profit_loss_pct": round(existing["profit_loss_pct"], 2)
        }
    
    # 创建新持仓
    new_holding = {
        "id": holding_id,
        "stock_code": holding_data.stock_code,
        "stock_name": holding_data.stock_name,
        "shares": holding_data.shares,
        "avg_cost": holding_data.avg_cost,
        "current_price": holding_data.avg_cost * 1.1,
        "market_value": holding_data.avg_cost * 1.1 * holding_data.shares,
        "profit_loss": holding_data.avg_cost * 0.1 * holding_data.shares,
        "profit_loss_pct": 10.0
    }
    
    holdings_db.setdefault(portfolio_id, []).append(new_holding)
    
    # 更新组合时间
    portfolio["updated_at"] = datetime.now().isoformat()
    
    return {
        "id": new_holding["id"],
        "stock_code": new_holding["stock_code"],
        "stock_name": new_holding["stock_name"],
        "shares": new_holding["shares"],
        "avg_cost": round(new_holding["avg_cost"], 2),
        "current_price": round(new_holding["current_price"], 2),
        "market_value": round(new_holding["market_value"], 2),
        "profit_loss": round(new_holding["profit_loss"], 2),
        "profit_loss_pct": round(new_holding["profit_loss_pct"], 2)
    }


@router.delete("/{portfolio_id}/holdings/{holding_id}")
def delete_holding(
    portfolio_id: str,
    holding_id: str,
    current_user: dict = Depends(get_current_user_dep)
):
    """
    删除持仓
    
    需要认证
    """
    portfolio = portfolios_db.get(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在")
    
    # 验证所有权
    username = current_user["username"]
    if portfolio.get("owner") != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权修改此投资组合")
    
    holdings = holdings_db.get(portfolio_id, [])
    holding = next((h for h in holdings if h["id"] == holding_id), None)
    
    if not holding:
        raise HTTPException(status_code=404, detail="持仓不存在")
    
    # 删除持仓
    holdings = [h for h in holdings if h["id"] != holding_id]
    holdings_db[portfolio_id] = holdings
    
    # 更新组合时间
    portfolio["updated_at"] = datetime.now().isoformat()
    
    return {"message": "持仓删除成功", "holding_id": holding_id}


# ==================== 绩效分析 API ====================

@router.get("/{portfolio_id}/performance", response_model=PerformanceResponse)
def get_performance(portfolio_id: str, current_user: dict = Depends(get_current_user_dep)):
    """
    获取投资组合绩效
    
    需要认证
    返回收益率、夏普比率等绩效指标
    """
    portfolio = portfolios_db.get(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在")
    
    # 验证所有权
    username = current_user["username"]
    if portfolio.get("owner") != username and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="无权访问此投资组合")
    
    # 更新市值
    update_portfolio_value(portfolio_id)
    
    # 计算绩效
    performance = calculate_performance(portfolio_id)
    
    if not performance:
        raise HTTPException(status_code=404, detail="无法计算绩效")
    
    return performance
