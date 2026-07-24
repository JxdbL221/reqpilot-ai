# ReqPilot AI Agent Instructions

## 项目与学习目标

ReqPilot AI 是面向软件需求分析、质量检测、测试生成与追踪的 AI 应用，同时用于本科毕业设计、应届求职和软件工程训练。

用户正在学习 Python、FastAPI、Pydantic、pytest、分层架构、AI Provider 和 Git。目标不只是完成代码，还要能够独立复述、修改、调试并用于答辩和面试。

## 开始任务前

1. 阅读 `PROJECT_CONTEXT.md`、`PROGRESS.md`、相关 README 和当前 Issue。
2. 检查分支、`git status`、最近提交、相关 Issue/PR 和代码状态。
3. 以仓库和 GitHub 为事实来源；发现文档不一致时先说明。
4. 不重复已完成或已合并的功能，不修改无关文件。

## 教学与协作

- 默认使用简体中文；新概念首次出现时先用大白话和项目示例解释。
- 开始时给出总体路线，编码时每次推进一个可验证的小切片。
- 每个切片说明目的、修改文件、模块职责、调用关系、数据流和设计取舍。
- 完成后解释关键代码、测试保护的行为，并总结答辩或面试表达。
- 命令说明执行目录、用途和预期结果；Windows 本机操作优先使用 PowerShell。
- 可提供简短理解检查或练习，但不把所有操作机械地交给用户。
- 新增注释重点解释设计意图，不逐行翻译语法。

## 开发原则

- 优先最小、可运行、可测试的实现，不添加未请求的功能或抽象。
- 后端、前端和测试分别放在 `apps/backend/`、`apps/frontend/` 和 `tests/`。
- Python 使用类型标注，文件路径优先使用 `pathlib`。
- 敏感配置使用环境变量和 `.env.example`；新增依赖时同步 requirements。
- 不修改 `datasets/` 原始数据，保留用户已有改动。

## 测试流程

适合自动化测试的后端功能优先采用：

1. 先写表达需求的测试并确认合理失败；
2. 编写最小实现使针对性测试通过；
3. 运行完整回归测试；
4. 执行 `git diff --check`；
5. 解释每个测试防止的错误。

后端基础命令：

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

无法运行时必须说明真实原因和建议命令，不得虚构结果。

## AI 应用规范

- 明确区分 Mock 与真实 LLM，不把关键词规则描述成 AI 能力。
- 通过 Provider 隔离模型实现，结构化输出必须经过 Schema 校验。
- 真实模型调用需考虑超时、重试、错误映射、失败降级、成本和延迟。
- API Key 不得进入代码、日志和测试数据。
- 无网络单元测试与真实模型集成测试分开执行。

## Git 工作流

- 不直接在 `main` 开发，使用 Issue → 分支 → 测试 → Commit → Push → PR → Merge → 同步 `main`。
- 分支名包含类型、Issue 编号和描述；提交使用 Conventional Commits。
- 精确暂存相关文件，不使用 `git add .`。
- Agent 实际执行 Commit、Push、Merge、部署或重要删除前，必须获得明确授权。
- 清理分支属于删除操作，仅在合并完成且用户授权后执行。

## 文档维护

- 每个 Issue 在同一 PR 中同步 `PROGRESS.md`。
- 用户可见变化更新 `CHANGELOG.md`；架构变化更新 `PROJECT_CONTEXT.md`。
- 文档描述稳定功能状态，避免记录“等待 Commit/PR/Merge”等合并后立即过时的瞬态信息。
- 保证文档、代码和 GitHub 状态一致。
