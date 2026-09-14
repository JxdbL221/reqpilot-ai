## 已完成

- FastAPI 后端基础结构与健康检查接口
- TXT 需求文档上传、校验与内存解析
- 需求文本预处理接口
  - 支持 `\r\n`、`\n` 和 `\r` 换行符
  - 清理每行首尾空白
  - 过滤空行
  - 将每个非空行转换为一条结构化需求
  - 生成从 1 开始的连续序号
  - 全空白文本返回 HTTP 400
  - 已添加自动化测试
- 需求质量检测模型与 Mock 接口
  - Issue #10 已通过 PR #11 合并
  - 新增 `POST /api/v1/requirements/quality-check`
  - 定义结构化请求、问题类型、严重程度和响应模型
  - 校验空列表、空白内容、非法序号、重复序号和错误字段类型
  - 定义独立的 `RequirementQualityProvider` 协议
  - 使用确定性 Mock 规则检测歧义、遗漏、冲突和不可测试问题
  - Service 通过依赖注入调用 Provider 并统计结果
  - 新增 Schema、Provider、Service 和 API 自动化测试
  - Mock 阶段完整测试共 30 项并全部通过
- OpenAI-compatible 真实 LLM Provider（Issue #14）
  - 新增环境变量配置加载与严格校验，默认继续使用 Mock
  - 新增 OpenAI-compatible Provider，可连接 DeepSeek 等兼容接口
  - 模型输出经过 JSON 解析、Pydantic Schema 校验和需求序号校验
  - 配置错误、超时、上游失败和非法输出具有明确的领域异常与 HTTP 映射
  - 真实模型失败时不静默降级为 Mock
  - 使用 Fake Client 完成无网络、无 Token 消耗的 Provider 自动化测试
  - 已手动验证真实 DeepSeek 成功调用返回 HTTP 200
  - 已手动验证无效但非空的 API Key 返回 HTTP 502，且未降级为 Mock
  - 为单次请求增加需求数量、单条内容和总字符数上限，控制模型成本与延迟
  - 复用 OpenAI Client，并在应用关闭时释放 HTTP 连接池
  - 将需求正文标记为不可信数据，拒绝执行其中的指令
  - 拒绝截断响应、SDK 解析异常、空白说明和非法关联序号
  - Issue #14 已通过 PR #15 合并
- 测试用例生成模型与 Mock 接口（Issue #16）
  - 新增 `POST /api/v1/test-cases/generate`
  - 定义正常、异常、边界和状态四类测试场景
  - 定义 `p0`、`p1`、`p2` 测试执行优先级
  - 测试用例包含稳定编号、标题、前置条件、步骤与逐步预期结果
  - 每条测试用例显式关联来源需求序号，为追踪矩阵提供数据基础
  - 定义独立的 `TestCaseGenerationProvider` 协议
  - 使用确定性 Mock 模板验证分层、接口和测试流程
  - Service 拒绝重复用例编号、非法需求关联和未覆盖需求
  - 新增 Schema、Provider、Service 和 API 自动化测试
  - 新增 pytest 收集配置，将自动化测试限定在 `tests/` 目录
  - 当前完整测试共 101 项并全部通过

## 正在进行

- 完成 Issue #16 的代码审查和交付流程

## 下一步

- 为测试用例生成接入 OpenAI-compatible 真实 LLM Provider
- 在后续独立 Issue 中实现人工审核和需求—测试追踪矩阵
