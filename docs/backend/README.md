# 后端 API 架构文档

## 概述

量化数据平台后端基于 **FastAPI** 构建，提供丰富的金融数据 API 接口。

## 技术栈

| 技术 | 用途 |
|------|------|
| FastAPI | Web 框架 |
| SQLAlchemy | ORM |
| AkShare | 金融数据源 |
| Tushare | 金融数据源 |
| APScheduler | 定时任务 |

## 模块数量统计

- **API 路由模块**: 56 个
- **服务层模块**: 9 个
- **数据模型**: 3 个
- **中间件**: 3 个

## API 分类

### 1. 股票相关 (stock)
- `stock.py` - 股票基本信息
- `stock_extra.py` - 股票扩展数据

### 2. 行情数据 (quote)
- `quote.py` - 实时行情
- `limit_price.py` - 涨跌停价格
- `suspension.py` - 停牌信息

### 3. K线数据 (kline)
- `adj.py` - 复权数据
- `history` 相关 - 历史数据

### 4. 技术分析 (analysis)
- `indicators.py` - 技术指标
- `signals.py` - 交易信号
- `filter.py` - 股票筛选
- `advanced_filter.py` - 高级筛选

### 5. 财务数据 (financial)
- `financial.py` - 财务数据
- `dividend.py` - 分红配股
- `rights_issue.py` - 配股
- `holder_trade.py` - 股东增减持

### 6. ETF/期权/期货
- `etf.py` - ETF 数据
- `options.py` - 期权数据
- `futures.py` - 期货数据

### 7. 港股/美股
- `hkstock.py` - 港股
- `usstock.py` - 美股

### 8. 市场数据 (market)
- `market.py` - 市场行情
- `toplist.py` - 排行榜
- `toplist_history.py` - 历史排行

### 9. 资金流向 (flow)
- `flow.py` - 资金流向
- `flow_history.py` - 历史资金流向

### 10. 风险与告警
- `risk.py` - 风险评估
- `alert.py` - 告警通知

### 11. 其他
- `auth.py` - 认证授权
- `users.py` - 用户管理
- `cache.py` - 缓存管理
- `scheduler.py` - 定时任务
- `monitor.py` - 系统监控
- `export.py` - 数据导出
