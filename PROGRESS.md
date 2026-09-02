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
  - 当前完整测试共 79 项并全部通过

## 正在进行

- 完成 Issue #14 的合并前代码审查和交付流程

## 下一步

- 完成 Issue #14 的代码审查和交付流程
- 根据 MVP 路线规划下一个独立功能 Issue
