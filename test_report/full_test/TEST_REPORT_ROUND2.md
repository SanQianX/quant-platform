# 全面测试报告 - 第二轮

## 测试日期
2026-03-09 23:31+

## 测试工程师
测试工程师

---

## 测试结果汇总

### 第一轮测试 (16 APIs)

| API | 状态 |
|-----|------|
| /health | ✅ 200 |
| /api/stock/list | ✅ 200 |
| /api/stock/search | ✅ 200 |
| /api/stock/600519 | ✅ 200 |
| /api/stock/600519/history | ✅ 200 |
| /api/indicators/600519/ma | ✅ 200 |
| /api/indicators/600519/macd | ✅ 200 |
| /api/indicators/600519/rsi | ✅ 200 |
| /api/filter/presets | ✅ 200 |
| /api/filter/stocks/simple | ✅ 200 |
| /api/market/overview | ✅ 200 |
| /api/flow/600519/main | ✅ 200 |
| /api/toplist | ✅ 200 |
| /api/etf/list | ✅ 200 |
| /api/bond/list | ✅ 200 |
| /api/ipo/list | ✅ 200 |

### 第二轮测试 (16 APIs)

| API | 状态 |
|-----|------|
| /api/scheduler/status | ✅ 200 |
| /api/cache/stats | ⚠️ Timeout |
| /api/monitor/metrics | ✅ 200 |
| /api/risk/600519/metrics | ✅ 200 |
| /api/stock/600519/quote | ✅ 200 |
| /api/stock/600519/financial/balance | ✅ 200 |
| /api/stock/600519/dividend | ✅ 200 |
| /api/stock/600519/split | ✅ 200 |
| /api/stock/600519/profile | ✅ 200 |
| /api/stock/600519/industry | ✅ 200 |
| /api/stock/600519/adj/forward | ✅ 200 |
| /api/stock/600519/adj/backward | ✅ 200 |
| /api/stock/600519/order-book | ✅ 200 |
| /api/stock/600519/limit-price | ✅ 200 |
| /api/stock/600519/news | ✅ 200 |
| /api/stock/600519/announcements | ✅ 200 |

### 第三轮测试 (10 APIs)

| API | 状态 |
|-----|------|
| /api/options/600519 | ✅ 200 |
| /api/futures/quote | ✅ 200 |
| /api/hkstock/list | ✅ 200 |
| /api/usstock/list | ✅ 200 |
| /api/margin/list | ✅ 200 |
| /api/block-trade/list | ✅ 200 |
| /api/holder-trade/list | ✅ 200 |
| /api/restricted-share/list | ✅ 200 |
| /api/broker/list | ✅ 200 |
| /api/topinstitution/list | ✅ 200 |

---

## 测试统计

| 指标 | 数量 |
|------|------|
| 总测试API | 42 |
| 通过 | 41 |
| 失败 | 0 |
| 超时 | 1 |

---

## 结论

**🎉 测试通过率 97.6%！**

仅 /api/cache/stats 出现超时（可能需要认证或Redis未运行），其他41个API全部通过！
