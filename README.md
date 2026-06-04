# TestCase Gen Agent

基于 LLM + RAG 的智能测试用例生成系统，支持从需求文档自动提取功能点，并生成规范的测试用例。

## 功能特性

- 📄 **需求文档解析** — 上传 `.docx` 需求文档，自动提取目录结构和功能点
- 🔍 **RAG 检索增强** — 基于 Chroma 向量数据库，结合文档上下文生成更精准的测试用例
- 🤖 **LLM 智能生成** — 支持 Qwen-Plus / DeepSeek-Chat 等多种模型，自动生成标准化测试用例
- 🖥️ **Web 管理界面** — 提供功能点管理、用例生成、已保存用例三大模块
- 💾 **持久化存储** — SQLite 数据库存储功能点和测试用例，支持审核后保存
- 📋 **批量操作** — 支持全量功能点批量生成测试用例

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| AI 框架 | LangChain + LangGraph |
| 向量数据库 | Chroma |
| 关系数据库 | SQLite |
| 大模型 | Qwen-Plus / DeepSeek-Chat |
| 前端框架 | React 18 + Vite |
| UI 组件库 | Ant Design 5 |
| MCP 集成 | langchain-mcp-adapters (WebParser) |

## 项目结构

```
testcase_gen_agent/
├── src/
│   ├── App.py                    # FastAPI 后端入口，API 路由
│   ├── testcase_gen/
│   │   ├── chains.py             # LLM Chain 封装（RAG、用例生成、功能提取）
│   │   ├── prompts.py            # Prompt 模板
│   │   ├── models.py             # Pydantic 数据模型（TestCase、FeaturePoint）
│   │   ├── vectorstore.py        # Chroma 向量存储与检索
│   │   ├── create_rag.py         # RAG 知识库创建脚本
│   │   └── testcase_gen.py       # 命令行测试入口
│   ├── db/
│   │   ├── database.py           # SQLite 连接与表初始化
│   │   ├── feature_repo.py       # 功能点 CRUD
│   │   └── test_case_repo.py     # 测试用例 CRUD
│   ├── agent/                    # LangGraph Agent 实验示例
│   │   ├── agent1.py             # MCP 客户端 Agent
│   │   ├── agent2.py             # StateGraph Agent
│   │   ├── demo1.py              # 多 MCP 服务示例
│   │   └── memory_agent.py       # 带记忆的 Agent
│   ├── frontend/                 # React 前端
│   │   ├── src/components/       # FeaturePanel / GeneratePanel / SavedPanel
│   │   └── src/api/              # Axios API 封装
│   └── utils/                    # 工具函数（模型加载、配置、MCP 服务端）
├── .env                          # 环境变量（API Keys）
├── .gitignore
└── README.md
```

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Git

### 1. 克隆项目

```bash
git clone git@github.com:fantasyiew/testcase_gen.git
cd testcase_gen
```

### 2. 配置环境变量

创建 `.env` 文件（项目根目录），填入以下内容：

```env
# Qwen 模型（DashScope）
QWEN_API_KEY="your-qwen-api-key"
QWEN_API_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

# DeepSeek 模型
DEEPSEEK_API_KEY="your-deepseek-api-key"
DEEPSEEK_API_URL="https://api.deepseek.com"

# LangSmith 追踪（可选）
LANGSMITH_TRACING="true"
LANGSMITH_API_KEY="your-langsmith-api-key"

# DashScope 嵌入模型
DASHSCOPE_API_KEY="your-dashscope-api-key"
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. 构建前端

```bash
cd src/frontend
npm install
npm run build
cd ../..
```

### 5. 创建 RAG 知识库

将需求文档（`.docx`）放入项目目录，运行：

```bash
cd src/testcase_gen
python create_rag.py
```

### 6. 启动服务

```bash
cd src
python App.py
```

访问 http://localhost:8000 打开管理界面。

## 使用流程

```
需求文档(.docx) → 上传/解析 → 提取功能点 → RAG检索 → LLM生成测试用例 → 审核 → 保存入库
```

1. **功能点管理** — 上传需求文档，系统自动提取目录中的功能点并存入数据库
2. **测试用例生成** — 选择功能点，LLM 结合 RAG 检索的上下文生成标准化测试用例
3. **审核保存** — 审核生成的用例，通过后保存到数据库
4. **已保存用例** — 查看、管理所有已保存的测试用例

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/features/upload` | 上传需求文档 |
| GET | `/api/features` | 获取所有功能点 |
| POST | `/api/features/extract` | 从文档提取功能点 |
| DELETE | `/api/features/{id}` | 删除功能点 |
| POST | `/api/test-cases/generate` | 生成单个功能的测试用例 |
| POST | `/api/test-cases/generate-all` | 批量生成全部测试用例 |
| POST | `/api/test-cases/save` | 保存审核通过的用例 |
| GET | `/api/test-cases/stats` | 获取用例统计信息 |
| DELETE | `/api/test-cases/{id}` | 删除测试用例 |

## 测试用例结构

每个生成的测试用例包含以下字段：

| 字段 | 说明 |
|------|------|
| `module_name` | 模块名称 |
| `function` | 功能项 |
| `case_description` | 用例说明 |
| `precondition` | 前置条件 |
| `input_data` | 输入数据 |
| `steps` | 执行步骤 |
| `expected_result` | 预期结果 |
| `priority` | 重要程度（高/中/低） |
| `test_result` | 执行结果（默认为未执行） |

## License

MIT
