import pytest

from apps.backend.app.config import (
    RequirementQualityConfigurationError,
    RequirementQualityProviderName,
    load_requirement_quality_settings,
)


def test_requirement_quality_settings_use_safe_mock_defaults() -> None:
    """未配置环境变量时，应使用无需 API Key 的 Mock Provider。"""

    settings = load_requirement_quality_settings({})

    assert settings.provider is RequirementQualityProviderName.MOCK
    assert settings.api_key is None
    assert settings.base_url == "https://api.deepseek.com"
    assert settings.model == "deepseek-v4-flash"
    assert settings.timeout_seconds == 30
    assert settings.max_retries == 2
    assert settings.max_tokens == 2000


def test_requirement_quality_settings_accept_openai_compatible_values() -> None:
    """合法环境变量应被转换为真实 Provider 所需的强类型配置。"""

    settings = load_requirement_quality_settings(
        {
            "REQUIREMENT_QUALITY_PROVIDER": "openai_compatible",
            "LLM_API_KEY": "test-api-key",
            "LLM_BASE_URL": "https://llm.example.com/v1",
            "LLM_MODEL": "example-model",
            "LLM_TIMEOUT_SECONDS": "45",
            "LLM_MAX_RETRIES": "0",
            "LLM_MAX_TOKENS": "1500",
        }
    )

    assert settings.provider is RequirementQualityProviderName.OPENAI_COMPATIBLE
    assert settings.api_key == "test-api-key"
    assert settings.base_url == "https://llm.example.com/v1"
    assert settings.model == "example-model"
    assert settings.timeout_seconds == 45
    assert settings.max_retries == 0
    assert settings.max_tokens == 1500


def test_openai_compatible_settings_require_api_key() -> None:
    """启用真实 Provider 却没有密钥时，应在发起网络请求前拒绝配置。"""

    with pytest.raises(
        RequirementQualityConfigurationError,
        match="LLM_API_KEY",
    ):
        load_requirement_quality_settings(
            {"REQUIREMENT_QUALITY_PROVIDER": "openai_compatible"}
        )


def test_requirement_quality_settings_reject_unknown_provider() -> None:
    """拼错 Provider 名称时应明确报错，不能悄悄退回 Mock。"""

    with pytest.raises(
        RequirementQualityConfigurationError,
        match="REQUIREMENT_QUALITY_PROVIDER",
    ):
        load_requirement_quality_settings(
            {"REQUIREMENT_QUALITY_PROVIDER": "unknown"}
        )


@pytest.mark.parametrize("variable_name", ["LLM_BASE_URL", "LLM_MODEL"])
def test_requirement_quality_settings_reject_blank_text(
    variable_name: str,
) -> None:
    """模型地址和名称不能是空白，否则真实调用一定无法成功。"""

    with pytest.raises(
        RequirementQualityConfigurationError,
        match=variable_name,
    ):
        load_requirement_quality_settings({variable_name: "   "})


@pytest.mark.parametrize(
    "base_url",
    ["not-a-url", "ftp://llm.example.com", "https:///missing-host"],
)
def test_requirement_quality_settings_reject_invalid_base_url(
    base_url: str,
) -> None:
    """模型地址必须包含受支持的协议和主机名。"""

    with pytest.raises(
        RequirementQualityConfigurationError,
        match="LLM_BASE_URL",
    ):
        load_requirement_quality_settings({"LLM_BASE_URL": base_url})


@pytest.mark.parametrize(
    ("variable_name", "value"),
    [
        ("LLM_TIMEOUT_SECONDS", "0"),
        ("LLM_MAX_RETRIES", "-1"),
        ("LLM_MAX_TOKENS", "not-an-integer"),
    ],
)
def test_requirement_quality_settings_reject_invalid_numbers(
    variable_name: str,
    value: str,
) -> None:
    """数值配置必须满足边界，避免把明显错误传给模型 SDK。"""

    with pytest.raises(
        RequirementQualityConfigurationError,
        match=variable_name,
    ):
        load_requirement_quality_settings({variable_name: value})
