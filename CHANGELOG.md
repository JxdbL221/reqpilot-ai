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
- 
- 添加 `POST /api/v1/documents/upload` TXT 需求文档上传与解析接口
- 添加 TXT 文件类型、大小、空内容和 UTF-8 编码校验
- 添加需求文档上传成功及异常场景自动化测试

### Changed

- 更新项目进度、当前阶段和 GitHub 工作流记录
- 将需求文档接口、响应模型和解析逻辑拆分为 API、Schema 和 Service 层