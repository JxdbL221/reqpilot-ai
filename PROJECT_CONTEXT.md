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

基础后端、健康检查接口、TXT 需求文档上传与内存解析功能已经完成。

需求文本预处理接口已经实现并通过自动化测试，可以将原始多行需求文本清理并转换为结构化需求条目。

需求质量检测的数据模型、分层结构、确定性 Mock Provider 和 HTTP 接口已经完成，可以对结构化需求返回歧义、遗漏、冲突和不可测试问题。当前版本仍未接入真实大语言模型。

## main 分支实现基线

- FastAPI 应用入口：`apps/backend/app/main.py`
- 健康检查接口：`GET /api/v1/health`
- TXT 文档上传接口：`POST /api/v1/documents/upload`
- 需求文本预处理接口：`POST /api/v1/requirements/preprocess`
- 需求质量检测接口：`POST /api/v1/requirements/quality-check`
- 文档接口层：`apps/backend/app/api/documents.py`
- 文档响应模型：`apps/backend/app/schemas/document.py`
- TXT 解析服务：`apps/backend/app/services/document_parser.py`
- 质量检测 Provider：`apps/backend/app/providers/requirement_quality.py`
- 质量检测 Service：`apps/backend/app/services/requirement_quality_checker.py`
- 健康检查测试：`tests/backend/test_health.py`
- 文档上传测试：`tests/backend/test_documents.py`
- GitHub Issue #1 已通过 PR #2 合并
- TXT 文档上传与解析功能已通过 PR #7 合并
- 项目继续采用 Issue → 分支 → 编码 → 测试 → Commit → Push → PR → Merge 流程

## 需求文本预处理实现

- Issue：#8 添加需求文本预处理接口
- 接口：`POST /api/v1/requirements/preprocess`
- 接口层：`apps/backend/app/api/requirements.py`
- 数据模型：`apps/backend/app/schemas/requirement.py`
- 预处理服务：`apps/backend/app/services/requirement_preprocessor.py`
- 自动化测试：`tests/backend/test_requirements.py`

### 当前预处理规则

1. 统一处理 `\r\n`、`\n` 和 `\r` 换行符
2. 清理每行首尾空白
3. 删除空行
4. 将每个非空行视为一条需求
5. 保留需求原始顺序
6. 生成从 1 开始的连续序号
7. 全空白文本返回 HTTP 400

预处理模块本身不负责智能语义分句、需求分类、质量检测、大模型调用和数据库存储。质量检测由独立的接口、Service 和 Provider 完成。

## 需求质量检测实现

- Issue：#10 添加需求质量检测模型与 Mock 接口
- 接口：`POST /api/v1/requirements/quality-check`
- 数据模型：`apps/backend/app/schemas/requirement.py`
- Provider 协议与 Mock：`apps/backend/app/providers/requirement_quality.py`
- Service：`apps/backend/app/services/requirement_quality_checker.py`
- API 测试：`tests/backend/test_requirement_quality_api.py`

### 当前质量检测边界

1. 请求只接收至少一条带唯一正整数序号的结构化需求
2. 响应支持歧义、遗漏、冲突和不可测试四类问题
3. 严重程度限定为 `low`、`medium` 和 `high`
4. Mock Provider 使用固定关键词和固定结果顺序，保证测试可重复
5. Service 只依赖 Provider 协议，负责调用检测能力和统计数量
6. API 使用 FastAPI 依赖注入选择当前 Provider
7. 非法请求由 Pydantic 统一返回 HTTP 422

当前 Mock 仅用于验证分层、接口和测试流程，不代表生产级自然语言检测能力。

## 近期重点

1. 完成 Issue #10 的代码审查、提交、PR 和合并流程
2. 将真实 LLM Provider 作为独立 Issue 设计和实现
3. 为真实模型调用补充结构化输出校验、超时、重试和失败降级
4. 继续保持 `PROGRESS.md`、`CHANGELOG.md` 和仓库实现状态一致

## 开发原则

- 先完成可运行、可测试的最小功能切片，再扩展复杂功能
- AI 输出必须采用结构化数据并经过校验
- API Key、密码和真实用户数据不得提交到 GitHub
- 新功能必须包含适当的自动化测试
- 每周更新进度、测试结果和项目文档
- 未经确认不直接提交、推送、合并或部署变更
