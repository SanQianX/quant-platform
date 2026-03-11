# 前端页面逻辑文档

## 技术架构

前端采用 **单页应用 (SPA)** 模式，使用原生 JavaScript + Vue 3 CDN + ECharts。

### 依赖库

| 库 | 版本 | 用途 |
|---|------|------|
| Vue | 3.4.15 | UI 框架 (CDN) |
| ECharts | 5.5.0 | 图表可视化 (CDN) |
| Fetch API | - | HTTP 请求 |

### 项目结构

```
frontend/
├── index.html      # 主页面 (所有逻辑)
├── public/
│   └── lib/       # 第三方库 (Vue, ECharts)
└── package.json   # 项目配置
```

## 页面功能模块

### 1. 股票列表模块
- 显示可用股票列表
- 支持点击选中
- 显示股票代码、名称、类型

### 2. 搜索功能
- 搜索输入框
- 实时过滤股票列表
- 支持代码和名称搜索

### 3. K线图表
- ECharts 蜡烛图 (K线图)
- 成交量柱状图
- 数据缩放支持
- 十字光标

### 4. 数据导出
- CSV 导出
- JSON 导出

## 核心代码逻辑

### Vue 应用创建
```javascript
const { createApp, ref, onMounted, watch } = Vue;
const app = createApp({ ... });
```

### API 调用
```javascript
const axios = {
  async get(url) {
    const res = await fetch(url);
    return { data: await res.json() };
  }
};
```

### K线图配置
使用 ECharts 的 candlestick 类型绘制 K 线，配合 bar 类型绘制成交量。
