from collections.abc import Iterator, Sequence

import pytest
from fastapi.testclient import TestClient

from apps.backend.app.api import requirements as requirements_api
from apps.backend.app.main import app
from apps.backend.app.providers.openai_compatible_requirement_quality import (
    OpenAICompatibleRequirementQualityProvider,
)
from apps.backend.app.providers.requirement_quality import (
    MockRequirementQualityProvider,
    RequirementQualityInvalidResponseError,
    RequirementQualityProviderError,
    RequirementQualityTimeoutError,
    RequirementQualityUpstreamError,
)
from apps.backend.app.schemas.requirement import (
    MAX_QUALITY_REQUIREMENTS,
    MAX_QUALITY_REQUEST_CHARACTERS,
    MAX_QUALITY_REQUIREMENT_CHARACTERS,
    RequirementItem,
    RequirementQualityIssue,
)


client = TestClient(app)


@pytest.fixture(autouse=True)
def force_mock_provider_in_api_tests(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[None]:
    """API 自动化测试默认固定使用 Mock，绝不读取开发者的真实模型配置。"""

    monkeypatch.setenv("REQUIREMENT_QUALITY_PROVIDER", "mock")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.example.com/v1")
    monkeypatch.setenv("LLM_MODEL", "example-model")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "30")
    monkeypatch.setenv("LLM_MAX_RETRIES", "2")
    monkeypatch.setenv("LLM_MAX_TOKENS", "2000")
    requirements_api.get_requirement_quality_provider.cache_clear()

    yield

    requirements_api.close_requirement_quality_provider()


class FailingRequirementQualityProvider:
    """测试替身：调用时抛出预设领域异常。"""

    def __init__(self, error: RequirementQualityProviderError) -> None:
        self._error = error

    def check_quality(
        self,
        requirements: Sequence[RequirementItem],
    ) -> list[RequirementQualityIssue]:
        raise self._error


def test_quality_check_success() -> None:
    """合法的结构化需求应返回 Mock Provider 的质量检测结果。"""

    response = client.post(
        "/api/v1/requirements/quality-check",
        json={
            "requirements": [
                {"sequence": 1, "content": "系统应尽快返回查询结果。"},
                {"sequence": 2, "content": "系统界面应当友好美观。"},
                {"sequence": 3, "content": "查询失败时应显示错误原因。"},
            ]
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "requirement_count": 3,
        "issue_count": 2,
        "issues": [
            {
                "issue_type": "ambiguity",
                "severity": "medium",
                "related_sequences": [1],
                "description": "需求包含模糊表达“尽快”，缺少明确边界。",
                "suggestion": "改为可以客观验证的数值、条件或时间范围。",
            },
            {
                "issue_type": "untestable",
                "severity": "medium",
                "related_sequences": [2],
                "description": "需求包含主观表达“美观、友好”，缺少可测试标准。",
                "suggestion": "补充可观察的验收条件、指标或操作步骤。",
            },
        ],
    }


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
        {"requirements": [{"sequence": [1], "content": "一条需求"}]},
        {
            "requirements": [
                {"sequence": index, "content": "一条需求"}
                for index in range(1, MAX_QUALITY_REQUIREMENTS + 2)
            ]
        },
        {
            "requirements": [
                {
                    "sequence": 1,
                    "content": "需" * (MAX_QUALITY_REQUIREMENT_CHARACTERS + 1),
                }
            ]
        },
        {
            "requirements": [
                {
                    "sequence": index,
                    "content": "需" * MAX_QUALITY_REQUIREMENT_CHARACTERS,
                }
                for index in range(
                    1,
                    MAX_QUALITY_REQUEST_CHARACTERS
                    // MAX_QUALITY_REQUIREMENT_CHARACTERS
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
        "wrong-field-type",
        "too-many-requirements",
        "requirement-content-too-long",
        "total-content-too-long",
    ],
)
def test_quality_check_rejects_invalid_input(request_body: dict[str, object]) -> None:
    """不符合请求 Schema 的 JSON 应由 FastAPI 统一返回 422。"""

    response = client.post(
        "/api/v1/requirements/quality-check",
        json=request_body,
    )

    assert response.status_code == 422


def test_provider_factory_uses_mock_by_default() -> None:
    """默认配置必须继续返回确定性的 Mock Provider。"""

    provider = requirements_api.get_requirement_quality_provider()

    assert isinstance(provider, MockRequirementQualityProvider)


def test_provider_factory_reuses_provider_instance() -> None:
    """同一进程应复用 Provider，避免每个请求重建 HTTP 连接池。"""

    first_provider = requirements_api.get_requirement_quality_provider()
    second_provider = requirements_api.get_requirement_quality_provider()

    assert first_provider is second_provider


def test_app_shutdown_clears_cached_provider() -> None:
    """应用关闭时应清理缓存 Provider，避免资源跨生命周期残留。"""

    with TestClient(app) as lifecycle_client:
        response = lifecycle_client.post(
            "/api/v1/requirements/quality-check",
            json={
                "requirements": [
                    {"sequence": 1, "content": "系统应返回查询结果。"}
                ]
            },
        )

        assert response.status_code == 200
        assert (
            requirements_api.get_requirement_quality_provider.cache_info().currsize
            == 1
        )

    assert (
        requirements_api.get_requirement_quality_provider.cache_info().currsize
        == 0
    )


def test_provider_factory_selects_openai_compatible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """合法真实模型配置应返回 OpenAI-compatible Provider。"""

    monkeypatch.setenv(
        "REQUIREMENT_QUALITY_PROVIDER",
        "openai_compatible",
    )
    monkeypatch.setenv("LLM_API_KEY", "not-a-real-secret")

    provider = requirements_api.get_requirement_quality_provider()

    assert isinstance(provider, OpenAICompatibleRequirementQualityProvider)


@pytest.mark.parametrize(
    "environment",
    [
        {"REQUIREMENT_QUALITY_PROVIDER": "unknown"},
        {
            "REQUIREMENT_QUALITY_PROVIDER": "openai_compatible",
            "LLM_API_KEY": "",
        },
        {"LLM_TIMEOUT_SECONDS": "0"},
    ],
    ids=["unknown-provider", "missing-api-key", "invalid-number"],
)
def test_quality_check_maps_configuration_errors_to_503(
    monkeypatch: pytest.MonkeyPatch,
    environment: dict[str, str],
) -> None:
    """配置不可用时应返回 503，且响应不能包含具体密钥。"""

    for variable_name, value in environment.items():
        monkeypatch.setenv(variable_name, value)

    response = client.post(
        "/api/v1/requirements/quality-check",
        json={
            "requirements": [
                {"sequence": 1, "content": "系统应返回查询结果。"}
            ]
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "需求质量检测服务配置不可用"
    }


@pytest.mark.parametrize(
    ("provider_error", "expected_status", "expected_detail"),
    [
        (
            RequirementQualityTimeoutError("SDK timeout detail"),
            504,
            "需求质量检测模型响应超时",
        ),
        (
            RequirementQualityUpstreamError("SDK upstream detail"),
            502,
            "需求质量检测模型服务不可用",
        ),
        (
            RequirementQualityInvalidResponseError("raw model content"),
            502,
            "需求质量检测模型返回了不可用内容",
        ),
    ],
    ids=["timeout", "upstream", "invalid-response"],
)
def test_quality_check_maps_provider_errors(
    provider_error: RequirementQualityProviderError,
    expected_status: int,
    expected_detail: str,
) -> None:
    """API 只返回稳定的公共错误，不泄露 SDK 或模型原始内容。"""

    app.dependency_overrides[
        requirements_api.get_requirement_quality_provider
    ] = lambda: FailingRequirementQualityProvider(provider_error)

    try:
        response = client.post(
            "/api/v1/requirements/quality-check",
            json={
                "requirements": [
                    {"sequence": 1, "content": "系统应返回查询结果。"}
                ]
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}


def test_real_provider_failure_never_falls_back_to_mock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """真实 Provider 失败时必须明确报错，不能把 Mock 结果伪装成 AI。"""

    mock_was_created = False
    failing_provider = FailingRequirementQualityProvider(
        RequirementQualityUpstreamError("upstream failed")
    )

    class ForbiddenMockProvider:
        def __init__(self) -> None:
            nonlocal mock_was_created
            mock_was_created = True

    monkeypatch.setenv(
        "REQUIREMENT_QUALITY_PROVIDER",
        "openai_compatible",
    )
    monkeypatch.setenv("LLM_API_KEY", "not-a-real-secret")
    monkeypatch.setattr(
        requirements_api,
        "MockRequirementQualityProvider",
        ForbiddenMockProvider,
    )
    monkeypatch.setattr(
        requirements_api,
        "OpenAICompatibleRequirementQualityProvider",
        lambda settings: failing_provider,
        raising=False,
    )

    response = client.post(
        "/api/v1/requirements/quality-check",
        json={
            "requirements": [
                {"sequence": 1, "content": "系统应返回查询结果。"}
            ]
        },
    )

    assert response.status_code == 502
    assert mock_was_created is False
