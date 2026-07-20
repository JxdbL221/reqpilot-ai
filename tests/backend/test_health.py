"""
测试模块：对后端服务的健康检查（/api/v1/health）进行单元测试。

说明：
- 使用 FastAPI 提供的 TestClient 来模拟 HTTP 请求。
- 验证响应状态码和返回的 JSON 内容是否符合预期。
"""

# 从 fastapi.testclient 导入 TestClient，用于在测试中模拟 HTTP 请求
from fastapi.testclient import TestClient

# 从应用中导入 FastAPI 的 app 实例（被测试的应用）
from apps.backend.app.main import app


# 使用 TestClient 包装 app，后续通过 client 发起请求进行断言
client = TestClient(app)


def test_health_check() -> None:
    """
    健康检查测试：
    1. 向 /api/v1/health 发送 GET 请求。
    2. 断言响应状态码为 200。
    3. 断言响应 JSON 包含预期的字段和值。
    """

    # 发起 GET 请求到健康检查端点
    response = client.get("/api/v1/health")

    # 断言返回的 HTTP 状态码为 200（OK）
    assert response.status_code == 200

    # 断言返回的 JSON 内容与预期一致
    assert response.json() == {
        "status": "ok",
        "service": "ReqPilot AI",
    }