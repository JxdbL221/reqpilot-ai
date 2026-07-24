from collections.abc import Sequence

from apps.backend.app.providers.requirement_quality import (
    RequirementQualityProvider,
)
from apps.backend.app.schemas.requirement import (
    RequirementItem,
    RequirementQualityCheckResponse,
)


def check_requirement_quality(
    requirements: Sequence[RequirementItem],
    provider: RequirementQualityProvider,
) -> RequirementQualityCheckResponse:
    """调用注入的 Provider，并将检测结果汇总为统一响应。"""

    issues = provider.check_quality(requirements)

    return RequirementQualityCheckResponse(
        requirement_count=len(requirements),
        issue_count=len(issues),
        issues=issues,
    )
