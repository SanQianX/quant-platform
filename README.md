# 量化数据平台

股票行情查询与分析平台

## 技术栈

- 后端: FastAPI + PostgreSQL
- 前端: Vue3 + ECharts
- 部署: Docker

## 快速启动

### 1. 启动数据库和服务

```bash
cd deploy
docker-compose up -d
```

### 2. 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 项目结构

```
quant-platform/
├── backend/          # FastAPI后端
│   ├── api/          # API路由
│   ├── models/       # 数据模型
│   ├── services/     # 业务逻辑
│   └── main.py       # 应用入口
├── frontend/         # Vue3前端
│   └── index.html    # 入口文件
├── deploy/           # Docker配置
│   └── docker-compose.yml
└── README.md
```

## 开发

### 后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 前端

```bash
cd frontend
npm install
npm run dev
```
