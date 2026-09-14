from collections.abc import Sequence

import pytest

from apps.backend.app.providers.test_case_generation import (
    TestCaseGenerationInvalidResponseError as InvalidGenerationResponseError,
)
from apps.backend.app.schemas.requirement import RequirementItem
from apps.backend.app.schemas.test_case import (
    TestCase as GeneratedCase,
    TestCasePriority as CasePriority,
    TestCaseScenarioType as ScenarioType,
    TestCaseStep as CaseStep,
)
from apps.backend.app.services.test_case_generator import generate_test_cases


class StubTestCaseGenerationProvider:
    """测试替身：返回预设用例并记录收到的需求。"""

    def __init__(self, test_cases: list[GeneratedCase]) -> None:
        self._test_cases = test_cases
        self.received_requirements: list[RequirementItem] | None = None

    def generate_test_cases(
        self,
        requirements: Sequence[RequirementItem],
    ) -> list[GeneratedCase]:
        self.received_requirements = list(requirements)
        return self._test_cases


def build_test_case(
    test_case_id: str = "TC-001",
    related_sequences: list[int] | None = None,
) -> GeneratedCase:
    return GeneratedCase(
        test_case_id=test_case_id,
        title="验证需求",
        scenario_type=ScenarioType.NORMAL,
        priority=CasePriority.P0,
        related_requirement_sequences=related_sequences or [1],
        preconditions=[],
        steps=[
            CaseStep(
                sequence=1,
                action="执行操作",
                expected_result="符合需求",
            )
        ],
    )


def test_generation_service_calls_provider_and_builds_summary() -> None:
    """Service 应调用 Provider，并返回正确的需求和用例计数。"""

    requirements = [RequirementItem(sequence=1, content="系统应返回结果。")]
    provider_cases = [build_test_case()]
    provider = StubTestCaseGenerationProvider(provider_cases)

    response = generate_test_cases(requirements, provider)

    assert provider.received_requirements == requirements
    assert response.requirement_count == 1
    assert response.test_case_count == 1
    assert response.test_cases == provider_cases


def test_generation_service_rejects_unknown_requirement_reference() -> None:
    """Provider 不得返回本次请求之外的需求关联。"""

    requirements = [RequirementItem(sequence=1, content="系统应返回结果。")]
    provider = StubTestCaseGenerationProvider(
        [build_test_case(related_sequences=[2])]
    )

    with pytest.raises(InvalidGenerationResponseError):
        generate_test_cases(requirements, provider)


def test_generation_service_rejects_duplicate_test_case_ids() -> None:
    """重复用例 ID 会破坏后续追踪，因此必须拒绝。"""

    requirements = [RequirementItem(sequence=1, content="系统应返回结果。")]
    provider = StubTestCaseGenerationProvider(
        [build_test_case(), build_test_case()]
    )

    with pytest.raises(InvalidGenerationResponseError):
        generate_test_cases(requirements, provider)


def test_generation_service_rejects_uncovered_requirement() -> None:
    """每条输入需求都必须至少被一条测试用例覆盖。"""

    requirements = [
        RequirementItem(sequence=1, content="系统应返回结果。"),
        RequirementItem(sequence=2, content="系统应记录日志。"),
    ]
    provider = StubTestCaseGenerationProvider([build_test_case()])

    with pytest.raises(InvalidGenerationResponseError):
        generate_test_cases(requirements, provider)
