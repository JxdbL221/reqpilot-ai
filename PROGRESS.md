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
  - 当前完整测试共 30 项并全部通过

## 正在进行

- 规划真实 LLM Provider 的结构化输出、超时、重试和失败降级方案

## 下一步

- 为真实 LLM Provider 创建并细化独立 Issue
- 实现不影响现有 API 和 Service 的真实 Provider
- 分开维护无网络单元测试与真实模型集成测试
