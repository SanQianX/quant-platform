# 高级筛选 API
"""
高级股票筛选功能
- 基本面筛选 (PE, PB, 市值)
- 技术面筛选 (均线多头, MACD金叉)
- 综合筛选 (组合条件)
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import akshare as ak
import pandas as pd
from services.stock_service import StockService
from services.technical_indicators import TechnicalIndicators
from models.response import success_response, error_response
from utils.logger import logger
from utils.cache import cache

router = APIRouter(prefix="/api/filter", tags=["高级筛选"])


def clean_value(val):
    """清理数值中的NaN和Inf"""
    if pd.isna(val) or pd.isinf(val):
        return None
    return val


def get_financial_data(stock_code: str) -> Optional[Dict]:
    """
    获取股票财务数据 (PE, PB, 市值)
    
    Args:
        stock_code: 股票代码
        
    Returns:
        dict: 财务数据 {'pe': float, 'pb': float, 'market_cap': float}
    """
    cache_key = f"financial:{stock_code}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        # 转换代码格式
        if len(stock_code) == 6:
            if stock_code.startswith(('6', '9')):
                symbol = f"{stock_code}.SH"
            else:
                symbol = f"{stock_code}.SZ"
        else:
            symbol = stock_code
        
        # 获取实时行情数据 (包含PE, PB, 市值)
        df = ak.stock_zh_a_spot_em()
        
        if df is None or df.empty:
            return None
        
        # 筛选当前股票
        stock_row = df[df['代码'] == stock_code]
        
        if stock_row.empty:
            return None
        
        row = stock_row.iloc[0]
        
        data = {
            'code': stock_code,
            'name': str(row.get('名称', '')),
            'price': clean_value(row.get('最新价')),
            'change_pct': clean_value(row.get('涨跌幅')),
            'volume': clean_value(row.get('成交量')),
            'amount': clean_value(row.get('成交额')),
            'amplitude': clean_value(row.get('振幅')),
            'high': clean_value(row.get('最高')),
            'low': clean_value(row.get('最低')),
            'open': clean_value(row.get('今开')),
            'close_prev': clean_value(row.get('昨收')),
            'pe': clean_value(row.get('市盈率-动态')),
            'pb': clean_value(row.get('市净率')),
            'market_cap': clean_value(row.get('总市值')),
            'float_cap': clean_value(row.get('流通市值')),
        }
        
        cache.set(cache_key, data, ttl=300)
        return data
        
    except Exception as e:
        logger.error(f"获取财务数据失败 {stock_code}: {e}")
        return None


def get_technical_signals(stock_code: str) -> Optional[Dict]:
    """
    获取股票技术面信号
    
    Args:
        stock_code: 股票代码
        
    Returns:
        dict: 技术信号 {'ma_golden_cross': bool, 'macd_golden_cross': bool, ...}
    """
    cache_key = f"technical:{stock_code}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        # 获取K线数据
        kline_result = StockService.get_kline_data(stock_code)
        
        if isinstance(kline_result, dict):
            if kline_result.get("code") != 0:
                return None
            kline_data = kline_result.get("data", [])
        else:
            kline_data = kline_result
        
        if not kline_data or len(kline_data) < 60:
            return None
        
        # 计算MA
        ma_data = TechnicalIndicators.calculate_ma(kline_data, [5, 10, 20, 60])
        
        # 计算MACD
        macd_data = TechnicalIndicators.calculate_macd(kline_data)
        
        # 获取最新数据
        latest_ma = ma_data[-1] if ma_data else {}
        prev_ma = ma_data[-2] if len(ma_data) > 1 else {}
        
        latest_macd = macd_data[-1] if macd_data else {}
        prev_macd = macd_data[-2] if len(macd_data) > 1 else {}
        
        # 判断均线多头 (MA5 > MA10 > MA20 > MA60)
        ma_golden_cross = (
            latest_ma.get('ma5') and latest_ma.get('ma10') and 
            latest_ma.get('ma20') and latest_ma.get('ma60') and
            latest_ma.get('ma5') > latest_ma.get('ma10') > latest_ma.get('ma20') > latest_ma.get('ma60')
        )
        
        # 判断MA5上穿MA10 (金叉)
        ma5_cross_above_ma10 = (
            prev_ma.get('ma5', 0) <= prev_ma.get('ma10', 0) and
            latest_ma.get('ma5', 0) > latest_ma.get('ma10', 0)
        )
        
        # 判断MACD金叉 (DIF上穿DEA)
        macd_golden_cross = (
            prev_macd.get('dif', 0) <= prev_macd.get('dea', 0) and
            latest_macd.get('dif', 0) > latest_macd.get('dea', 0)
        )
        
        # 判断MACD死叉 (DIF下穿DEA)
        macd_death_cross = (
            prev_macd.get('dif', 0) >= prev_macd.get('dea', 0) and
            latest_macd.get('dif', 0) < latest_macd.get('dea', 0)
        )
        
        # 判断MACD多头 (DIF > DEA > 0)
        macd_bullish = (
            latest_macd.get('dif', 0) > latest_macd.get('dea', 0) > 0
        )
        
        # 判断价格站在均线上
        price_above_ma5 = latest_ma.get('close', 0) > latest_ma.get('ma5', 0) if latest_ma.get('close') and latest_ma.get('ma5') else False
        price_above_ma10 = latest_ma.get('close', 0) > latest_ma.get('ma10', 0) if latest_ma.get('close') and latest_ma.get('ma10') else False
        price_above_ma20 = latest_ma.get('close', 0) > latest_ma.get('ma20', 0) if latest_ma.get('close') and latest_ma.get('ma20') else False
        
        data = {
            'code': stock_code,
            'price': latest_ma.get('close'),
            'ma5': latest_ma.get('ma5'),
            'ma10': latest_ma.get('ma10'),
            'ma20': latest_ma.get('ma20'),
            'ma60': latest_ma.get('ma60'),
            'dif': latest_macd.get('dif'),
            'dea': latest_macd.get('dea'),
            'macd': latest_macd.get('macd'),
            'ma_golden_cross': ma_golden_cross,
            'ma5_cross_above_ma10': ma5_cross_above_ma10,
            'macd_golden_cross': macd_golden_cross,
            'macd_death_cross': macd_death_cross,
            'macd_bullish': macd_bullish,
            'price_above_ma5': price_above_ma5,
            'price_above_ma10': price_above_ma10,
            'price_above_ma20': price_above_ma20,
        }
        
        cache.set(cache_key, data, ttl=300)
        return data
        
    except Exception as e:
        logger.error(f"获取技术信号失败 {stock_code}: {e}")
        return None


# ==================== 基本面筛选 ====================

class FundamentalFilter(BaseModel):
    """基本面筛选条件"""
    min_pe: Optional[float] = None       # 最小PE (市盈率-动态)
    max_pe: Optional[float] = None       # 最大PE
    min_pb: Optional[float] = None       # 最小PB (市净率)
    max_pb: Optional[float] = None       # 最大PB
    min_market_cap: Optional[float] = None    # 最小市值 (亿元)
    max_market_cap: Optional[float] = None   # 最大市值 (亿元)
    min_price: Optional[float] = None    # 最低股价
    max_price: Optional[float] = None    # 最高股价
    min_change_pct: Optional[float] = None   # 最小涨跌幅
    max_change_pct: Optional[float] = None   # 最大涨跌幅


@router.get("/fundamental")
def filter_by_fundamental(
    min_pe: Optional[float] = Query(None, description="最小PE (市盈率-动态)"),
    max_pe: Optional[float] = Query(None, description="最大PE"),
    min_pb: Optional[float] = Query(None, description="最小PB (市净率)"),
    max_pb: Optional[float] = Query(None, description="最大PB"),
    min_market_cap: Optional[float] = Query(None, description="最小市值 (亿元)"),
    max_market_cap: Optional[float] = Query(None, description="最大市值 (亿元)"),
    min_price: Optional[float] = Query(None, description="最低股价"),
    max_price: Optional[float] = Query(None, description="最高股价"),
    min_change_pct: Optional[float] = Query(None, description="最小涨跌幅 (%)"),
    max_change_pct: Optional[float] = Query(None, description="最大涨跌幅 (%)"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(50, description="每页数量"),
    use_cache: bool = Query(True, description="是否使用缓存")
):
    """
    基本面筛选
    
    按PE、PB、市值等财务指标筛选股票
    
    示例:
    /api/filter/fundamental?min_pe=5&max_pe=30&min_market_cap=10&max_market_cap=500
    """
    cache_key = f"filter:fundamental:{min_pe}:{max_pe}:{min_pb}:{max_pb}:{min_market_cap}:{max_market_cap}:{min_price}:{max_price}:{min_change_pct}:{max_change_pct}:{page}:{page_size}"
    
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    try:
        # 获取所有股票
        stocks_result = StockService.get_stock_list()
        
        if isinstance(stocks_result, dict):
            if stocks_result.get("code") != 0:
                return error_response(stocks_result.get("message", "获取股票列表失败"))
            stocks = stocks_result.get("data", [])
        else:
            stocks = stocks_result
        
        if not stocks:
            return error_response("没有股票数据")
        
        # 筛选符合条件的股票
        filtered_stocks = []
        
        for stock in stocks:
            code = stock.get('code')
            if not code:
                continue
            
            # 获取财务数据
            financial_data = get_financial_data(code)
            
            if not financial_data:
                continue
            
            # 应用筛选条件
            if min_price is not None and (financial_data.get('price') or 0) < min_price:
                continue
            if max_price is not None and (financial_data.get('price') or 999999) > max_price:
                continue
            
            if min_pe is not None and (financial_data.get('pe') or 999999) < min_pe:
                continue
            if max_pe is not None and (financial_data.get('pe') or 0) > max_pe:
                continue
            
            if min_pb is not None and (financial_data.get('pb') or 999999) < min_pb:
                continue
            if max_pb is not None and (financial_data.get('pb') or 0) > max_pb:
                continue
            
            # 市值单位转换 (AkShare返回的是元，转为亿元)
            market_cap = financial_data.get('market_cap')
            if market_cap:
                market_cap = market_cap / 1e8  # 转为亿元
            
            if min_market_cap is not None and (market_cap or 0) < min_market_cap:
                continue
            if max_market_cap is not None and (market_cap or 999999999) > max_market_cap:
                continue
            
            if min_change_pct is not None and (financial_data.get('change_pct') or -999) < min_change_pct:
                continue
            if max_change_pct is not None and (financial_data.get('change_pct') or 999) > max_change_pct:
                continue
            
            # 添加到结果
            filtered_stocks.append({
                'code': code,
                'name': financial_data.get('name'),
                'price': financial_data.get('price'),
                'change_pct': financial_data.get('change_pct'),
                'pe': financial_data.get('pe'),
                'pb': financial_data.get('pb'),
                'market_cap': market_cap,
                'volume': financial_data.get('volume'),
            })
        
        # 分页
        total = len(filtered_stocks)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_stocks = filtered_stocks[start:end]
        
        result = {
            "code": 0,
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "results": paginated_stocks
            }
        }
        
        if use_cache:
            cache.set(cache_key, result, ttl=60)
        
        return result
        
    except Exception as e:
        logger.error(f"基本面筛选失败: {e}")
        return error_response(f"基本面筛选失败: {str(e)}")


# ==================== 技术面筛选 ====================

class TechnicalFilter(BaseModel):
    """技术面筛选条件"""
    ma_golden_cross: Optional[bool] = Query(None, description="均线多头排列")
    ma5_cross_above_ma10: Optional[bool] = Query(None, description="MA5上穿MA10 (金叉)")
    macd_golden_cross: Optional[bool] = Query(None, description="MACD金叉")
    macd_death_cross: Optional[bool] = Query(None, description="MACD死叉")
    macd_bullish: Optional[bool] = Query(None, description="MACD多头 (DIF>DEA>0)")
    price_above_ma5: Optional[bool] = Query(None, description="价格站上MA5")
    price_above_ma10: Optional[bool] = Query(None, description="价格站上MA10")
    price_above_ma20: Optional[bool] = Query(None, description="价格站上MA20")


@router.get("/technical")
def filter_by_technical(
    ma_golden_cross: Optional[bool] = Query(None, description="均线多头排列"),
    ma5_cross_above_ma10: Optional[bool] = Query(None, description="MA5上穿MA10 (金叉)"),
    macd_golden_cross: Optional[bool] = Query(None, description="MACD金叉"),
    macd_death_cross: Optional[bool] = Query(None, description="MACD死叉"),
    macd_bullish: Optional[bool] = Query(None, description="MACD多头"),
    price_above_ma5: Optional[bool] = Query(None, description="价格站上MA5"),
    price_above_ma10: Optional[bool] = Query(None, description="价格站上MA10"),
    price_above_ma20: Optional[bool] = Query(None, description="价格站上MA20"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(50, description="每页数量"),
    use_cache: bool = Query(True, description="是否使用缓存")
):
    """
    技术面筛选
    
    按均线多头、MACD金叉等技术指标筛选股票
    
    示例:
    /api/filter/technical?ma_golden_cross=true&macd_golden_cross=true
    """
    cache_key = f"filter:technical:{ma_golden_cross}:{ma5_cross_above_ma10}:{macd_golden_cross}:{macd_death_cross}:{macd_bullish}:{price_above_ma5}:{price_above_ma10}:{price_above_ma20}:{page}:{page_size}"
    
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    try:
        # 获取所有股票
        stocks_result = StockService.get_stock_list()
        
        if isinstance(stocks_result, dict):
            if stocks_result.get("code") != 0:
                return error_response(stocks_result.get("message", "获取股票列表失败"))
            stocks = stocks_result.get("data", [])
        else:
            stocks = stocks_result
        
        if not stocks:
            return error_response("没有股票数据")
        
        # 筛选符合条件的股票
        filtered_stocks = []
        
        for stock in stocks:
            code = stock.get('code')
            if not code:
                continue
            
            # 获取技术信号
            tech_data = get_technical_signals(code)
            
            if not tech_data:
                continue
            
            # 应用筛选条件
            if ma_golden_cross is not None:
                if tech_data.get('ma_golden_cross') != ma_golden_cross:
                    continue
            
            if ma5_cross_above_ma10 is not None:
                if tech_data.get('ma5_cross_above_ma10') != ma5_cross_above_ma10:
                    continue
            
            if macd_golden_cross is not None:
                if tech_data.get('macd_golden_cross') != macd_golden_cross:
                    continue
            
            if macd_death_cross is not None:
                if tech_data.get('macd_death_cross') != macd_death_cross:
                    continue
            
            if macd_bullish is not None:
                if tech_data.get('macd_bullish') != macd_bullish:
                    continue
            
            if price_above_ma5 is not None:
                if tech_data.get('price_above_ma5') != price_above_ma5:
                    continue
            
            if price_above_ma10 is not None:
                if tech_data.get('price_above_ma10') != price_above_ma10:
                    continue
            
            if price_above_ma20 is not None:
                if tech_data.get('price_above_ma20') != price_above_ma20:
                    continue
            
            # 添加到结果
            filtered_stocks.append({
                'code': code,
                'price': tech_data.get('price'),
                'ma5': tech_data.get('ma5'),
                'ma10': tech_data.get('ma10'),
                'ma20': tech_data.get('ma20'),
                'ma60': tech_data.get('ma60'),
                'dif': tech_data.get('dif'),
                'dea': tech_data.get('dea'),
                'macd': tech_data.get('macd'),
                'ma_golden_cross': tech_data.get('ma_golden_cross'),
                'ma5_cross_above_ma10': tech_data.get('ma5_cross_above_ma10'),
                'macd_golden_cross': tech_data.get('macd_golden_cross'),
                'macd_death_cross': tech_data.get('macd_death_cross'),
                'macd_bullish': tech_data.get('macd_bullish'),
                'price_above_ma5': tech_data.get('price_above_ma5'),
                'price_above_ma10': tech_data.get('price_above_ma10'),
                'price_above_ma20': tech_data.get('price_above_ma20'),
            })
        
        # 分页
        total = len(filtered_stocks)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_stocks = filtered_stocks[start:end]
        
        result = {
            "code": 0,
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "results": paginated_stocks
            }
        }
        
        if use_cache:
            cache.set(cache_key, result, ttl=60)
        
        return result
        
    except Exception as e:
        logger.error(f"技术面筛选失败: {e}")
        return error_response(f"技术面筛选失败: {str(e)}")


# ==================== 综合筛选 ====================

class CombineFilterRequest(BaseModel):
    """综合筛选请求"""
    # 基本面条件
    min_pe: Optional[float] = None
    max_pe: Optional[float] = None
    min_pb: Optional[float] = None
    max_pb: Optional[float] = None
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    
    # 技术面条件
    ma_golden_cross: Optional[bool] = None
    ma5_cross_above_ma10: Optional[bool] = None
    macd_golden_cross: Optional[bool] = None
    macd_bullish: Optional[bool] = None
    price_above_ma5: Optional[bool] = None
    
    # 分页
    page: int = 1
    page_size: int = 50


@router.post("/combine")
def filter_combine(
    request: CombineFilterRequest = Body(...)
):
    """
    综合筛选
    
    组合基本面和技术面条件进行筛选
    
    请求示例:
    {
        "min_pe": 5,
        "max_pe": 30,
        "ma_golden_cross": true,
        "macd_golden_cross": true,
        "page": 1,
        "page_size": 50
    }
    """
    try:
        # 获取所有股票
        stocks_result = StockService.get_stock_list()
        
        if isinstance(stocks_result, dict):
            if stocks_result.get("code") != 0:
                return error_response(stocks_result.get("message", "获取股票列表失败"))
            stocks = stocks_result.get("data", [])
        else:
            stocks = stocks_result
        
        if not stocks:
            return error_response("没有股票数据")
        
        # 筛选符合条件的股票
        filtered_stocks = []
        
        for stock in stocks:
            code = stock.get('code')
            if not code:
                continue
            
            # 获取财务数据和技术信号
            financial_data = get_financial_data(code)
            tech_data = get_technical_signals(code)
            
            # 应用基本面条件
            if financial_data:
                if request.min_price is not None and (financial_data.get('price') or 0) < request.min_price:
                    continue
                if request.max_price is not None and (financial_data.get('price') or 999999) > request.max_price:
                    continue
                
                if request.min_pe is not None and (financial_data.get('pe') or 999999) < request.min_pe:
                    continue
                if request.max_pe is not None and (financial_data.get('pe') or 0) > request.max_pe:
                    continue
                
                if request.min_pb is not None and (financial_data.get('pb') or 999999) < request.min_pb:
                    continue
                if request.max_pb is not None and (financial_data.get('pb') or 0) > request.max_pb:
                    continue
                
                market_cap = financial_data.get('market_cap')
                if market_cap:
                    market_cap = market_cap / 1e8
                
                if request.min_market_cap is not None and (market_cap or 0) < request.min_market_cap:
                    continue
                if request.max_market_cap is not None and (market_cap or 999999999) > request.max_market_cap:
                    continue
            
            # 应用技术面条件
            if tech_data:
                if request.ma_golden_cross is not None:
                    if tech_data.get('ma_golden_cross') != request.ma_golden_cross:
                        continue
                
                if request.ma5_cross_above_ma10 is not None:
                    if tech_data.get('ma5_cross_above_ma10') != request.ma5_cross_above_ma10:
                        continue
                
                if request.macd_golden_cross is not None:
                    if tech_data.get('macd_golden_cross') != request.macd_golden_cross:
                        continue
                
                if request.macd_bullish is not None:
                    if tech_data.get('macd_bullish') != request.macd_bullish:
                        continue
                
                if request.price_above_ma5 is not None:
                    if tech_data.get('price_above_ma5') != request.price_above_ma5:
                        continue
            
            # 如果没有财务数据或技术数据，跳过
            if not financial_data and not tech_data:
                continue
            
            # 添加到结果
            result_item = {
                'code': code,
                'name': financial_data.get('name') if financial_data else stock.get('name'),
            }
            
            if financial_data:
                result_item.update({
                    'price': financial_data.get('price'),
                    'change_pct': financial_data.get('change_pct'),
                    'pe': financial_data.get('pe'),
                    'pb': financial_data.get('pb'),
                    'market_cap': financial_data.get('market_cap') / 1e8 if financial_data.get('market_cap') else None,
                })
            
            if tech_data:
                result_item.update({
                    'ma5': tech_data.get('ma5'),
                    'ma10': tech_data.get('ma10'),
                    'ma20': tech_data.get('ma20'),
                    'dif': tech_data.get('dif'),
                    'dea': tech_data.get('dea'),
                    'ma_golden_cross': tech_data.get('ma_golden_cross'),
                    'macd_golden_cross': tech_data.get('macd_golden_cross'),
                    'macd_bullish': tech_data.get('macd_bullish'),
                })
            
            filtered_stocks.append(result_item)
        
        # 分页
        total = len(filtered_stocks)
        start = (request.page - 1) * request.page_size
        end = start + request.page_size
        paginated_stocks = filtered_stocks[start:end]
        
        return {
            "code": 0,
            "data": {
                "total": total,
                "page": request.page,
                "page_size": request.page_size,
                "results": paginated_stocks
            }
        }
        
    except Exception as e:
        logger.error(f"综合筛选失败: {e}")
        return error_response(f"综合筛选失败: {str(e)}")
