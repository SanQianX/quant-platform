# 模拟交易API路由
"""
模拟交易功能接口

提供模拟下单、持仓查询、交易记录查询、账户余额查询等功能
使用内存模拟交易
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.response import success_response, error_response
from config import MOCK_DATA_CONFIG
from utils.logger import logger
import random
import uuid

# 创建路由
router = APIRouter(prefix="/api/trade", tags=["模拟交易"])

# ============ 内存存储 ============
# 账户余额
_account_balance = {
    "cash": 1000000.0,  # 初始资金100万
    "frozen": 0.0,  # 冻结资金
    "total_assets": 1000000.0,  # 总资产
    "market_value": 0.0,  # 市值
}

# 持仓列表
_positions = {}  # {stock_code: Position}

# 交易历史
_trade_history = []  # [Order]


# ============ 数据模型 ============
class OrderRequest(BaseModel):
    """下单请求"""
    stock_code: str
    stock_name: Optional[str] = None
    direction: str  # "buy" 或 "sell"
    price: float  # 下单价格
    quantity: int  # 数量（手）
    order_type: str = "limit"  # "limit" 或 "market"


class Order(BaseModel):
    """订单"""
    order_id: str
    stock_code: str
    stock_name: str
    direction: str
    price: float
    quantity: int
    order_type: str
    status: str  # "pending" / "filled" / "cancelled" / "rejected"
    filled_price: Optional[float] = None
    filled_quantity: int = 0
    created_at: str
    updated_at: str


class Position(BaseModel):
    """持仓"""
    stock_code: str
    stock_name: str
    quantity: int  # 持有数量（股）
    avg_cost: float  # 平均成本
    current_price: float  # 当前价格
    market_value: float  # 市值
    profit_loss: float  # 浮动盈亏
    profit_loss_pct: float  # 盈亏比例


class Balance(BaseModel):
    """账户余额"""
    cash: float  # 可用资金
    frozen: float  # 冻结资金
    total_assets: float  # 总资产
    market_value: float  # 市值


# ============ 辅助函数 ============
def get_mock_price(stock_code: str) -> float:
    """获取模拟价格"""
    seed = int(stock_code) if stock_code.isdigit() else hash(stock_code) % 10000
    random.seed(seed)
    
    base_prices = {
        "600519": 1850.0,
        "000001": 12.5,
        "300750": 210.0,
        "600036": 36.0,
        "601318": 46.0,
        "000858": 155.0,
        "002594": 260.0,
        "600900": 23.0,
        "601888": 72.0,
        "300059": 21.0,
    }
    return base_prices.get(stock_code, 50.0) * (1 + random.uniform(-0.02, 0.02))


def update_account_balance():
    """更新账户余额"""
    global _account_balance
    
    # 计算总市值
    total_market_value = 0.0
    for pos in _positions.values():
        total_market_value += pos["market_value"]
    
    _account_balance["market_value"] = total_market_value
    _account_balance["total_assets"] = _account_balance["cash"] + total_market_value


def update_position(stock_code: str, stock_name: str, direction: str, filled_price: float, filled_quantity: int):
    """更新持仓"""
    global _positions
    
    if stock_code not in _positions:
        _positions[stock_code] = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "quantity": 0,
            "avg_cost": 0.0,
            "current_price": filled_price,
            "market_value": 0.0,
            "profit_loss": 0.0,
            "profit_loss_pct": 0.0
        }
    
    pos = _positions[stock_code]
    
    if direction == "buy":
        # 买入：增加持仓
        total_cost = pos["quantity"] * pos["avg_cost"] + filled_quantity * filled_price
        pos["quantity"] += filled_quantity
        pos["avg_cost"] = total_cost / pos["quantity"] if pos["quantity"] > 0 else 0.0
    else:
        # 卖出：减少持仓
        pos["quantity"] -= filled_quantity
        if pos["quantity"] <= 0:
            del _positions[stock_code]
            return
    
    # 更新当前价格和市值
    pos["current_price"] = filled_price
    pos["market_value"] = pos["quantity"] * pos["current_price"]
    
    # 计算浮动盈亏
    if pos["quantity"] > 0:
        pos["profit_loss"] = (pos["current_price"] - pos["avg_cost"]) * pos["quantity"]
        pos["profit_loss_pct"] = (pos["current_price"] - pos["avg_cost"]) / pos["avg_cost"] * 100 if pos["avg_cost"] > 0 else 0.0


# ============ API 接口 ============
@router.post("/order")
def create_order(order: OrderRequest):
    """
    下单
    
    买入或卖出股票
    
    Args:
        order: 下单请求
        
    Returns:
        dict: 统一响应格式，包含订单信息
    """
    logger.info(f"下单: {order.stock_code}, {order.direction}, {order.price}, {order.quantity}")
    
    # 验证股票代码
    if not order.stock_code or len(order.stock_code) != 6:
        return error_response("股票代码格式错误，应为6位数字")
    
    # 验证方向
    if order.direction not in ["buy", "sell"]:
        return error_response("交易方向错误，应为 buy 或 sell")
    
    # 验证数量
    if order.quantity <= 0:
        return error_response("数量必须大于0")
    
    # 验证价格
    if order.price <= 0:
        return error_response("价格必须大于0")
    
    # 获取股票名称
    stock_name = order.stock_name or f"股票{order.stock_code}"
    
    # 模拟成交（直接以限价成交）
    filled_price = order.price
    filled_quantity = order.quantity * 100  # 手转股
    
    # 计算交易金额
    trade_amount = filled_price * filled_quantity
    commission = trade_amount * 0.0003  # 佣金万三
    
    if order.direction == "buy":
        # 买入：检查资金是否足够
        total_cost = trade_amount + commission
        if _account_balance["cash"] < total_cost:
            return error_response("资金不足")
        
        # 扣款
        _account_balance["cash"] -= total_cost
        
        # 更新持仓
        update_position(order.stock_code, stock_name, "buy", filled_price, filled_quantity)
        
    else:
        # 卖出：检查持仓是否足够
        if order.stock_code not in _positions:
            return error_response("持仓不足")
        
        pos = _positions[order.stock_code]
        if pos["quantity"] < filled_quantity:
            return error_response("持仓不足")
        
        # 收款
        _account_balance["cash"] += (trade_amount - commission)
        
        # 更新持仓
        update_position(order.stock_code, stock_name, "sell", filled_price, filled_quantity)
    
    # 更新账户余额
    update_account_balance()
    
    # 创建订单记录
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order_record = {
        "order_id": str(uuid.uuid4())[:8].upper(),
        "stock_code": order.stock_code,
        "stock_name": stock_name,
        "direction": order.direction,
        "price": order.price,
        "quantity": order.quantity,
        "order_type": order.order_type,
        "status": "filled",
        "filled_price": filled_price,
        "filled_quantity": order.quantity,
        "commission": commission,
        "created_at": now,
        "updated_at": now
    }
    
    # 添加到交易历史
    _trade_history.append(order_record)
    
    logger.info(f"下单成功: {order_record['order_id']}")
    return success_response(order_record)


@router.get("/positions")
def get_positions():
    """
    获取持仓
    
    返回当前所有持仓
    
    Returns:
        dict: 统一响应格式，包含持仓列表
    """
    logger.info("获取持仓")
    
    # 更新所有持仓的当前价格
    for pos in _positions.values():
        pos["current_price"] = get_mock_price(pos["stock_code"])
        pos["market_value"] = pos["quantity"] * pos["current_price"]
        if pos["quantity"] > 0 and pos["avg_cost"] > 0:
            pos["profit_loss"] = (pos["current_price"] - pos["avg_cost"]) * pos["quantity"]
            pos["profit_loss_pct"] = (pos["current_price"] - pos["avg_cost"]) / pos["avg_cost"] * 100
    
    # 更新账户余额
    update_account_balance()
    
    positions_list = list(_positions.values())
    return success_response(positions_list)


@router.get("/history")
def get_history(
    stock_code: Optional[str] = Query(None, description="股票代码筛选"),
    direction: Optional[str] = Query(None, regex="^(buy|sell)$", description="交易方向筛选"),
    limit: int = Query(50, ge=1, le=200, description="返回条数")
):
    """
    获取交易历史
    
    返回历史交易记录
    
    Args:
        stock_code: 股票代码筛选（可选）
        direction: 交易方向筛选（可选）
        limit: 返回条数
        
    Returns:
        dict: 统一响应格式，包含交易历史列表
    """
    logger.info(f"获取交易历史: stock_code={stock_code}, direction={direction}, limit={limit}")
    
    # 筛选
    history = _trade_history.copy()
    
    if stock_code:
        history = [h for h in history if h["stock_code"] == stock_code]
    
    if direction:
        history = [h for h in history if h["direction"] == direction]
    
    # 按时间倒序
    history.sort(key=lambda x: x["created_at"], reverse=True)
    
    # 限制数量
    history = history[:limit]
    
    return success_response(history)


@router.get("/balance")
def get_balance():
    """
    获取账户余额
    
    返回当前账户资金状况
    
    Returns:
        dict: 统一响应格式，包含账户余额信息
    """
    logger.info("获取账户余额")
    
    # 更新所有持仓的当前价格
    for pos in _positions.values():
        pos["current_price"] = get_mock_price(pos["stock_code"])
        pos["market_value"] = pos["quantity"] * pos["current_price"]
        if pos["quantity"] > 0 and pos["avg_cost"] > 0:
            pos["profit_loss"] = (pos["current_price"] - pos["avg_cost"]) * pos["quantity"]
            pos["profit_loss_pct"] = (pos["current_price"] - pos["avg_cost"]) / pos["avg_cost"] * 100
    
    # 更新账户余额
    update_account_balance()
    
    balance = {
        "cash": round(_account_balance["cash"], 2),
        "frozen": round(_account_balance["frozen"], 2),
        "total_assets": round(_account_balance["total_assets"], 2),
        "market_value": round(_account_balance["market_value"], 2)
    }
    
    return success_response(balance)


@router.post("/reset")
def reset_account():
    """
    重置账户
    
    重置账户余额和持仓（用于测试）
    
    Returns:
        dict: 统一响应格式
    """
    logger.info("重置账户")
    
    global _account_balance, _positions, _trade_history
    
    _account_balance = {
        "cash": 1000000.0,
        "frozen": 0.0,
        "total_assets": 1000000.0,
        "market_value": 0.0,
    }
    _positions = {}
    _trade_history = []
    
    return success_response({"message": "账户已重置"})
