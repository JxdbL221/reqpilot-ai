"""TXT 需求文档上传接口测试。"""

from fastapi.testclient import TestClient

from apps.backend.app.main import app


client = TestClient(app)
UPLOAD_URL = "/api/v1/documents/upload"


def test_upload_txt_document_successfully() -> None:
    """正常的 UTF-8 TXT 文件应当上传并解析成功。"""

    content = "用户可以使用邮箱和密码登录系统。"
    files = {
        "file": (
            "login-requirements.txt",
            content.encode("utf-8"),
            "text/plain",
        )
    }

    response = client.post(UPLOAD_URL, files=files)

    assert response.status_code == 200
    assert response.json() == {
        "filename": "login-requirements.txt",
        "file_type": "txt",
        "char_count": len(content),
        "content": content,
    }


def test_reject_empty_txt_document() -> None:
    """空 TXT 文件应返回 HTTP 400。"""

    files = {
        "file": (
            "empty.txt",
            b"",
            "text/plain",
        )
    }

    response = client.post(UPLOAD_URL, files=files)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "上传文件不能为空",
    }


def test_reject_non_txt_document() -> None:
    """非 TXT 扩展名文件应返回 HTTP 415。"""

    files = {
        "file": (
            "requirements.pdf",
            b"fake pdf content",
            "application/pdf",
        )
    }

    response = client.post(UPLOAD_URL, files=files)

    assert response.status_code == 415
    assert response.json() == {
        "detail": "只支持 .txt 格式的需求文档",
    }


def test_reject_oversized_txt_document() -> None:
    """超过 1 MB 的 TXT 文件应返回 HTTP 413。"""

    oversized_content = b"a" * (1024 * 1024 + 1)
    files = {
        "file": (
            "large-requirements.txt",
            oversized_content,
            "text/plain",
        )
    }

    response = client.post(UPLOAD_URL, files=files)

    assert response.status_code == 413
    assert response.json() == {
        "detail": "文件大小不能超过 1 MB",
    }


def test_reject_non_utf8_txt_document() -> None:
    """无法按 UTF-8 解码的 TXT 文件应返回 HTTP 400。"""

    files = {
        "file": (
            "invalid-encoding.txt",
            b"\xff\xfe\xfa",
            "text/plain",
        )
    }

    response = client.post(UPLOAD_URL, files=files)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "TXT 文件必须使用 UTF-8 编码",
    }