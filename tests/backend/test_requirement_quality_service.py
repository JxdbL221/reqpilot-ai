from collections.abc import Sequence

from apps.backend.app.schemas.requirement import (
    RequirementIssueSeverity,
    RequirementIssueType,
    RequirementItem,
    RequirementQualityIssue,
)
from apps.backend.app.services.requirement_quality_checker import (
    check_requirement_quality,
)


class StubRequirementQualityProvider:
    """测试替身：返回预设结果，并记录 Service 传入的需求。"""

    def __init__(self, issues: list[RequirementQualityIssue]) -> None:
        self._issues = issues
        self.received_requirements: list[RequirementItem] | None = None

    def check_quality(
        self,
        requirements: Sequence[RequirementItem],
    ) -> list[RequirementQualityIssue]:
        self.received_requirements = list(requirements)
        return self._issues


def test_quality_service_calls_provider_and_builds_response() -> None:
    """Service 应调用注入的 Provider，并正确统计需求与问题数量。"""

    requirements = [
        RequirementItem(sequence=1, content="系统应尽快返回结果。"),
        RequirementItem(sequence=2, content="失败时显示错误原因。"),
    ]
    provider_issues = [
        RequirementQualityIssue(
            issue_type=RequirementIssueType.AMBIGUITY,
            severity=RequirementIssueSeverity.MEDIUM,
            related_sequences=[1],
            description="‘尽快’缺少明确标准。",
            suggestion="补充可测量的时间范围。",
        )
    ]
    provider = StubRequirementQualityProvider(provider_issues)

    response = check_requirement_quality(requirements, provider)

    assert provider.received_requirements == requirements
    assert response.requirement_count == 2
    assert response.issue_count == 1
    assert response.issues == provider_issues


def test_quality_service_supports_provider_with_no_issues() -> None:
    """Provider 没有发现问题时，Service 应返回空问题列表和零计数。"""

    requirements = [
        RequirementItem(sequence=1, content="请求失败时应在 2 秒内返回错误码。")
    ]
    provider = StubRequirementQualityProvider([])

    response = check_requirement_quality(requirements, provider)

    assert response.requirement_count == 1
    assert response.issue_count == 0
    assert response.issues == []
