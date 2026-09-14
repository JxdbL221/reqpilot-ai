from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from apps.backend.app.providers.test_case_generation import (
    MockTestCaseGenerationProvider,
    TestCaseGenerationInvalidResponseError,
    TestCaseGenerationProvider,
)
from apps.backend.app.schemas.test_case import (
    TestCaseGenerationRequest,
    TestCaseGenerationResponse,
)
from apps.backend.app.services.test_case_generator import generate_test_cases


router = APIRouter(prefix="/test-cases", tags=["test-cases"])


def get_test_case_generation_provider() -> TestCaseGenerationProvider:
    """当前切片固定提供确定性 Mock，真实模型将在独立 Issue 接入。"""

    return MockTestCaseGenerationProvider()


@router.post(
    "/generate",
    response_model=TestCaseGenerationResponse,
    status_code=status.HTTP_200_OK,
)
def generate_requirement_test_cases(
    request: TestCaseGenerationRequest,
    provider: Annotated[
        TestCaseGenerationProvider,
        Depends(get_test_case_generation_provider),
    ],
) -> TestCaseGenerationResponse:
    """根据结构化需求生成可追踪的测试用例。"""

    try:
        return generate_test_cases(request.requirements, provider)
    except TestCaseGenerationInvalidResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="测试用例生成服务返回了不可用内容",
        ) from exc
