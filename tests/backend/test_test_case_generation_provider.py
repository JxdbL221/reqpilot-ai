from apps.backend.app.providers.test_case_generation import (
    MockTestCaseGenerationProvider,
)
from apps.backend.app.schemas.requirement import RequirementItem
from apps.backend.app.schemas.test_case import TestCaseScenarioType as ScenarioType


def test_mock_provider_generates_all_supported_scenarios_deterministically() -> None:
    """Mock 应以固定顺序覆盖四类场景，保证分层测试可重复。"""

    requirements = [
        RequirementItem(sequence=7, content="用户可以使用账号和密码登录。")
    ]
    provider = MockTestCaseGenerationProvider()

    first_result = provider.generate_test_cases(requirements)
    second_result = provider.generate_test_cases(requirements)

    assert first_result == second_result
    assert [case.scenario_type for case in first_result] == [
        ScenarioType.NORMAL,
        ScenarioType.EXCEPTION,
        ScenarioType.BOUNDARY,
        ScenarioType.STATE,
    ]
    assert [case.test_case_id for case in first_result] == [
        "TC-001",
        "TC-002",
        "TC-003",
        "TC-004",
    ]
    assert all(case.related_requirement_sequences == [7] for case in first_result)


def test_mock_provider_keeps_requirement_order_in_generated_cases() -> None:
    """多条需求的用例应按输入需求顺序生成，方便阅读和追踪。"""

    requirements = [
        RequirementItem(sequence=3, content="用户可以登录。"),
        RequirementItem(sequence=9, content="用户可以退出登录。"),
    ]

    cases = MockTestCaseGenerationProvider().generate_test_cases(requirements)

    assert len(cases) == 8
    assert [case.related_requirement_sequences for case in cases] == [
        [3],
        [3],
        [3],
        [3],
        [9],
        [9],
        [9],
        [9],
    ]
