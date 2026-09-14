from collections.abc import Sequence

import pytest
from fastapi.testclient import TestClient

from apps.backend.app.api import test_cases as test_cases_api
from apps.backend.app.main import app
from apps.backend.app.providers.test_case_generation import (
    MockTestCaseGenerationProvider,
    TestCaseGenerationInvalidResponseError as InvalidGenerationResponseError,
)
from apps.backend.app.schemas.requirement import RequirementItem
from apps.backend.app.schemas.test_case import (
    MAX_GENERATION_REQUIREMENTS,
    MAX_GENERATION_REQUEST_CHARACTERS,
    MAX_GENERATION_REQUIREMENT_CHARACTERS,
    TestCase as GeneratedCase,
)


client = TestClient(app)


def test_generate_test_cases_success() -> None:
    """合法需求应返回四类可追踪的确定性 Mock 用例。"""

    response = client.post(
        "/api/v1/test-cases/generate",
        json={
            "requirements": [
                {"sequence": 5, "content": "用户可以使用账号和密码登录。"}
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["requirement_count"] == 1
    assert body["test_case_count"] == 4
    assert [case["scenario_type"] for case in body["test_cases"]] == [
        "normal",
        "exception",
        "boundary",
        "state",
    ]
    assert all(
        case["related_requirement_sequences"] == [5]
        for case in body["test_cases"]
    )


@pytest.mark.parametrize(
    "request_body",
    [
        {},
        {"requirements": []},
        {"requirements": [{"sequence": 0, "content": "一条需求"}]},
        {"requirements": [{"sequence": 1, "content": "   \t"}]},
        {
            "requirements": [
                {"sequence": 1, "content": "第一条需求"},
                {"sequence": 1, "content": "另一条需求"},
            ]
        },
        {
            "requirements": [
                {"sequence": index, "content": "一条需求"}
                for index in range(1, MAX_GENERATION_REQUIREMENTS + 2)
            ]
        },
        {
            "requirements": [
                {
                    "sequence": 1,
                    "content": "需" * (MAX_GENERATION_REQUIREMENT_CHARACTERS + 1),
                }
            ]
        },
        {
            "requirements": [
                {
                    "sequence": index,
                    "content": "需" * MAX_GENERATION_REQUIREMENT_CHARACTERS,
                }
                for index in range(
                    1,
                    MAX_GENERATION_REQUEST_CHARACTERS
                    // MAX_GENERATION_REQUIREMENT_CHARACTERS
                    + 2,
                )
            ]
        },
    ],
    ids=[
        "missing-requirements",
        "empty-requirements",
        "sequence-less-than-one",
        "blank-content",
        "duplicate-sequence",
        "too-many-requirements",
        "requirement-content-too-long",
        "total-content-too-long",
    ],
)
def test_generate_test_cases_rejects_invalid_request(
    request_body: dict[str, object],
) -> None:
    """不符合生成约束的请求应由 Pydantic 返回 HTTP 422。"""

    response = client.post(
        "/api/v1/test-cases/generate",
        json=request_body,
    )

    assert response.status_code == 422


def test_test_case_provider_factory_returns_mock() -> None:
    """当前 Issue 的依赖工厂只提供明确标识的 Mock。"""

    provider = test_cases_api.get_test_case_generation_provider()

    assert isinstance(provider, MockTestCaseGenerationProvider)


class InvalidTestCaseGenerationProvider:
    """测试替身：模拟 Provider 产生无法追踪的输出。"""

    def generate_test_cases(
        self,
        requirements: Sequence[RequirementItem],
    ) -> list[GeneratedCase]:
        raise InvalidGenerationResponseError("private provider detail")


def test_generate_test_cases_maps_invalid_provider_output_to_502() -> None:
    """接口不能向调用者泄露 Provider 的内部错误细节。"""

    app.dependency_overrides[
        test_cases_api.get_test_case_generation_provider
    ] = InvalidTestCaseGenerationProvider

    try:
        response = client.post(
            "/api/v1/test-cases/generate",
            json={
                "requirements": [
                    {"sequence": 1, "content": "系统应返回结果。"}
                ]
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json() == {"detail": "测试用例生成服务返回了不可用内容"}
