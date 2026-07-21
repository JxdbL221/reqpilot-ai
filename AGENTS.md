# ReqPilot AI Agent Instructions

## 项目定位

ReqPilot AI 是基于大语言模型的软件需求分析、质量检测、测试用例生成与需求追踪平台。

项目同时用于本科毕业设计、AI 应用开发求职和软件工程训练。

## 开始任务前

1. 阅读 `PROJECT_CONTEXT.md`、`PROGRESS.md` 和相关 README。
2. 检查当前分支、`git status` 和最近提交。
3. 阅读当前 GitHub Issue 的任务内容和验收标准。
4. 不重复已经完成或合并的功能。
5. 如果文档、代码和 GitHub 状态不一致，先报告差异。

## 协作与教学

- 默认使用简体中文。
- 用户仍在学习 FastAPI、测试与 Git 工作流，先解释目的，再给出操作。
- 命令需要说明用途和预期结果。
- 新增代码添加适量中文注释，重点解释设计意图，不机械翻译每行语法。
- 每次只推进一个可验证的小步骤，明确说明验证结果。

## Git 工作流

- 不直接在 `main` 上开发。
- 使用 Issue → 分支 → 编码 → 测试 → Commit → Push → PR → Merge 流程。
- 分支名称包含类型、Issue 编号和简短描述。
- 使用 Conventional Commits。
- 精确暂存相关文件，不使用 `git add .`。
- 未经用户明确确认，不执行 Commit、Push、Merge、部署或重要删除操作。
- 保留用户已有改动，不修改无关文件。

## 代码规范

- 后端代码放在 `apps/backend/`。
- 前端代码放在 `apps/frontend/`。
- 测试代码放在 `tests/`。
- Python 使用类型标注。
- 文件路径优先使用 `pathlib`。
- 敏感配置使用环境变量和 `.env.example`。
- 新增依赖时同步更新对应 requirements 文件。
- 不修改 `datasets/` 中的原始数据。

## 验证要求

提交前至少执行与改动相关的测试。

后端基础验证命令：

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Git 格式检查命令：

```powershell
git diff --check
```

无法运行测试时，必须说明原因和建议的验证命令，不得虚构测试结果。

## 文档维护

- 每完成一个 Issue，在同一 PR 中更新 `PROGRESS.md`。
- 用户可见的功能变化同时更新 `CHANGELOG.md`。
- 架构或技术方案改变时更新 `PROJECT_CONTEXT.md`。
- 保证文档记录、代码状态和 GitHub 状态一致。
