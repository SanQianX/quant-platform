# 数据质量监控服务
"""
数据质量检查和监控
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

class DataQualityMonitor:
    """数据质量监控"""
    
    @staticmethod
    def check_data_completeness(stock_code: str, kline_data: List[Dict]) -> Dict[str, Any]:
        """
        检查数据完整性
        
        Args:
            stock_code: 股票代码
            kline_data: K线数据
            
        Returns:
            完整性报告
        """
        if not kline_data:
            return {
                "stock_code": stock_code,
                "status": "no_data",
                "total_records": 0,
                "completeness": 0
            }
        
        # 统计
        total = len(kline_data)
        
        # 检查缺失字段
        required_fields = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing_fields = {}
        
        for field in required_fields:
            missing_count = sum(1 for row in kline_data if not row.get(field))
            if missing_count > 0:
                missing_fields[field] = missing_count
        
        # 计算完整性
        completeness = ((total * len(required_fields) - sum(missing_fields.values())) / 
                       (total * len(required_fields))) * 100
        
        # 检查日期连续性
        dates = [row.get('date') for row in kline_data if row.get('date')]
        date_gaps = DataQualityMonitor._check_date_continuity(dates)
        
        return {
            "stock_code": stock_code,
            "status": "ok" if completeness > 95 else "warning",
            "total_records": total,
            "completeness": round(completeness, 2),
            "missing_fields": missing_fields,
            "date_gaps": date_gaps,
            "checked_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def _check_date_continuity(dates: List[str]) -> List[Dict]:
        """检查日期连续性"""
        if len(dates) < 2:
            return []
        
        gaps = []
        for i in range(len(dates) - 1):
            try:
                d1 = datetime.strptime(dates[i], "%Y-%m-%d")
                d2 = datetime.strptime(dates[i+1], "%Y-%m-%d")
                diff = (d2 - d1).days
                
                # 跳过周末（2天差异）
                if diff > 2:
                    gaps.append({
                        "from": dates[i],
                        "to": dates[i+1],
                        "missing_days": diff - 1
                    })
            except:
                continue
        
        return gaps
    
    @staticmethod
    def check_data_accuracy(stock_code: str, kline_data: List[Dict]) -> Dict[str, Any]:
        """
        检查数据准确性
        
        Args:
            stock_code: 股票代码
            kline_data: K线数据
            
        Returns:
            准确性报告
        """
        if not kline_data:
            return {
                "stock_code": stock_code,
                "status": "no_data",
                "issues": []
            }
        
        issues = []
        
        for i, row in enumerate(kline_data):
            # 检查最高价 >= 最低价
            high = row.get('high', 0)
            low = row.get('low', 0)
            if high < low:
                issues.append({
                    "date": row.get('date'),
                    "issue": "high_less_than_low",
                    "high": high,
                    "low": low
                })
            
            # 检查收盘价在高低范围内
            close = row.get('close', 0)
            if close > high or close < low:
                issues.append({
                    "date": row.get('date'),
                    "issue": "close_out_of_range",
                    "close": close,
                    "high": high,
                    "low": low
                })
            
            # 检查成交量为负
            volume = row.get('volume', 0)
            if volume < 0:
                issues.append({
                    "date": row.get('date'),
                    "issue": "negative_volume",
                    "volume": volume
                })
        
        return {
            "stock_code": stock_code,
            "status": "ok" if len(issues) == 0 else "warning",
            "total_checked": len(kline_data),
            "issues_found": len(issues),
            "issues": issues[:10],  # 最多返回10个问题
            "checked_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def get_quality_report(stock_code: str, kline_data: List[Dict]) -> Dict[str, Any]:
        """
        获取完整质量报告
        
        Args:
            stock_code: 股票代码
            kline_data: K线数据
            
        Returns:
            完整质量报告
        """
        completeness = DataQualityMonitor.check_data_completeness(stock_code, kline_data)
        accuracy = DataQualityMonitor.check_data_accuracy(stock_code, kline_data)
        
        # 综合状态
        if completeness['status'] == 'no_data' or accuracy['status'] == 'no_data':
            overall_status = 'no_data'
        elif completeness['status'] == 'warning' or accuracy['status'] == 'warning':
            overall_status = 'warning'
        else:
            overall_status = 'ok'
        
        return {
            "stock_code": stock_code,
            "overall_status": overall_status,
            "completeness": completeness,
            "accuracy": accuracy,
            "generated_at": datetime.now().isoformat()
        }
