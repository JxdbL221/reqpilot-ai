import pytest
from pydantic import ValidationError

from apps.backend.app.schemas.test_case import (
    TestCase as GeneratedCase,
    TestCaseGenerationRequest as GenerationRequest,
    TestCasePriority as CasePriority,
    TestCaseScenarioType as ScenarioType,
    TestCaseStep as CaseStep,
)


def test_test_case_accepts_structured_traceable_case() -> None:
    """测试用例应保存场景、步骤和来源需求之间的显式关系。"""

    test_case = GeneratedCase(
        test_case_id="TC-001",
        title="验证用户成功登录",
        scenario_type=ScenarioType.NORMAL,
        priority=CasePriority.P0,
        related_requirement_sequences=[1],
        preconditions=["用户账号已注册"],
        steps=[
            CaseStep(
                sequence=1,
                action="输入正确账号和密码并提交",
                expected_result="系统进入首页",
            )
        ],
    )

    assert test_case.test_case_id == "TC-001"
    assert test_case.related_requirement_sequences == [1]


@pytest.mark.parametrize(
    "invalid_case",
    [
        {"test_case_id": "1", "related_requirement_sequences": [1]},
        {"test_case_id": "TC-001", "related_requirement_sequences": []},
        {"test_case_id": "TC-001", "related_requirement_sequences": [1, 1]},
    ],
    ids=["invalid-id", "missing-traceability", "duplicate-traceability"],
)
def test_test_case_rejects_invalid_identity_or_traceability(
    invalid_case: dict[str, object],
) -> None:
    """用例 ID 和需求关联必须能支撑后续追踪矩阵。"""

    with pytest.raises(ValidationError):
        GeneratedCase(
            title="合法标题",
            scenario_type=ScenarioType.NORMAL,
            priority=CasePriority.P1,
            preconditions=[],
            steps=[
                CaseStep(
                    sequence=1,
                    action="执行操作",
                    expected_result="得到结果",
                )
            ],
            **invalid_case,
        )


def test_generation_request_rejects_duplicate_requirement_sequences() -> None:
    """同一次生成不能包含重复需求序号。"""

    with pytest.raises(ValidationError):
        GenerationRequest(
            requirements=[
                {"sequence": 1, "content": "第一条需求"},
                {"sequence": 1, "content": "另一条需求"},
            ]
        )
