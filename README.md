# Wikforge

企业级知识库系统。基于 RAG 架构的文档管理 / 智能搜索 / AI 问答平台。

## 技术栈

**后端**
- Python 3.11 + FastAPI + SQLAlchemy 2.0 (async)
- Celery (文档处理流水线)
- Alembic (数据库迁移)

**前端**
- Next.js 14 (App Router) + Tailwind + shadcn/ui
- Zustand (状态管理) + Playwright (E2E)

**基础设施**
- PostgreSQL 16 (元数据)
- Redis 7 (缓存 / Celery broker)
- OpenSearch 2.17 (BM25 全文检索)
- Qdrant 1.14 (向量检索, Dense + Sparse)
- MinIO (S3 兼容对象存储)
- LiteLLM Proxy (统一 LLM 网关)

## 核心能力

- 文档解析: PDF / DOCX / Markdown / HTML / 源代码 + LLM 兜底解析 (扫描版 PDF)
- Profile 系统: 自动匹配文档类型 (通用文本 / 中式技术规范 / 扫描版 PDF)
- 复合搜索: BM25 + Dense Vector + Sparse Vector + RRF 融合 + Cross-Encoder 重排
- 查询增强: Rewriting / HyDE / Sub-query Decomposition
- RAG 问答: 流式 SSE 输出 + 引用标注 + 会话记忆
- 反馈闭环: 用户反馈 → 聚合分析 → 优化建议 → 一键应用 → 重处理
- 领域词典: 同义词 + 术语标准化 + 候选词审核
- 完整后台: 空间 / 用户 / 权限 / Profile / 词典 / 审核 / LLM / 监控

## 快速启动

```bash
# 1. 复制配置, 按需填写凭证
cp .env.example .env
make secrets       # 生成强随机密钥, 复制到 .env
vim .env           # 至少填: CPA_API_KEY / DASHSCOPE_API_KEY

# 2. 一键拉起
make first-run

# 3. 访问
# http://localhost          前端
# http://localhost:8000/docs API 文档
# http://localhost:4000/ui   LiteLLM Admin
```

详细部署 / 升级 / 备份 / 排错见 [`docs/deploy.md`](docs/deploy.md)。

## 常用命令

```bash
make help            # 查看全部命令
make ps              # 服务状态
make logs            # 跟踪日志
make logs-api        # 只看 api
make psql            # 进 PostgreSQL CLI
make verify          # 完整健康检查
make down            # 停止 (保留数据)
make reset           # 完全清理 (会丢数据!)
```

## 冒烟测试

```bash
./scripts/smoke-test.sh
```

走一遍: 登录 → 创建空间 → 上传文档 → 等处理 → 搜索 → RAG 问答。

## 目录结构

```
wikforge/
├── backend/                  Python / FastAPI
│   ├── app/
│   │   ├── api/              路由层
│   │   ├── services/         业务逻辑
│   │   ├── tasks/            Celery 任务
│   │   ├── models/           SQLAlchemy ORM
│   │   ├── core/             基础设施 (db / redis / qdrant / opensearch / minio)
│   │   └── scripts/          init_db / api-entrypoint
│   ├── alembic/              数据库迁移
│   ├── tests/                单元 + 集成测试
│   └── eval/                 检索质量评估
├── frontend/                 Next.js 14
│   ├── src/app/              App Router 页面
│   ├── src/components/       UI 组件
│   ├── src/lib/              api-client / utils
│   └── src/stores/           Zustand stores
├── litellm/                  LiteLLM Proxy 配置
├── scripts/                  运维脚本
├── docs/                     文档
└── docker-compose.yml        9 服务编排
```

## 开发规范

- Python 代码: ruff format + mypy
- TypeScript: 默认 Next.js + ESLint
- 提交前运行 `./scripts/smoke-test.sh` 确保无回归
- 数据库改动必须走 Alembic 迁移, 禁止 `Base.metadata.create_all`

## License

私有项目, 未授权不得外发。
