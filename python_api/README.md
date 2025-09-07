# Let's Go Python 后端

基于 FastAPI 的 AI 旅行规划应用后端服务。

## 功能特性

- 🚀 **FastAPI**: 现代、快速的 Web 框架
- 📝 **自动文档**: 自动生成 API 文档 (Swagger UI)
- 🔒 **类型安全**: 使用 Pydantic 进行数据验证
- ⚡ **异步支持**: 高性能异步处理
- 🌐 **CORS 支持**: 跨域资源共享
- 🔐 **JWT 认证**: JSON Web Token 身份验证

## 快速开始

### 环境要求

- Python 3.8+
- pip 或 conda

### 安装依赖

```bash
# 方法 1: 使用启动脚本自动安装
python start.py --install

# 方法 2: 手动安装
pip install -r requirements.txt
```

### 环境配置

1. 复制环境变量示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，配置相关参数：
```env
PORT=3001
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

### 启动服务

```bash
# 方法 1: 使用启动脚本
python start.py

# 方法 2: 直接使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 3001 --reload

# 方法 3: 从项目根目录启动
npm run server:dev
```

### 访问 API 文档

服务启动后，可以访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:3001/api/docs
- **ReDoc**: http://localhost:3001/api/redoc

## API 接口

### 健康检查

```http
GET /api/health
```

### 用户认证

```http
# 用户注册
POST /api/auth/register

# 用户登录
POST /api/auth/login

# 用户登出
POST /api/auth/logout

# 获取当前用户信息
GET /api/auth/me
```

## 项目结构

```
python_api/
├── main.py              # FastAPI 主应用
├── start.py             # 启动脚本
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量示例
├── .env                 # 环境变量配置（需要创建）
├── routes/              # 路由模块
│   ├── __init__.py
│   └── auth.py          # 认证路由
└── README.md            # 说明文档
```

## 开发指南

### 添加新的路由

1. 在 `routes/` 目录下创建新的路由文件
2. 在 `main.py` 中导入并注册路由
3. 使用 Pydantic 模型定义请求和响应数据结构

### 数据库集成

项目预留了数据库集成的配置，可以根据需要选择：

- **SQLAlchemy + PostgreSQL**: 关系型数据库
- **MongoDB + Motor**: 文档型数据库
- **SQLite**: 轻量级开发数据库

### 部署

```bash
# 生产环境启动
uvicorn main:app --host 0.0.0.0 --port 3001

# 使用 Gunicorn (推荐)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3001
```

## 与前端集成

该 Python 后端完全兼容原有的 Express.js 后端 API，前端代码无需修改即可使用。

- 前端地址: http://localhost:5173
- 后端地址: http://localhost:3001
- API 前缀: `/api`

## 故障排除

### 常见问题

1. **端口被占用**: 修改 `.env` 文件中的 `PORT` 配置
2. **依赖安装失败**: 确保 Python 版本 >= 3.8
3. **CORS 错误**: 检查 `main.py` 中的 CORS 配置

### 日志查看

```bash
# 查看服务器日志
tail -f logs/app.log
```

## 贡献

欢迎提交 Issue 和 Pull Request！