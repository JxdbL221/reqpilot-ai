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

### Changed

- 更新项目进度、当前阶段和 GitHub 工作流记录
- 将需求文档接口、响应模型和解析逻辑拆分为 API、Schema 和 Service 层
