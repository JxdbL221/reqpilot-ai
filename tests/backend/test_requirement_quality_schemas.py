import pytest
from pydantic import ValidationError

from apps.backend.app.schemas.requirement import (
    RequirementIssueSeverity,
    RequirementIssueType,
    RequirementQualityCheckRequest,
    RequirementQualityCheckResponse,
    RequirementQualityIssue,
)


def test_quality_check_models_accept_valid_data() -> None:
    """合法输入应能被转换为稳定、结构化的质量检测数据。"""

    request = RequirementQualityCheckRequest(
        requirements=[
            {"sequence": 1, "content": "系统应尽快返回查询结果。"},
            {"sequence": 2, "content": "系统界面应当友好美观。"},
        ]
    )
    issue = RequirementQualityIssue(
        issue_type=RequirementIssueType.AMBIGUITY,
        severity=RequirementIssueSeverity.MEDIUM,
        related_sequences=[1],
        description="‘尽快’没有明确的时间标准。",
        suggestion="补充可测量的响应时间。",
    )
    response = RequirementQualityCheckResponse(
        requirement_count=2,
        issue_count=1,
        issues=[issue],
    )

    assert request.requirements[0].sequence == 1
    assert response.issues[0].issue_type == RequirementIssueType.AMBIGUITY
    assert response.issue_count == 1


def test_quality_check_request_rejects_empty_requirements() -> None:
    """没有任何需求时不能启动质量检测。"""

    with pytest.raises(ValidationError):
        RequirementQualityCheckRequest(requirements=[])


def test_requirement_item_rejects_blank_content() -> None:
    """只有空白字符的内容不算一条有效需求。"""

    with pytest.raises(ValidationError):
        RequirementQualityCheckRequest(
            requirements=[{"sequence": 1, "content": "  \t  "}]
        )


def test_quality_check_request_rejects_duplicate_sequences() -> None:
    """同一次请求中的需求序号必须唯一。"""

    with pytest.raises(ValidationError):
        RequirementQualityCheckRequest(
            requirements=[
                {"sequence": 1, "content": "第一条需求"},
                {"sequence": 1, "content": "另一条需求"},
            ]
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("issue_type", "unknown"),
        ("severity", "urgent"),
    ],
)
def test_quality_issue_rejects_unknown_enum_values(
    field_name: str,
    invalid_value: str,
) -> None:
    """问题类型和严重程度只能使用协议中约定的枚举值。"""

    issue_data = {
        "issue_type": "ambiguity",
        "severity": "medium",
        "related_sequences": [],
        "description": "问题描述",
        "suggestion": "修改建议",
    }
    issue_data[field_name] = invalid_value

    with pytest.raises(ValidationError):
        RequirementQualityIssue(**issue_data)


def test_quality_issue_rejects_invalid_related_sequence() -> None:
    """关联序号可以为空，但列表中的每个序号必须从 1 开始。"""

    with pytest.raises(ValidationError):
        RequirementQualityIssue(
            issue_type="omission",
            severity="high",
            related_sequences=[0],
            description="缺少异常处理说明。",
            suggestion="补充异常处理需求。",
        )
