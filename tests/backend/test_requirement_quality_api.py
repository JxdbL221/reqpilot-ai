import pytest
from fastapi.testclient import TestClient

from apps.backend.app.main import app


client = TestClient(app)


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
    ],
    ids=[
        "missing-requirements",
        "empty-requirements",
        "sequence-less-than-one",
        "blank-content",
        "duplicate-sequence",
        "wrong-field-type",
    ],
)
def test_quality_check_rejects_invalid_input(request_body: dict[str, object]) -> None:
    """不符合请求 Schema 的 JSON 应由 FastAPI 统一返回 422。"""

    response = client.post(
        "/api/v1/requirements/quality-check",
        json=request_body,
    )

    assert response.status_code == 422
