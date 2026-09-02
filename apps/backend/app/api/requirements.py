from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status  # 导入 FastAPI 的路由、依赖注入、异常和状态码工具

from apps.backend.app.config import (
    RequirementQualityConfigurationError,
    RequirementQualityProviderName,
    load_requirement_quality_settings,
)
from apps.backend.app.providers.openai_compatible_requirement_quality import (
    OpenAICompatibleRequirementQualityProvider,
)
from apps.backend.app.providers.requirement_quality import (
    MockRequirementQualityProvider,
    RequirementQualityInvalidResponseError,
    RequirementQualityProvider,
    RequirementQualityTimeoutError,
    RequirementQualityUpstreamError,
)

from apps.backend.app.schemas.requirement import (
    RequirementPreprocessRequest,
    RequirementPreprocessResponse,
    RequirementQualityCheckRequest,
    RequirementQualityCheckResponse,
)
from apps.backend.app.services.requirement_quality_checker import (
    check_requirement_quality,
)
from apps.backend.app.services.requirement_preprocessor import (  # 从 Service 层导入预处理函数与自定义异常
    EmptyRequirementTextError,  # 自定义异常：当请求中没有需求文本时抛出
    preprocess_requirements,  # 业务函数：将原始文本预处理并返回需求条目列表
)

router = APIRouter(prefix="/requirements", tags=["requirements"])  # 创建路由器实例，所有路由以 /requirements 为前缀


@lru_cache(maxsize=1)
def get_requirement_quality_provider() -> RequirementQualityProvider:
    """根据环境配置提供 Mock 或真实 LLM 质量检测实现。"""

    try:
        settings = load_requirement_quality_settings()
    except RequirementQualityConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="需求质量检测服务配置不可用",
        ) from exc

    if settings.provider is RequirementQualityProviderName.MOCK:
        return MockRequirementQualityProvider()

    return OpenAICompatibleRequirementQualityProvider(settings)


def close_requirement_quality_provider() -> None:
    """在应用关闭时释放缓存 Provider 持有的外部资源。"""

    if get_requirement_quality_provider.cache_info().currsize == 0:
        return

    provider = get_requirement_quality_provider()
    close = getattr(provider, "close", None)
    if callable(close):
        close()
    get_requirement_quality_provider.cache_clear()


# 定义 POST /requirements/preprocess 路由，用于对需求文本进行预处理
@router.post(  # 路由装饰器：注册 POST 方法的端点
    "/preprocess",  # 路径：/requirements/preprocess
    response_model=RequirementPreprocessResponse,  # 指定返回的 Pydantic 模型用于自动校验与文档
    status_code=status.HTTP_200_OK,  # 成功返回的 HTTP 状态码
)
def preprocess_requirement_text(  # 视图函数：处理预处理请求
    request: RequirementPreprocessRequest,  # 参数：请求体，会被 FastAPI 自动解析为 Pydantic 模型
) -> RequirementPreprocessResponse:
    """清理需求文本，并返回按行生成的结构化需求条目。"""

    try:  # 调用 Service 层函数并捕获业务异常
        requirements = preprocess_requirements(request.content)  # 将请求中的 content 字段交给预处理器，得到需求列表
    except EmptyRequirementTextError as exc:  # 如果输入为空文本，Service 层会抛出此异常
        raise HTTPException(  # 将业务异常转换为 HTTPException，从而返回 400 给客户端
            status_code=status.HTTP_400_BAD_REQUEST,  # HTTP 400 表示客户端请求不合法
            detail=str(exc),  # 将异常信息作为 detail 返回，便于前端显示错误原因
        ) from exc

    return RequirementPreprocessResponse(  # 构造并返回响应模型实例
        requirement_count=len(requirements),  # 响应中包含生成的需求条目数量
        requirements=requirements,  # 响应中包含具体的需求条目列表
    )  # 返回结束

# 预处理接口职责：
# 接收并校验 JSON 请求体；
# 调用 Service 层处理文本；
# 将业务异常转换为 HTTP 400；
# 构造符合 Schema 的响应。


@router.post(
    "/quality-check",
    response_model=RequirementQualityCheckResponse,
    status_code=status.HTTP_200_OK,
)
def quality_check_requirements(
    request: RequirementQualityCheckRequest,
    provider: Annotated[
        RequirementQualityProvider,
        Depends(get_requirement_quality_provider),
    ],
) -> RequirementQualityCheckResponse:
    """检测结构化需求的质量问题并返回统一报告。"""

    try:
        return check_requirement_quality(request.requirements, provider)
    except RequirementQualityTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="需求质量检测模型响应超时",
        ) from exc
    except RequirementQualityUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="需求质量检测模型服务不可用",
        ) from exc
    except RequirementQualityInvalidResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="需求质量检测模型返回了不可用内容",
        ) from exc
