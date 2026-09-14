from collections.abc import Sequence

from apps.backend.app.providers.test_case_generation import (
    TestCaseGenerationInvalidResponseError,
    TestCaseGenerationProvider,
)
from apps.backend.app.schemas.requirement import RequirementItem
from apps.backend.app.schemas.test_case import TestCaseGenerationResponse


def generate_test_cases(
    requirements: Sequence[RequirementItem],
    provider: TestCaseGenerationProvider,
) -> TestCaseGenerationResponse:
    """调用 Provider，并校验支撑追踪矩阵所需的跨对象关系。"""

    test_cases = provider.generate_test_cases(requirements)
    if not test_cases:
        raise TestCaseGenerationInvalidResponseError("Provider 未返回测试用例")

    test_case_ids = [test_case.test_case_id for test_case in test_cases]
    if len(test_case_ids) != len(set(test_case_ids)):
        raise TestCaseGenerationInvalidResponseError("测试用例编号不能重复")

    requirement_sequences = {
        requirement.sequence for requirement in requirements
    }
    returned_sequences = {
        sequence
        for test_case in test_cases
        for sequence in test_case.related_requirement_sequences
    }
    if not returned_sequences.issubset(requirement_sequences):
        raise TestCaseGenerationInvalidResponseError(
            "测试用例关联了本次请求之外的需求"
        )
    if returned_sequences != requirement_sequences:
        raise TestCaseGenerationInvalidResponseError(
            "部分需求没有关联测试用例"
        )

    return TestCaseGenerationResponse(
        requirement_count=len(requirements),
        test_case_count=len(test_cases),
        test_cases=test_cases,
    )
