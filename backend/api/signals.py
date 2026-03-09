# 交易信号 API
"""
股票交易信号接口
- 技术信号: MA交叉、MACD、RSI等信号
- 买入卖出信号: 基于多指标的综合信号
- 支撑阻力位: 关键价格位
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from services.stock_service import StockService
from services.technical_indicators import TechnicalIndicators
import pandas as pd
import numpy as np

router = APIRouter(prefix="/api/stock/{code}/signals", tags=["交易信号"])


def _get_kline_data(code: str, start_date: Optional[str] = None, 
                    end_date: Optional[str] = None) -> List[Dict]:
    """获取K线数据并验证"""
    result = StockService.get_history_kline(code, "daily", start_date, end_date)
    
    if isinstance(result, dict):
        if result.get("code") != 0:
            raise HTTPException(status_code=400, detail=result.get("message", "获取数据失败"))
        data = result.get("data", [])
    else:
        data = result
    
    if not data:
        raise HTTPException(status_code=404, detail="没有数据")
    
    # 按日期排序
    df = pd.DataFrame(data)
    df = df.sort_values('date')
    return df.to_dict('records')


def _detect_ma_cross(df: pd.DataFrame) -> List[Dict]:
    """检测MA均线交叉信号"""
    signals = []
    
    # 计算MA5, MA10, MA20, MA60
    for period in [5, 10, 20, 60]:
        df[f'ma{period}'] = df['close'].rolling(window=period).mean()
    
    # 获取最近几行数据进行比对
    if len(df) < 2:
        return signals
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 金叉/死叉信号检测
    # MA5 上穿 MA10 -> 金叉 (买入信号)
    ma5_now = latest.get('ma5')
    ma10_now = latest.get('ma10')
    ma5_prev = prev.get('ma5')
    ma10_prev = prev.get('ma10')
    
    if all(pd.notna(v) for v in [ma5_now, ma10_now, ma5_prev, ma10_prev]):
        if ma5_prev <= ma10_prev and ma5_now > ma10_now:
            signals.append({
                "type": "golden_cross",
                "description": "MA5上穿MA10形成金叉",
                "signal": "buy",
                "strength": "strong"
            })
        elif ma5_prev >= ma10_prev and ma5_now < ma10_now:
            signals.append({
                "type": "death_cross",
                "description": "MA5下穿MA10形成死叉",
                "signal": "sell",
                "strength": "strong"
            })
    
    # MA10 上穿/下穿 MA20
    ma20_now = latest.get('ma20')
    ma20_prev = prev.get('ma20')
    
    if all(pd.notna(v) for v in [ma10_now, ma20_now, ma10_prev, ma20_prev]):
        if ma10_prev <= ma20_prev and ma10_now > ma20_now:
            signals.append({
                "type": "ma10_ma20_cross",
                "description": "MA10上穿MA20",
                "signal": "buy",
                "strength": "medium"
            })
        elif ma10_prev >= ma20_prev and ma10_now < ma20_now:
            signals.append({
                "type": "ma10_ma20_cross",
                "description": "MA10下穿MA20",
                "signal": "sell",
                "strength": "medium"
            })
    
    # MA20 上穿/下穿 MA60
    ma60_now = latest.get('ma60')
    ma60_prev = prev.get('ma60')
    
    if all(pd.notna(v) for v in [ma20_now, ma60_now, ma20_prev, ma60_prev]):
        if ma20_prev <= ma60_prev and ma20_now > ma60_now:
            signals.append({
                "type": "ma20_ma60_cross",
                "description": "MA20上穿MA60",
                "signal": "buy",
                "strength": "strong"
            })
        elif ma20_prev >= ma60_prev and ma20_now < ma60_now:
            signals.append({
                "type": "ma20_ma60_cross",
                "description": "MA20下穿MA60",
                "signal": "sell",
                "strength": "strong"
            })
    
    return signals


def _detect_macd_signal(df: pd.DataFrame) -> List[Dict]:
    """检测MACD信号"""
    signals = []
    
    # 计算MACD
    fast, slow, signal = 12, 26, 9
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    df['dif'] = ema_fast - ema_slow
    df['dea'] = df['dif'].ewm(span=signal, adjust=False).mean()
    df['macd'] = (df['dif'] - df['dea']) * 2
    
    if len(df) < 2:
        return signals
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    dif = latest.get('dif')
    dea = latest.get('dea')
    macd = latest.get('macd')
    dif_prev = prev.get('dif')
    dea_prev = prev.get('dea')
    
    # MACD金叉: DIF从下往上穿过DEA
    if all(pd.notna(v) for v in [dif, dea, dif_prev, dea_prev]):
        if dif_prev <= dea_prev and dif > dea:
            signals.append({
                "type": "macd_golden_cross",
                "description": "MACD金叉 (DIF上穿DEA)",
                "signal": "buy",
                "strength": "strong",
                "values": {
                    "dif": round(dif, 4),
                    "dea": round(dea, 4),
                    "macd": round(macd, 4)
                }
            })
        elif dif_prev >= dea_prev and dif < dea:
            signals.append({
                "type": "macd_death_cross",
                "description": "MACD死叉 (DIF下穿DEA)",
                "signal": "sell",
                "strength": "strong",
                "values": {
                    "dif": round(dif, 4),
                    "dea": round(dea, 4),
                    "macd": round(macd, 4)
                }
            })
    
    # MACD柱状图翻红/翻绿
    macd_prev = prev.get('macd')
    if pd.notna(macd) and pd.notna(macd_prev):
        if macd_prev < 0 and macd > 0:
            signals.append({
                "type": "macd_histogram_turn_positive",
                "description": "MACD柱状图翻红 (由负转正)",
                "signal": "buy",
                "strength": "medium"
            })
        elif macd_prev > 0 and macd < 0:
            signals.append({
                "type": "macd_histogram_turn_negative",
                "description": "MACD柱状图翻绿 (由正转负)",
                "signal": "sell",
                "strength": "medium"
            })
    
    return signals


def _detect_rsi_signal(df: pd.DataFrame) -> List[Dict]:
    """检测RSI信号"""
    signals = []
    
    # 计算RSI(6), RSI(12), RSI(24)
    for period in [6, 12, 24]:
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / avg_loss
        df[f'rsi{period}'] = 100 - (100 / (1 + rs))
    
    if len(df) < 1:
        return signals
    
    latest = df.iloc[-1]
    
    for period in [6, 12, 24]:
        rsi = latest.get(f'rsi{period}')
        if pd.notna(rsi):
            if rsi > 80:
                signals.append({
                    "type": f"rsi{period}_overbought",
                    "description": f"RSI({period})超买区域 ({rsi:.2f})",
                    "signal": "sell",
                    "strength": "medium",
                    "value": round(rsi, 2)
                })
            elif rsi < 20:
                signals.append({
                    "type": f"rsi{period}_oversold",
                    "description": f"RSI({period})超卖区域 ({rsi:.2f})",
                    "signal": "buy",
                    "strength": "medium",
                    "value": round(rsi, 2)
                })
    
    return signals


def _calculate_support_resistance(df: pd.DataFrame) -> Dict[str, Any]:
    """计算支撑位和阻力位"""
    if len(df) < 5:
        return {"support": [], "resistance": []}
    
    # 取最近60个交易日的数据
    recent_df = df.tail(60) if len(df) > 60 else df
    
    # 方法1: 基于近期高低点
    highs = recent_df['high'].values
    lows = recent_df['low'].values
    
    # 阻力位: 近期最高点的几个价位
    high_prices = sorted(highs, reverse=True)[:3]
    
    # 支撑位: 近期最低点的几个价位  
    low_prices = sorted(lows)[:3]
    
    # 当前价格
    current_price = df.iloc[-1]['close']
    
    # 方法2: 基于均线支撑阻力
    ma20 = df['close'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else None
    ma60 = df['close'].rolling(window=60).mean().iloc[-1] if len(df) >= 60 else None
    
    # 构建支撑位列表
    support_levels = []
    for price in low_prices:
        if price < current_price:
            support_levels.append(round(price, 2))
    
    if pd.notna(ma20) and ma20 < current_price:
        support_levels.append(round(ma20, 2))
    if pd.notna(ma60) and ma60 < current_price:
        support_levels.append(round(ma60, 2))
    
    # 构建阻力位列表
    resistance_levels = []
    for price in high_prices:
        if price > current_price:
            resistance_levels.append(round(price, 2))
    
    if pd.notna(ma20) and ma20 > current_price:
        resistance_levels.append(round(ma20, 2))
    if pd.notna(ma60) and ma60 > current_price:
        resistance_levels.append(round(ma60, 2))
    
    # 去重并排序
    support_levels = sorted(list(set(support_levels)), reverse=True)[:5]
    resistance_levels = sorted(list(set(resistance_levels)))[:5]
    
    return {
        "current_price": round(current_price, 2),
        "support": support_levels,
        "resistance": resistance_levels,
        "ma20": round(ma20, 2) if pd.notna(ma20) else None,
        "ma60": round(ma60, 2) if pd.notna(ma60) else None
    }


def _generate_buy_sell_signals(df: pd.DataFrame) -> Dict[str, Any]:
    """生成综合买入卖出信号"""
    
    # 收集所有信号
    all_signals = []
    all_signals.extend(_detect_ma_cross(df))
    all_signals.extend(_detect_macd_signal(df))
    all_signals.extend(_detect_rsi_signal(df))
    
    # 统计买入/卖出信号数量
    buy_count = sum(1 for s in all_signals if s.get('signal') == 'buy')
    sell_count = sum(1 for s in all_signals if s.get('signal') == 'sell')
    
    # 计算强度
    buy_strength = sum(
        3 if s.get('strength') == 'strong' else 2 if s.get('strength') == 'medium' else 1
        for s in all_signals if s.get('signal') == 'buy'
    )
    sell_strength = sum(
        3 if s.get('strength') == 'strong' else 2 if s.get('strength') == 'medium' else 1
        for s in all_signals if s.get('signal') == 'sell'
    )
    
    # 综合判断
    if buy_count > sell_count and buy_strength > sell_strength:
        overall = "strong_buy" if buy_strength >= sell_strength * 2 else "buy"
    elif sell_count > buy_count and sell_strength > buy_strength:
        overall = "strong_sell" if sell_strength >= buy_strength * 2 else "sell"
    elif buy_count > 0 and sell_count == 0:
        overall = "buy"
    elif sell_count > 0 and buy_count == 0:
        overall = "sell"
    else:
        overall = "hold"
    
    # 当前价格
    current_price = df.iloc[-1]['close']
    
    return {
        "overall_signal": overall,
        "buy_signals_count": buy_count,
        "sell_signals_count": sell_count,
        "buy_strength": buy_strength,
        "sell_strength": sell_strength,
        "current_price": round(current_price, 2),
        "latest_date": df.iloc[-1]['date'],
        "signals": all_signals
    }


@router.get("/technical")
def get_technical_signals(
    code: str,
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD")
):
    """
    获取技术信号
    
    返回MA交叉、MACD、RSI等技术信号
    
    Args:
        code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        技术信号数据
    """
    # 获取K线数据
    data = _get_kline_data(code, start_date, end_date)
    df = pd.DataFrame(data)
    
    # 获取各类型信号
    ma_signals = _detect_ma_cross(df)
    macd_signals = _detect_macd_signal(df)
    rsi_signals = _detect_rsi_signal(df)
    
    # 获取最新指标值
    latest = df.iloc[-1]
    
    return {
        "code": 0,
        "data": {
            "stock_code": code,
            "latest_date": latest['date'],
            "close": round(latest['close'], 2),
            "ma_signals": ma_signals,
            "macd_signals": macd_signals,
            "rsi_signals": rsi_signals,
            "total_signals": len(ma_signals) + len(macd_signals) + len(rsi_signals)
        }
    }


@router.get("/buy-sell")
def get_buy_sell_signals(
    code: str,
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD")
):
    """
    获取买入卖出信号
    
    基于多指标综合判断买入/卖出信号
    
    Args:
        code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        买入卖出信号数据
    """
    # 获取K线数据
    data = _get_kline_data(code, start_date, end_date)
    df = pd.DataFrame(data)
    
    # 生成综合信号
    result = _generate_buy_sell_signals(df)
    
    return {
        "code": 0,
        "data": {
            "stock_code": code,
            **result
        }
    }


@router.get("/support-resistance")
def get_support_resistance(
    code: str,
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD")
):
    """
    获取支撑阻力位
    
    返回关键支撑位和阻力位
    
    Args:
        code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        支撑阻力位数据
    """
    # 获取K线数据
    data = _get_kline_data(code, start_date, end_date)
    df = pd.DataFrame(data)
    
    # 计算支撑阻力位
    sr_levels = _calculate_support_resistance(df)
    
    return {
        "code": 0,
        "data": {
            "stock_code": code,
            **sr_levels
        }
    }
