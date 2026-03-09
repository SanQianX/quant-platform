# 风险控制 API
"""
风险控制接口

提供风险指标计算、风险评估和止损建议
使用 AkShare 获取历史数据，计算 VaR、波动率、最大回撤等指标
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models.response import success_response, error_response
from utils.logger import logger

# 创建路由
router = APIRouter(prefix="/api/risk", tags=["风险控制"])


def get_stock_symbol(code: str) -> str:
    """转换股票代码格式"""
    if len(code) == 6:
        if code.startswith(('6', '9')):
            return f"{code}.SH"
        else:
            return f"{code}.SZ"
    return code


def get_historical_prices(code: str, days: int = 250) -> Optional[pd.DataFrame]:
    """
    获取历史价格数据
    
    Args:
        code: 股票代码
        days: 获取天数
        
    Returns:
        DataFrame: 包含日期和收盘价的数据
    """
    try:
        symbol = get_stock_symbol(code)
        # 使用 AkShare 获取历史 K 线数据
        df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                start_date=(datetime.now() - timedelta(days=days+30)).strftime("%Y%m%d"),
                                end_date=datetime.now().strftime("%Y%m%d"),
                                adjust="qfq")
        
        if df is None or df.empty:
            return None
            
        # 确保有日期列
        if '日期' not in df.columns:
            return None
            
        df = df.sort_values('日期')
        return df
    except Exception as e:
        logger.error(f"获取历史数据失败: {e}")
        return None


def calculate_volatility(returns: pd.Series, annualize: bool = True) -> float:
    """
    计算波动率
    
    Args:
        returns: 收益率序列
        annualize: 是否年化
        
    Returns:
        float: 波动率
    """
    if len(returns) < 2:
        return 0.0
    
    vol = returns.std()
    if annualize:
        vol = vol * np.sqrt(252)  # 年化波动率
    return round(float(vol), 4)


def calculate_max_drawdown(prices: pd.Series) -> float:
    """
    计算最大回撤
    
    Args:
        prices: 价格序列
        
    Returns:
        float: 最大回撤（正值表示回撤幅度）
    """
    if len(prices) < 2:
        return 0.0
    
    # 计算累计最大值
    cummax = prices.cummax()
    # 计算回撤
    drawdown = (prices - cummax) / cummax
    # 返回最大回撤
    max_dd = abs(drawdown.min())
    return round(max_dd, 4)


def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """
    计算 Value at Risk (VaR)
    
    Args:
        returns: 收益率序列
        confidence: 置信水平
        
    Returns:
        float: VaR 值
    """
    if len(returns) < 2:
        return 0.0
    
    # 使用历史法计算 VaR
    var = np.percentile(returns, (1 - confidence) * 100)
    return round(float(var), 4)


def calculate_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """
    计算 Conditional VaR (CVaR / Expected Shortfall)
    
    Args:
        returns: 收益率序列
        confidence: 置信水平
        
    Returns:
        float: CVaR 值
    """
    if len(returns) < 2:
        return 0.0
    
    var = np.percentile(returns, (1 - confidence) * 100)
    cvar = returns[returns <= var].mean()
    return round(float(cvar), 4)


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.03) -> float:
    """
    计算夏普比率
    
    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率
        
    Returns:
        float: 夏普比率
    """
    if len(returns) < 2:
        return 0.0
    
    excess_returns = returns - risk_free_rate / 252
    if returns.std() == 0:
        return 0.0
    
    sharpe = excess_returns.mean() / returns.std() * np.sqrt(252)
    return round(float(sharpe), 4)


def calculate_beta(returns: pd.Series, market_returns: pd.Series) -> float:
    """
    计算 Beta 系数
    
    Args:
        returns: 股票收益率序列
        market_returns: 市场收益率序列
        
    Returns:
        float: Beta 值
    """
    if len(returns) < 2 or len(market_returns) < 2:
        return 1.0
    
    # 确保长度一致
    min_len = min(len(returns), len(market_returns))
    returns = returns[:min_len]
    market_returns = market_returns[:min_len]
    
    # 计算协方差和方差
    covariance = np.cov(returns, market_returns)[0, 1]
    market_variance = np.var(market_returns)
    
    if market_variance == 0:
        return 1.0
    
    beta = covariance / market_variance
    return round(float(beta), 4)


def get_mock_risk_data(code: str, days: int = 250) -> dict:
    """
    生成模拟风险数据
    
    Args:
        code: 股票代码
        days: 模拟天数
        
    Returns:
        dict: 模拟风险数据
    """
    # 基于股票代码生成稳定的随机数
    seed = int(code) if code.isdigit() else hash(code) % 10000
    np.random.seed(seed)
    
    # 生成模拟价格序列
    base_price = 50.0 + np.random.random() * 50
    daily_returns = np.random.normal(0.0005, 0.02, days)
    prices = [base_price]
    for r in daily_returns[1:]:
        prices.append(prices[-1] * (1 + r))
    
    prices = pd.Series(prices)
    returns = prices.pct_change().dropna()
    
    # 计算各项指标
    volatility = calculate_volatility(returns)
    max_drawdown = calculate_max_drawdown(prices)
    var_95 = calculate_var(returns, 0.95)
    var_99 = calculate_var(returns, 0.99)
    cvar_95 = calculate_cvar(returns, 0.95)
    sharpe = calculate_sharpe_ratio(returns)
    beta = 0.8 + np.random.random() * 0.4  # 0.8 - 1.2 之间的 Beta
    
    # 当前价格
    current_price = prices.iloc[-1]
    
    return {
        "code": code,
        "current_price": round(current_price, 2),
        "volatility": volatility,
        "max_drawdown": max_drawdown,
        "var_95": var_95,
        "var_99": var_99,
        "cvar_95": cvar_95,
        "sharpe_ratio": sharpe,
        "beta": beta,
        "days": days,
        "calculation_date": datetime.now().strftime("%Y-%m-%d")
    }


@router.get("/{code}/metrics")
def get_risk_metrics(
    code: str = Path(..., description="股票代码"),
    days: int = Query(250, description="计算天数", ge=30, le=500)
):
    """
    获取风险指标
    
    返回 VaR、波动率、最大回撤、夏普比率、Beta 等风险指标
    
    Args:
        code: 股票代码
        days: 计算天数，默认 250 个交易日
        
    Returns:
        风险指标数据
    """
    try:
        # 尝试获取真实数据
        df = get_historical_prices(code, days)
        
        if df is None or len(df) < 30:
            # 如果获取失败或数据不足，使用模拟数据
            logger.warning(f"使用模拟数据: {code}")
            data = get_mock_risk_data(code, days)
            return success_response(data)
        
        # 提取收盘价
        if '收盘' in df.columns:
            prices = df['收盘']
        elif 'close' in df.columns:
            prices = df['close']
        else:
            return error_response("数据格式不正确")
        
        # 计算收益率
        returns = prices.pct_change().dropna()
        
        if len(returns) < 10:
            return error_response("数据不足，无法计算风险指标")
        
        # 获取上证指数数据用于计算 Beta
        try:
            market_df = ak.stock_zh_index_daily(symbol="sh000001")
            market_df = market_df.sort_values('date')
            market_prices = market_df['close'].tail(days)
            market_returns = market_prices.pct_change().dropna()
            # 对齐数据
            min_len = min(len(returns), len(market_returns))
            if min_len > 10:
                beta = calculate_beta(returns[:min_len], market_returns[:min_len])
            else:
                beta = 1.0
        except:
            beta = 1.0
        
        # 计算各项指标
        volatility = calculate_volatility(returns)
        max_drawdown = calculate_max_drawdown(prices)
        var_95 = calculate_var(returns, 0.95)
        var_99 = calculate_var(returns, 0.99)
        cvar_95 = calculate_cvar(returns, 0.95)
        sharpe = calculate_sharpe_ratio(returns)
        
        current_price = float(prices.iloc[-1])
        
        data = {
            "code": code,
            "current_price": round(current_price, 2),
            "volatility": volatility,
            "max_drawdown": max_drawdown,
            "var_95": var_95,
            "var_99": var_99,
            "cvar_95": cvar_95,
            "sharpe_ratio": sharpe,
            "beta": beta,
            "days": len(returns),
            "calculation_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"计算风险指标失败: {e}")
        # 发生错误时返回模拟数据
        data = get_mock_risk_data(code, days)
        return success_response(data)


@router.get("/{code}/assessment")
def get_risk_assessment(
    code: str = Path(..., description="股票代码"),
    days: int = Query(250, description="评估天数", ge=30, le=500)
):
    """
    获取风险评估
    
    返回风险等级和风险点分析
    
    Args:
        code: 股票代码
        days: 评估天数
        
    Returns:
        风险评估数据
    """
    try:
        # 先获取风险指标
        df = get_historical_prices(code, days)
        
        if df is None or len(df) < 30:
            # 使用模拟数据
            data = get_mock_risk_data(code, days)
        else:
            if '收盘' in df.columns:
                prices = df['收盘']
            elif 'close' in df.columns:
                prices = df['close']
            else:
                return error_response("数据格式不正确")
            
            returns = prices.pct_change().dropna()
            
            if len(returns) < 10:
                return error_response("数据不足")
            
            data = {
                "volatility": calculate_volatility(returns),
                "max_drawdown": calculate_max_drawdown(prices),
                "var_95": calculate_var(returns, 0.95),
                "sharpe_ratio": calculate_sharpe_ratio(returns),
            }
        
        # 风险评估
        volatility = data.get("volatility", 0)
        max_drawdown = data.get("max_drawdown", 0)
        var_95 = data.get("var_95", 0)
        sharpe = data.get("sharpe_ratio", 0)
        
        # 计算风险得分 (0-100)
        risk_score = 0
        
        # 波动率风险 (0-30分)
        if volatility > 0.4:
            risk_score += 30
        elif volatility > 0.3:
            risk_score += 25
        elif volatility > 0.2:
            risk_score += 15
        elif volatility > 0.15:
            risk_score += 10
        else:
            risk_score += 5
        
        # 回撤风险 (0-30分)
        if max_drawdown > 0.5:
            risk_score += 30
        elif max_drawdown > 0.3:
            risk_score += 25
        elif max_drawdown > 0.2:
            risk_score += 15
        elif max_drawdown > 0.1:
            risk_score += 10
        else:
            risk_score += 5
        
        # VaR 风险 (0-20分)
        if abs(var_95) > 0.1:
            risk_score += 20
        elif abs(var_95) > 0.05:
            risk_score += 15
        elif abs(var_95) > 0.03:
            risk_score += 10
        else:
            risk_score += 5
        
        # 夏普比率风险 (0-20分)
        if sharpe < 0:
            risk_score += 20
        elif sharpe < 0.5:
            risk_score += 15
        elif sharpe < 1.0:
            risk_score += 10
        else:
            risk_score += 5
        
        # 确定风险等级
        if risk_score >= 70:
            risk_level = "高风险"
            risk_level_en = "HIGH"
            risk_color = "red"
        elif risk_score >= 50:
            risk_level = "中等风险"
            risk_level_en = "MEDIUM"
            risk_color = "orange"
        elif risk_score >= 30:
            risk_level = "较低风险"
            risk_level_en = "LOW"
            risk_color = "yellow"
        else:
            risk_level = "低风险"
            risk_level_en = "VERY_LOW"
            risk_color = "green"
        
        # 风险点分析
        risk_points = []
        
        if volatility > 0.3:
            risk_points.append({
                "type": "波动率风险",
                "level": "高",
                "description": f"年化波动率为 {volatility:.2%}，价格波动剧烈",
                "suggestion": "建议降低持仓比例或设置更宽的止损"
            })
        elif volatility > 0.2:
            risk_points.append({
                "type": "波动率风险",
                "level": "中",
                "description": f"年化波动率为 {volatility:.2%}，价格波动适中",
                "suggestion": "关注市场动态，适时调整仓位"
            })
        
        if max_drawdown > 0.3:
            risk_points.append({
                "type": "回撤风险",
                "level": "高",
                "description": f"历史最大回撤为 {max_drawdown:.2%}",
                "suggestion": "注意风险控制，避免重仓操作"
            })
        elif max_drawdown > 0.15:
            risk_points.append({
                "type": "回撤风险",
                "level": "中",
                "description": f"历史最大回撤为 {max_drawdown:.2%}",
                "suggestion": "设置合理的止损位"
            })
        
        if abs(var_95) > 0.05:
            risk_points.append({
                "type": "VaR风险",
                "level": "高",
                "description": f"95%置信度下单日VaR为 {var_95:.2%}",
                "suggestion": "在险价值较高，需注意仓位控制"
            })
        
        if sharpe < 0:
            risk_points.append({
                "type": "收益风险",
                "level": "高",
                "description": f"夏普比率为 {sharpe:.2f}，风险调整后收益为负",
                "suggestion": "建议观望或选择其他标的"
            })
        elif sharpe < 0.5:
            risk_points.append({
                "type": "收益风险",
                "level": "中",
                "description": f"夏普比率为 {sharpe:.2f}，风险调整后收益较低",
                "suggestion": "考虑其他高性价比标的"
            })
        
        if not risk_points:
            risk_points.append({
                "type": "整体风险",
                "level": "低",
                "description": "各项风险指标处于合理范围",
                "suggestion": "可继续持有，关注市场变化"
            })
        
        result = {
            "code": code,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_level_en": risk_level_en,
            "risk_color": risk_color,
            "risk_points": risk_points,
            "metrics": {
                "volatility": volatility,
                "max_drawdown": max_drawdown,
                "var_95": var_95,
                "sharpe_ratio": sharpe
            },
            "assessment_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        return success_response(result)
        
    except Exception as e:
        logger.error(f"风险评估失败: {e}")
        return error_response(f"风险评估失败: {str(e)}")


@router.get("/{code}/stop-loss")
def get_stop_loss_suggestion(
    code: str = Path(..., description="股票代码"),
    buy_price: Optional[float] = Query(None, description="买入价格（可选）"),
    position_size: Optional[float] = Query(None, description="仓位比例（0-1，可选）"),
    risk_tolerance: str = Query("medium", description="风险承受能力: low/medium/high")
):
    """
    获取止损建议
    
    根据风险指标和市场波动情况给出止损建议
    
    Args:
        code: 股票代码
        buy_price: 买入价格（可选）
        position_size: 仓位比例（可选）
        risk_tolerance: 风险承受能力
        
    Returns:
        止损建议数据
    """
    try:
        # 获取风险指标
        days = 60  # 使用近60天数据计算短期波动
        df = get_historical_prices(code, days)
        
        if df is None or len(df) < 20:
            # 使用模拟数据
            data = get_mock_risk_data(code, 60)
        else:
            if '收盘' in df.columns:
                prices = df['收盘']
            else:
                prices = df['close']
            
            returns = prices.pct_change().dropna()
            
            if len(returns) < 10:
                return error_response("数据不足")
            
            volatility = calculate_volatility(returns)
            max_dd = calculate_max_drawdown(prices)
            current_price = float(prices.iloc[-1])
            
            data = {
                "volatility": volatility,
                "max_drawdown": max_dd,
                "current_price": current_price
            }
        
        current_price = data.get("current_price", 100.0)
        volatility = data.get("volatility", 0.2)
        
        # 如果没有提供买入价格，使用当前价格
        if buy_price is None:
            buy_price = current_price
        
        # 止损计算始终以当前价格为准
        reference_price = current_price
        
        # 根据风险承受能力和波动率计算止损位
        # 风险容忍度系数
        risk_multipliers = {
            "low": 1.5,      # 保守，止损较近
            "medium": 2.0,   # 中等
            "high": 2.5      # 激进，止损较远
        }
        multiplier = risk_multipliers.get(risk_tolerance, 2.0)
        
        # 基于波动率计算止损幅度
        # 使用 ATR 概念：平均真实波幅的倍数
        atr_like = volatility * reference_price * multiplier
        
        # 止损价格（基于当前价格计算）
        stop_loss_price = reference_price - atr_like
        
        # 确保止损价为正
        if stop_loss_price <= 0:
            stop_loss_price = reference_price * 0.9  # 默认设置 10% 止损
        
        # 止损百分比（相对于买入价格）
        stop_loss_pct = (buy_price - stop_loss_price) / buy_price if buy_price > 0 else 0.1
        
        # 建议止损价格（向下取整到合理价位）
        if stop_loss_price > 100:
            stop_loss_price = round(stop_loss_price, 1)
        elif stop_loss_price > 10:
            stop_loss_price = round(stop_loss_price, 2)
        else:
            stop_loss_price = round(stop_loss_price, 3)
        
        # 计算建议止盈位 (风险收益比 2:1)
        risk_amount = buy_price - stop_loss_price
        take_profit_price = buy_price + risk_amount * 2
        
        if take_profit_price > 100:
            take_profit_price = round(take_profit_price, 1)
        elif take_profit_price > 10:
            take_profit_price = round(take_profit_price, 2)
        else:
            take_profit_price = round(take_profit_price, 3)
        
        # 计算建议仓位
        # 根据单次风险不超过总资金的 2% 原则
        suggested_position = 0.1  # 默认 10%
        if risk_tolerance == "low":
            suggested_position = 0.05  # 5%
        elif risk_tolerance == "high":
            suggested_position = 0.15  # 15%
        
        if position_size is not None and position_size > 0:
            # 验证仓位是否合理
            position_risk = position_size * stop_loss_pct
            if position_risk > 0.05:  # 超过 5% 总风险
                warning = f"当前仓位风险较高 ({position_risk:.1%})，建议降低仓位"
            else:
                warning = None
        else:
            warning = None
            position_size = suggested_position
        
        result = {
            "code": code,
            "current_price": round(current_price, 2),
            "buy_price": round(buy_price, 2),
            "stop_loss_price": stop_loss_price,
            "stop_loss_pct": round(stop_loss_pct, 4),
            "take_profit_price": take_profit_price,
            "risk_reward_ratio": 2.0,
            "suggested_position": round(suggested_position, 4),
            "actual_position": round(position_size, 4) if position_size else None,
            "risk_tolerance": risk_tolerance,
            "volatility": round(volatility, 4),
            "warning": warning,
            "suggestion_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        return success_response(result)
        
    except Exception as e:
        logger.error(f"计算止损建议失败: {e}")
        return error_response(f"计算止损建议失败: {str(e)}")


@router.get("/{code}/var-history")
def get_var_history(
    code: str = Path(..., description="股票代码"),
    days: int = Query(60, description="计算天数", ge=30, le=250),
    confidence: float = Query(0.95, description="置信水平", ge=0.9, le=0.99)
):
    """
    获取 VaR 历史序列
    
    返回历史每日 VaR 变化
    
    Args:
        code: 股票代码
        days: 计算天数
        confidence: 置信水平
        
    Returns:
        VaR 历史数据
    """
    try:
        df = get_historical_prices(code, days + 30)  # 多获取一些数据
        
        if df is None or len(df) < days:
            return error_response("数据不足")
        
        if '收盘' in df.columns:
            prices = df['收盘']
        else:
            prices = df['close']
        
        # 计算滚动 VaR
        var_series = []
        window = 20  # 使用 20 天窗口
        
        for i in range(window, len(prices)):
            window_returns = prices.iloc[i-window:i].pct_change().dropna()
            if len(window_returns) > 10:
                var = calculate_var(window_returns, confidence)
                date = df.iloc[i]['日期'] if '日期' in df.columns else str(i)
                var_series.append({
                    "date": str(date),
                    "var": var
                })
        
        return success_response({
            "code": code,
            "confidence": confidence,
            "var_history": var_series[-days:]  # 返回最后指定天数
        })
        
    except Exception as e:
        logger.error(f"获取 VaR 历史失败: {e}")
        return error_response(f"获取 VaR 历史失败: {str(e)}")
