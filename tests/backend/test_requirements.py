from fastapi.testclient import TestClient

from apps.backend.app.main import app


client = TestClient(app)


def test_preprocess_requirements_success() -> None:
    """正常的多行需求文本应转换为结构化需求条目。"""

    response = client.post(
        "/api/v1/requirements/preprocess",
        json={
            "content": "用户可以登录系统。\n登录失败时应提示错误。"
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "requirement_count": 2,
        "requirements": [
            {
                "sequence": 1,
                "content": "用户可以登录系统。",
            },
            {
                "sequence": 2,
                "content": "登录失败时应提示错误。",
            },
        ],
    }


def test_preprocess_requirements_supports_mixed_line_endings() -> None:
    """Windows、Linux 和旧式 Mac 换行符都应被正确识别。"""

    response = client.post(
        "/api/v1/requirements/preprocess",
        json={
            "content": (
                "第一条需求\r\n"
                "第二条需求\r"
                "第三条需求\n"
                "第四条需求"
            )
        },
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["requirement_count"] == 4
    assert response_body["requirements"] == [
        {"sequence": 1, "content": "第一条需求"},
        {"sequence": 2, "content": "第二条需求"},
        {"sequence": 3, "content": "第三条需求"},
        {"sequence": 4, "content": "第四条需求"},
    ]


def test_preprocess_requirements_removes_blank_lines_and_spaces() -> None:
    """空行应被删除，每行首尾空白应被清理。"""

    response = client.post(
        "/api/v1/requirements/preprocess",
        json={
            "content": "\n  第一条需求  \n\n\t第二条需求\t\n"
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "requirement_count": 2,
        "requirements": [
            {"sequence": 1, "content": "第一条需求"},
            {"sequence": 2, "content": "第二条需求"},
        ],
    }


def test_preprocess_requirements_rejects_blank_content() -> None:
    """只包含空格、制表符和换行符的文本应返回 400。"""

    response = client.post(
        "/api/v1/requirements/preprocess",
        json={"content": "   \r\n\t\r   "},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "需求文本不能为空"
    }