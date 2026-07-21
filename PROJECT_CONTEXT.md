# ReqPilot AI — Project Context

## 项目名称

ReqPilot AI

## 毕业设计题目

基于大语言模型的软件需求分析与测试用例生成及追踪系统设计与实现

## 项目目标

构建一个面向软件需求工程与测试工作的 AI 辅助平台，实现需求文档解析、需求质量分析、测试用例生成、人工审核和需求—测试追踪。

## MVP 核心功能

1. 上传并解析 PDF、DOCX、Markdown 和 TXT 需求文档
2. 提取功能需求、非功能需求、参与者和业务规则
3. 检查需求的歧义、遗漏、冲突和不可测试问题
4. 生成用户故事、验收标准和测试用例
5. 支持正常、异常、边界和状态类测试场景
6. 建立需求与测试用例追踪矩阵
7. 支持人工审核、修改以及 Markdown/Excel 导出

## 计划技术栈

- Frontend: Vue 3 + TypeScript + Element Plus
- Backend: FastAPI + Pydantic + SQLAlchemy
- Database: MySQL
- AI: OpenAI-compatible API / DeepSeek
- Document Parsing: Docling
- Testing: pytest + Vitest
- Deployment: Docker Compose

## 当前阶段

基础后端已初始化，首个健康检查接口及自动化测试已合并。当前处于项目规范完善与下一功能切片设计阶段。

## 当前实现基线

- FastAPI 应用入口：`apps/backend/app/main.py`
- 健康检查接口：`GET /api/v1/health`
- 后端自动化测试：`tests/backend/test_health.py`
- 已完成 GitHub Issue #1，并通过 PR #2 合并到 `main`
- 后续开发继续采用 Issue → 分支 → 编码 → 测试 → Commit → Push → PR → Merge 流程

## 近期重点

1. 保持 `AGENTS.md`、`PROGRESS.md`、`CHANGELOG.md` 与仓库状态一致
2. 将需求文档导入与解析拆分为可独立验证的最小功能切片
3. 在增加大模型能力前建立可测试的接口、数据结构和 Mock Provider

## 开发原则

- 先完成可运行的 MVP，再增加扩展功能
- AI 输出必须采用结构化数据并经过校验
- API Key、密码和真实用户数据不得提交到 GitHub
- 每周更新进度、测试结果和项目文档
- 未经确认不直接提交、推送、合并或部署变更
