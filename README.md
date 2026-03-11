# 量化数据平台

股票行情查询与分析平台

## 项目简介

Quant Platform 是一个专业的股票数据查询与分析平台，提供实时股票行情、K线数据、历史数据查询等功能。

### 主要特性

- 📈 实时股票行情查询
- 📊 K线数据支持（日线/周线/月线）
- 🔄 自动数据更新定时任务
- 💾 数据缓存加速
- 📚 完整API文档

## 技术栈

- 后端: FastAPI + SQLAlchemy + Tushare/AkShare
- 前端: Vue3 + ECharts
- 数据库: SQLite/PostgreSQL
- 缓存: 内存缓存
- 部署: Docker

## 快速启动

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

### 3. 访问应用

- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc

## API 使用示例

### 1. 获取股票列表

```bash
curl http://localhost:8000/api/stock/list
```

响应:
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {"code": "000001", "name": "平安银行", "market": "sz", "stock_type": "stock"},
    {"code": "600519", "name": "贵州茅台", "market": "sh", "stock_type": "stock"}
  ]
}
```

### 2. 搜索股票

```bash
curl "http://localhost:8000/api/stock/search?keyword=茅台"
```

### 3. 获取K线数据

```bash
# 日K线
curl http://localhost:8000/api/stock/000001

# 历史K线（日线）
curl "http://localhost:8000/api/stock/000001/history?period=daily&start_date=2024-01-01&end_date=2024-12-31"

# 周线
curl "http://localhost:8000/api/stock/000001/history?period=weekly"

# 月线
curl "http://localhost:8000/api/stock/000001/history?period=monthly"
```

### 4. 定时任务管理

```bash
# 获取任务状态
curl http://localhost:8000/api/scheduler/status

# 启动定时任务
curl -X POST http://localhost:8000/api/scheduler/start

# 手动触发更新
curl -X POST "http://localhost:8000/api/scheduler/trigger?period=daily"

# 更新单只股票
curl -X POST "http://localhost:8000/api/scheduler/update/000001?period=daily"
```

### 5. 缓存管理

```bash
# 查看缓存状态
curl http://localhost:8000/api/cache/stats

# 清空缓存
curl -X POST http://localhost:8000/api/cache/clear
```

### 6. 导出数据

```bash
# 导出CSV
curl "http://localhost:8000/api/stock/000001/export?format=csv" -o stock.csv

# 导出JSON
curl "http://localhost:8000/api/stock/000001/export?format=json" -o stock.json
```

## API 文档

完整API文档访问:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 项目结构

```
quant-platform/
├── backend/              # FastAPI后端
│   ├── api/             # API路由
│   │   ├── stock.py     # 股票接口
│   │   ├── scheduler.py # 定时任务接口
│   │   └── cache.py     # 缓存管理接口
│   ├── models/          # 数据模型
│   ├── services/        # 业务逻辑
│   ├── scheduler/       # 定时任务
│   ├── utils/           # 工具函数
│   ├── main.py          # 应用入口
│   └── requirements.txt # 依赖
├── frontend/            # Vue3前端
├── deploy/              # Docker配置
├── docs/                # 项目文档
└── README.md
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| TUSHARE_TOKEN | Tushare API Token | - |
| REDIS_HOST | Redis主机 | localhost |
| REDIS_PORT | Redis端口 | 6379 |

### Tushare Token 配置

```bash
# Linux/Mac
export TUSHARE_TOKEN="your_token_here"

# Windows
set TUSHARE_TOKEN=your_token_here
```

## 开发

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python main 前端启动

.py
```

###```bash
cd frontend
npm install
npm run dev
```

## 部署

### Docker 部署 (推荐)

#### 1. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入 Tushare Token
# 获取Token: https://tushare.pro 注册后获取
```

#### 2. 启动服务

```bash
cd deploy
docker-compose up -d
```

#### 3. 访问应用

- 前端开发服务器: http://localhost:3000
- 前端生产版: http://localhost:3001
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

详细部署指南: [Docker部署文档](docs/DEPLOYMENT.md)

### 本地部署

```bash
cd deploy
docker-compose up -d
```

## 迭代历史

| 迭代 | 功能 | 状态 |
|------|------|------|
| #1 | 基础股票查询API | ✅ |
| #2 | 历史K线API（日/周/月） | ✅ |
| #3 | 定时数据采集任务 | ✅ |
| #4 | 缓存层优化 | ✅ |
| #5 | API文档完善 | 🔄 |

## 许可证

MIT License
