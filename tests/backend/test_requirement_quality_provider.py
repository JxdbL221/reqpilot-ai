from apps.backend.app.providers.requirement_quality import (
    MockRequirementQualityProvider,
    RequirementQualityProvider,
)
from apps.backend.app.schemas.requirement import (
    RequirementIssueType,
    RequirementItem,
)


def test_mock_provider_follows_stable_issue_order() -> None:
    """Mock 结果应按单条问题、冲突、文档遗漏的固定顺序返回。"""

    requirements = [
        RequirementItem(sequence=1, content="系统应尽快返回，并保持界面美观。"),
        RequirementItem(sequence=2, content="系统允许游客查看首页。"),
        RequirementItem(sequence=3, content="系统禁止游客查看首页。"),
    ]

    issues = MockRequirementQualityProvider().check_quality(requirements)

    assert [issue.issue_type for issue in issues] == [
        RequirementIssueType.AMBIGUITY,
        RequirementIssueType.UNTESTABLE,
        RequirementIssueType.CONFLICT,
        RequirementIssueType.OMISSION,
    ]
    assert [issue.related_sequences for issue in issues] == [
        [1],
        [1],
        [2, 3],
        [],
    ]


def test_mock_provider_does_not_report_omission_when_error_handling_exists() -> None:
    """整组需求包含失败、异常或错误处理时，不应报告文档级遗漏。"""

    requirements = [
        RequirementItem(sequence=1, content="登录失败时，系统应显示错误原因。")
    ]

    issues = MockRequirementQualityProvider().check_quality(requirements)

    assert issues == []


def test_mock_provider_reports_conflict_for_guest_permission_example() -> None:
    """固定的游客允许/禁止示例应生成一条冲突问题。"""

    requirements = [
        RequirementItem(sequence=1, content="系统禁止游客查看订单。"),
        RequirementItem(sequence=2, content="系统允许游客查看订单。"),
        RequirementItem(sequence=3, content="访问失败时显示错误信息。"),
    ]

    issues = MockRequirementQualityProvider().check_quality(requirements)

    assert len(issues) == 1
    assert issues[0].issue_type == RequirementIssueType.CONFLICT
    assert issues[0].related_sequences == [1, 2]


def test_mock_provider_is_deterministic() -> None:
    """相同输入重复检测时，内容与顺序必须完全相同。"""

    requirements = [
        RequirementItem(sequence=1, content="系统通常应当高效完成处理。"),
    ]
    provider: RequirementQualityProvider = MockRequirementQualityProvider()

    first_result = provider.check_quality(requirements)
    second_result = provider.check_quality(requirements)

    assert first_result == second_result
