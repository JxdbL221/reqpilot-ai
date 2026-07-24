from collections.abc import Sequence
from typing import Protocol

from apps.backend.app.schemas.requirement import (
    RequirementIssueSeverity,
    RequirementIssueType,
    RequirementItem,
    RequirementQualityIssue,
)


class RequirementQualityProvider(Protocol):
    """需求质量检测能力必须遵守的统一接口。"""

    def check_quality(
        self,
        requirements: Sequence[RequirementItem],
    ) -> list[RequirementQualityIssue]:
        """检查结构化需求并返回顺序稳定的问题列表。"""

        ...


class MockRequirementQualityProvider:
    """使用固定关键词验证质量检测流程，不承担真实语义分析。"""

    _AMBIGUITY_TERMS = ("尽快", "适当", "大约", "通常")
    _UNTESTABLE_TERMS = ("美观", "友好", "高效")
    _ERROR_HANDLING_TERMS = ("失败", "异常", "错误")
    _GUEST_ALLOWED_TERM = "允许游客"
    _GUEST_FORBIDDEN_TERM = "禁止游客"

    def check_quality(
        self,
        requirements: Sequence[RequirementItem],
    ) -> list[RequirementQualityIssue]:
        """按照固定规则和固定顺序返回可重复的 Mock 结果。"""

        issues: list[RequirementQualityIssue] = []

        # 先按输入顺序处理单条需求，保证结果不会随运行次数变化。
        for requirement in requirements:
            ambiguity_terms = self._find_terms(
                requirement.content,
                self._AMBIGUITY_TERMS,
            )
            if ambiguity_terms:
                issues.append(
                    self._build_ambiguity_issue(requirement, ambiguity_terms)
                )

            untestable_terms = self._find_terms(
                requirement.content,
                self._UNTESTABLE_TERMS,
            )
            if untestable_terms:
                issues.append(
                    self._build_untestable_issue(requirement, untestable_terms)
                )

        conflict_issue = self._detect_guest_permission_conflict(requirements)
        if conflict_issue is not None:
            issues.append(conflict_issue)

        if not self._contains_error_handling(requirements):
            issues.append(
                RequirementQualityIssue(
                    issue_type=RequirementIssueType.OMISSION,
                    severity=RequirementIssueSeverity.HIGH,
                    related_sequences=[],
                    description="整组需求缺少失败、异常或错误处理说明。",
                    suggestion="补充关键操作失败时的系统行为和提示规则。",
                )
            )

        return issues

    @staticmethod
    def _find_terms(content: str, terms: Sequence[str]) -> list[str]:
        """按规则表中的固定顺序收集命中的关键词。"""

        return [term for term in terms if term in content]

    @staticmethod
    def _build_ambiguity_issue(
        requirement: RequirementItem,
        matched_terms: Sequence[str],
    ) -> RequirementQualityIssue:
        terms_text = "、".join(matched_terms)
        return RequirementQualityIssue(
            issue_type=RequirementIssueType.AMBIGUITY,
            severity=RequirementIssueSeverity.MEDIUM,
            related_sequences=[requirement.sequence],
            description=f"需求包含模糊表达“{terms_text}”，缺少明确边界。",
            suggestion="改为可以客观验证的数值、条件或时间范围。",
        )

    @staticmethod
    def _build_untestable_issue(
        requirement: RequirementItem,
        matched_terms: Sequence[str],
    ) -> RequirementQualityIssue:
        terms_text = "、".join(matched_terms)
        return RequirementQualityIssue(
            issue_type=RequirementIssueType.UNTESTABLE,
            severity=RequirementIssueSeverity.MEDIUM,
            related_sequences=[requirement.sequence],
            description=f"需求包含主观表达“{terms_text}”，缺少可测试标准。",
            suggestion="补充可观察的验收条件、指标或操作步骤。",
        )

    def _detect_guest_permission_conflict(
        self,
        requirements: Sequence[RequirementItem],
    ) -> RequirementQualityIssue | None:
        allowed_requirement: tuple[int, RequirementItem] | None = None
        forbidden_requirement: tuple[int, RequirementItem] | None = None

        for index, requirement in enumerate(requirements):
            if (
                allowed_requirement is None
                and self._GUEST_ALLOWED_TERM in requirement.content
            ):
                allowed_requirement = (index, requirement)
            if (
                forbidden_requirement is None
                and self._GUEST_FORBIDDEN_TERM in requirement.content
            ):
                forbidden_requirement = (index, requirement)

        if allowed_requirement is None or forbidden_requirement is None:
            return None

        if allowed_requirement[1].sequence == forbidden_requirement[1].sequence:
            return None

        # 关联序号保持原文出现顺序，而不是强制按数值大小排序。
        conflict_pair = sorted(
            (allowed_requirement, forbidden_requirement),
            key=lambda item: item[0],
        )
        related_sequences = [item[1].sequence for item in conflict_pair]

        return RequirementQualityIssue(
            issue_type=RequirementIssueType.CONFLICT,
            severity=RequirementIssueSeverity.HIGH,
            related_sequences=related_sequences,
            description="游客权限需求同时包含允许和禁止规则。",
            suggestion="明确游客权限边界，并删除或调整相互矛盾的规则。",
        )

    def _contains_error_handling(
        self,
        requirements: Sequence[RequirementItem],
    ) -> bool:
        return any(
            term in requirement.content
            for requirement in requirements
            for term in self._ERROR_HANDLING_TERMS
        )
