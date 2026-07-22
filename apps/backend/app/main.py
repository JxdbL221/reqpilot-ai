# 后端主入口：定义 FastAPI 应用、健康检查响应模型及健康检查路由
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel
from apps.backend.app.api.documents import router as documents_router
from apps.backend.app.api.requirements import router as requirements_router

# 健康检查响应模型，使用 Pydantic 验证返回结构
class HealthResponse(BaseModel):
    status: Literal["ok"]  # 状态固定为 "ok"
    service: str  # 服务名称，例如 "ReqPilot AI"


# 创建 FastAPI 应用并设置基础元数据（标题、描述、版本）
app = FastAPI(
    title="ReqPilot AI API",
    description="软件需求分析与测试用例生成及追踪平台后端接口",
    version="0.1.0",
)
app.include_router(requirements_router, prefix="/api/v1")
# 注册需求文档相关接口
app.include_router(documents_router)


# 健康检查接口，返回服务运行状态（用于负载均衡或运维检测）
@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="检查服务运行状态",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="ReqPilot AI",
    )