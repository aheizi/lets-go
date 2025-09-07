# Let's Go - 基于NeMo Agent的智能旅行规划平台

🌍 一个集成了NVIDIA NeMo Agent Toolkit的现代化旅行规划应用，提供传统规划和AI智能规划两种模式，让旅行规划变得更加智能和便捷。

## ✨ 项目特色

- 🤖 **AI智能规划**: 集成NVIDIA NeMo Agent Toolkit，提供智能化的旅行建议
- 🗺️ **地图集成**: 实时地图显示和路线规划
- 🌤️ **天气服务**: 实时天气信息获取
- 📱 **响应式设计**: 支持桌面端和移动端
- 🔐 **用户认证**: 完整的用户注册、登录系统
- 💾 **数据持久化**: 支持旅行计划的保存和管理
- 🚀 **现代化架构**: 前后端分离，API优先设计

## 🛠️ 技术栈

### 前端
- **React 18** - 现代化的用户界面框架
- **TypeScript** - 类型安全的JavaScript超集
- **Vite** - 快速的构建工具
- **Tailwind CSS** - 实用优先的CSS框架
- **React Router** - 客户端路由管理
- **Zustand** - 轻量级状态管理
- **Lucide React** - 现代化图标库

### 后端
- **Python 3.8+** - 后端开发语言
- **FastAPI** - 现代化的Python Web框架
- **Uvicorn** - ASGI服务器
- **Pydantic** - 数据验证和序列化
- **LangGraph** - AI工作流编排
- **LangChain** - LLM应用开发框架

### AI集成
- **NVIDIA NeMo Agent Toolkit** - 企业级AI Agent开发工具
- **OpenAI API** - GPT模型集成
- **Anthropic Claude** - Claude模型支持
- **LangChain** - LLM应用开发框架

## 📁 项目结构

```
lets-go/
├── src/                          # 前端源码
│   ├── components/               # React组件
│   ├── pages/                    # 页面组件
│   │   ├── Home.tsx             # 首页
│   │   ├── PlanCreate.tsx       # 创建计划
│   │   ├── PlanList.tsx         # 计划列表
│   │   ├── PlanDetail.tsx       # 计划详情
│   │   └── ...
│   ├── hooks/                    # 自定义Hooks
│   ├── store/                    # 状态管理
│   └── assets/                   # 静态资源
├── python_api/                   # 后端API
│   ├── main.py                  # FastAPI主应用
│   ├── routes/                  # API路由
│   │   ├── auth.py             # 认证路由
│   │   ├── plans.py            # 传统计划路由
│   │   └── nemo_plans.py       # AI智能计划路由
│   ├── agents/                  # AI Agent定义
│   ├── services/                # 业务服务
│   │   ├── llm_service.py      # LLM服务
│   │   ├── map_service.py      # 地图服务
│   │   └── weather_service.py  # 天气服务
│   ├── models/                  # 数据模型
│   ├── configs/                 # 配置文件
│   └── NeMo-Agent-Toolkit/      # NeMo Agent工具包
├── public/                       # 公共静态文件
├── package.json                  # 前端依赖配置
└── python_api/requirements.txt   # 后端依赖配置
```

## 🚀 快速开始

### 环境要求

- **Node.js** 18+ 
- **Python** 3.8+
- **npm** 或 **pnpm**
- **Git**

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd lets-go
```

#### 2. 安装前端依赖

```bash
# 使用 npm
npm install

# 或使用 pnpm (推荐)
pnpm install
```

#### 3. 安装后端依赖

```bash
cd python_api
pip install -r requirements.txt
```

#### 4. 环境配置

在 `python_api` 目录下创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的环境变量：

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# 地图服务 (可选)
MAP_API_KEY=your_map_api_key

# 天气服务 (可选)
WEATHER_API_KEY=your_weather_api_key

# 应用配置
PORT=3001
ENVIRONMENT=development
```

#### 5. 启动应用

**方式一：同时启动前后端 (推荐)**

```bash
# 在项目根目录
npm run dev
```

**方式二：分别启动**

```bash
# 启动后端 (终端1)
cd python_api
python main.py

# 启动前端 (终端2)
npm run client:dev
```

#### 6. 访问应用

- 前端应用: http://localhost:5173
- 后端API: http://localhost:3001
- API文档: http://localhost:3001/api/docs

## 🎯 功能特性

### 传统旅行规划
- 📝 手动创建旅行计划
- 📅 日程安排管理
- 📍 地点添加和编辑
- 💰 预算管理
- 📋 计划列表查看

### AI智能规划
- 🤖 基于NeMo Agent的智能推荐
- 🗣️ 自然语言交互
- 🎯 个性化建议生成
- 🔄 实时优化调整
- 📊 智能数据分析

### 用户系统
- 👤 用户注册和登录
- 🔐 安全认证机制
- 👥 个人资料管理
- 📱 多设备同步

## 📡 API接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出

### 传统计划接口
- `GET /api/plans` - 获取计划列表
- `POST /api/plans` - 创建新计划
- `GET /api/plans/:id` - 获取计划详情
- `PUT /api/plans/:id` - 更新计划
- `DELETE /api/plans/:id` - 删除计划

### AI智能计划接口
- `POST /api/nemo/plans` - AI生成计划
- `POST /api/nemo/chat` - AI对话交互
- `POST /api/nemo/optimize` - 计划优化建议

### 工具服务接口
- `GET /api/weather` - 天气信息查询
- `GET /api/maps` - 地图和路线服务
- `GET /api/health` - 健康检查

## 🔧 开发指南

### 代码规范

```bash
# 代码检查
npm run lint

# 类型检查
npm run check

# 代码格式化 (Python)
cd python_api
black .
flake8 .
```

### 测试

```bash
# 前端测试
npm run test

# 后端测试
cd python_api
pytest
```

### 构建部署

```bash
# 前端构建
npm run build

# 预览构建结果
npm run preview
```

## 🌐 部署

### Vercel部署 (推荐)

1. 连接GitHub仓库到Vercel
2. 配置环境变量
3. 自动部署

### 手动部署

```bash
# 构建前端
npm run build

# 部署后端
cd python_api
uvicorn main:app --host 0.0.0.0 --port 3001
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 遵循现有的代码风格
- 添加适当的注释和文档
- 确保所有测试通过
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [NVIDIA NeMo](https://github.com/NVIDIA/NeMo) - AI模型和工具包
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Python Web框架
- [React](https://reactjs.org/) - 用户界面库
- [Tailwind CSS](https://tailwindcss.com/) - CSS框架
- [LangChain](https://langchain.com/) - LLM应用开发框架

## 📞 联系我们

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](../../issues)
- 发起 [Discussion](../../discussions)
- 邮箱: [your-email@example.com]

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！
