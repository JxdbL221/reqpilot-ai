import os
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlparse


class RequirementQualityConfigurationError(ValueError):
    """需求质量检测配置不合法。"""


class RequirementQualityProviderName(StrEnum):
    """允许通过环境变量选择的需求质量检测 Provider。"""

    MOCK = "mock"
    OPENAI_COMPATIBLE = "openai_compatible"


@dataclass(frozen=True)
class RequirementQualitySettings:
    """经过类型转换和校验、可安全交给 Provider 使用的配置。"""

    provider: RequirementQualityProviderName
    api_key: str | None
    base_url: str
    model: str
    timeout_seconds: int
    max_retries: int
    max_tokens: int


def load_requirement_quality_settings(
    environment: Mapping[str, str] | None = None,
) -> RequirementQualitySettings:
    """从环境变量读取需求质量检测配置，并尽早拒绝非法值。"""

    source = os.environ if environment is None else environment
    provider = _read_provider_name(source)
    api_key = _read_optional_text(source, "LLM_API_KEY")

    if (
        provider is RequirementQualityProviderName.OPENAI_COMPATIBLE
        and api_key is None
    ):
        raise RequirementQualityConfigurationError(
            "使用 openai_compatible Provider 时必须配置 LLM_API_KEY"
        )

    return RequirementQualitySettings(
        provider=provider,
        api_key=api_key,
        base_url=_read_http_url(
            source,
            "LLM_BASE_URL",
            default="https://api.deepseek.com",
        ),
        model=_read_required_text(
            source,
            "LLM_MODEL",
            default="deepseek-v4-flash",
        ),
        timeout_seconds=_read_integer(
            source,
            "LLM_TIMEOUT_SECONDS",
            default=30,
            minimum=1,
        ),
        max_retries=_read_integer(
            source,
            "LLM_MAX_RETRIES",
            default=2,
            minimum=0,
        ),
        max_tokens=_read_integer(
            source,
            "LLM_MAX_TOKENS",
            default=2000,
            minimum=1,
        ),
    )


def _read_provider_name(
    environment: Mapping[str, str],
) -> RequirementQualityProviderName:
    raw_value = environment.get(
        "REQUIREMENT_QUALITY_PROVIDER",
        RequirementQualityProviderName.MOCK.value,
    ).strip()

    try:
        return RequirementQualityProviderName(raw_value)
    except ValueError as exc:
        raise RequirementQualityConfigurationError(
            "REQUIREMENT_QUALITY_PROVIDER 只支持 mock 或 openai_compatible"
        ) from exc


def _read_optional_text(
    environment: Mapping[str, str],
    variable_name: str,
) -> str | None:
    value = environment.get(variable_name)
    if value is None:
        return None

    stripped_value = value.strip()
    return stripped_value or None


def _read_required_text(
    environment: Mapping[str, str],
    variable_name: str,
    *,
    default: str,
) -> str:
    value = environment.get(variable_name, default).strip()
    if not value:
        raise RequirementQualityConfigurationError(
            f"{variable_name} 不能为空"
        )
    return value


def _read_http_url(
    environment: Mapping[str, str],
    variable_name: str,
    *,
    default: str,
) -> str:
    value = _read_required_text(
        environment,
        variable_name,
        default=default,
    )
    parsed_value = urlparse(value)

    if parsed_value.scheme not in {"http", "https"} or not parsed_value.netloc:
        raise RequirementQualityConfigurationError(
            f"{variable_name} 必须是合法的 HTTP 或 HTTPS 地址"
        )

    return value


def _read_integer(
    environment: Mapping[str, str],
    variable_name: str,
    *,
    default: int,
    minimum: int,
) -> int:
    raw_value = environment.get(variable_name, str(default)).strip()

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RequirementQualityConfigurationError(
            f"{variable_name} 必须是整数"
        ) from exc

    if value < minimum:
        raise RequirementQualityConfigurationError(
            f"{variable_name} 不能小于 {minimum}"
        )

    return value
