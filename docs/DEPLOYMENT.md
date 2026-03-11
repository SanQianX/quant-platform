# 量化数据平台 - Docker 部署指南

## 概述

本文档提供使用 Docker 和 Docker Compose 部署量化数据平台的完整指南。

## 系统要求

- Docker Engine 20.10+
- Docker Compose 2.0+
- Windows 10/11 (WSL2) / Linux / macOS

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd quant-platform
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入真实的 Tushare Token
# Tushare Token 获取: https://tushare.pro 注册后获取
```

### 3. 启动所有服务

```bash
cd deploy
docker-compose up -d
```

### 4. 验证服务

检查服务状态：
```bash
docker-compose ps
```

访问应用：
- 前端开发服务器: http://localhost:3000
- 前端生产版: http://localhost:3001
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- PostgreSQL: localhost:5432

## 服务架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Network                          │
│                   (quant-network)                           │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │   Backend   │    │  Frontend   │    │  Postgres   │   │
│  │   :8000     │◄──►│  :3000/80   │    │   :5432     │   │
│  │  (FastAPI)  │    │   (Vue3)    │    │  (Database) │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│        │                   │                   │            │
│        └───────────────────┴───────────────────┘            │
│                         │                                    │
│                    Host Machine                              │
│              (localhost:8000/3000/3001)                      │
└─────────────────────────────────────────────────────────────┘
```

## 详细配置

### 端口映射

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|---------|---------|------|
| backend | 8000 | 8000 | FastAPI 后端 |
| frontend-dev | 3000 | 3000 | Vue 开发服务器 (热更新) |
| frontend-prod | 80 | 3001 | Nginx 生产构建 |
| postgres | 5432 | 5432 | PostgreSQL 数据库 |

### 环境变量

在 `.env` 文件中配置以下变量：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `TUSHARE_TOKEN` | Tushare API Token | - |
| `DB_HOST` | 数据库主机 | postgres |
| `DB_PORT` | 数据库端口 | 5432 |
| `DB_USER` | 数据库用户名 | quant_user |
| `DB_PASSWORD` | 数据库密码 | quant_pass |
| `DB_NAME` | 数据库名称 | quant_platform |

## 使用场景

### 开发模式 (推荐)

启动前端开发服务器 + 后端 + 数据库：

```bash
# 方式1: 启动所有服务
docker-compose up -d

# 方式2: 只启动后端和数据库，在主机运行前端
docker-compose up -d postgres backend
cd ../frontend && npm run dev
```

特点：
- 代码热更新 (通过 volume 挂载)
- 实时查看代码修改效果
- 适合日常开发

### 生产模式

```bash
# 只启动生产构建版本
docker-compose up -d postgres frontend backend
```

特点：
- 使用 Nginx 提供静态文件
- 适合部署测试

## 常用命令

### 启动服务
```bash
cd deploy
docker-compose up -d          # 后台启动
docker-compose up            # 前台启动 (查看日志)
```

### 停止服务
```bash
docker-compose down          # 停止并删除容器
docker-compose down -v       # 同时删除数据卷
```

### 查看日志
```bash
docker-compose logs -f       # 查看所有日志
docker-compose logs -f backend  # 只看后端日志
```

### 重启服务
```bash
docker-compose restart backend
```

### 进入容器
```bash
docker exec -it quant-backend sh
docker exec -it quant-db psql -U quant_user -d quant_platform
```

### 数据持久化

PostgreSQL 数据存储在 Docker 卷中：
```bash
# 查看卷
docker volume ls | grep quant

# 备份数据
docker run --rm -v quant-platform_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data
```

## 故障排查

### 容器无法启动

```bash
# 检查容器状态
docker-compose ps

# 查看详细日志
docker-compose logs <service-name>
```

### 数据库连接失败

1. 确认 PostgreSQL 容器正在运行：
   ```bash
   docker-compose ps
   ```

2. 检查健康状态：
   ```bash
   docker inspect quant-db | grep -A 10 Health
   ```

3. 等待数据库就绪后再启动后端

### 前端无法访问后端

1. 检查后端是否正常运行：
   ```bash
   curl http://localhost:8000/docs
   ```

2. 检查 Nginx 代理配置：
   ```bash
   docker exec quant-frontend cat /etc/nginx/conf.d/default.conf
   ```

### Windows 路径问题

在 Windows 上使用 Docker Desktop，volume 路径格式：
```yaml
# 正确格式
volumes:
  - //f/quant-platform/backend:/app
  - ./relative/path:/app
```

### 代码修改不生效

1. 确保使用 volume 挂载：
   ```yaml
   volumes:
     - ../backend:/app   # 挂载源代码
   ```

2. 后端开启了 `--reload` 选项，修改代码会自动重载

## 清理

```bash
# 停止所有服务
docker-compose down

# 删除数据卷 (谨慎!)
docker-compose down -v

# 删除镜像
docker-compose down --rmi all

# 完全清理
docker system prune -a
```

## 进阶配置

### 使用外部数据库

修改 `docker-compose.yml` 中的数据库配置或设置环境变量：

```yaml
environment:
  - DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### 自定义 Nginx 配置

编辑 `frontend/nginx.conf` 文件。

### 添加 Redis 缓存

在 `docker-compose.yml` 中添加：

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  networks:
    - quant-network
```

## 相关文档

- [后端文档](../backend/)
- [前端文档](../frontend/)
- [API文档](http://localhost:8000/docs)
