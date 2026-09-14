# Changelog

本文件记录 ReqPilot AI 的主要版本变化。

## [Unreleased]

### Added

- 初始化项目目录结构
- 添加项目上下文和进度记录
- 添加环境变量示例文件
- 初始化 FastAPI 后端应用及基础 API 元数据
- 添加 `GET /api/v1/health` 健康检查接口
- 添加健康检查响应模型和自动化测试
- 添加 FastAPI、Uvicorn、pytest 和 httpx 依赖配置
- 添加项目级 `AGENTS.md` 协作规范

- 添加 `POST /api/v1/documents/upload` TXT 需求文档上传与解析接口
- 添加 TXT 文件类型、大小、空内容和 UTF-8 编码校验
- 添加需求文档上传成功及异常场景自动化测试

- 新增 `POST /api/v1/requirements/preprocess` 接口，可将原始需求文本清理并转换为结构化需求条目。
- 支持统一不同系统的换行符、过滤空行和清理每行首尾空白。
- 全空白需求文本返回 HTTP 400。

- 新增 `POST /api/v1/requirements/quality-check` 需求质量检测接口。
- 新增歧义、遗漏、冲突和不可测试四类结构化质量问题模型。
- 新增 Provider 协议、确定性 Mock Provider 和质量检测 Service。
- 新增空列表、空白内容、非法序号、重复序号和字段类型校验。
- 新增 Schema、Provider、Service 和 API 自动化测试。
- 新增 OpenAI-compatible 需求质量检测 Provider，可通过环境变量连接兼容模型服务。
- 新增真实模型配置加载与校验，覆盖 API Key、Base URL、模型、超时、重试和最大输出 Token。
- 新增模型 JSON 输出的 Pydantic Schema 校验与需求序号校验。
- 新增 Fake Client 离线测试，无需访问网络或消耗模型 Token。
- 新增质量检测请求数量与字符数上限，避免超大 Prompt 带来的成本和延迟风险。
- 新增模型响应完成状态、空白文本和关联序号语义校验。
- 新增 SDK Client 进程内复用及应用关闭清理。
- 新增 `POST /api/v1/test-cases/generate` 测试用例生成接口。
- 新增正常、异常、边界和状态四类测试场景及 `p0`、`p1`、`p2` 优先级。
- 新增可追踪的测试用例、测试步骤、Provider 协议、确定性 Mock Provider 和 Service。
- 新增测试用例编号、需求关联、步骤顺序和需求覆盖完整性校验。
- 新增测试用例生成的 Schema、Provider、Service 和 API 自动化测试。
- 新增 `pytest.ini`，将 pytest 自动收集范围限定在 `tests/` 目录。

### Changed

- 更新项目进度、当前阶段和 GitHub 工作流记录
- 将需求文档接口、响应模型和解析逻辑拆分为 API、Schema 和 Service 层
- 需求质量检测接口支持通过配置选择 Mock 或 OpenAI-compatible Provider，默认保持 Mock。
- 配置错误、模型超时及上游服务错误分别映射为 HTTP 503、504 和 502，且真实模型失败时不静默降级为 Mock。
- 后端新增 `openai==2.50.0` 依赖。
- 真实 Provider 将需求作为不可信 JSON 数据传入 Prompt，并明确禁止执行需求正文中的指令。
