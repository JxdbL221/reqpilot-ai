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

项目初始化与基础技术训练阶段。

## 开发原则

- 先完成可运行的 MVP，再增加扩展功能
- AI 输出必须采用结构化数据并经过校验
- API Key、密码和真实用户数据不得提交到 GitHub
- 每周更新进度、测试结果和项目文档
