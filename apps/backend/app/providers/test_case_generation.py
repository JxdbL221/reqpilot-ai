from collections.abc import Sequence
from typing import Protocol

from apps.backend.app.schemas.requirement import RequirementItem
from apps.backend.app.schemas.test_case import (
    TestCase,
    TestCasePriority,
    TestCaseScenarioType,
    TestCaseStep,
)


class TestCaseGenerationInvalidResponseError(RuntimeError):
    """Provider 返回的测试用例无法安全用于后续业务。"""


class TestCaseGenerationProvider(Protocol):
    """所有测试用例生成能力必须遵守的统一接口。"""

    def generate_test_cases(
        self,
        requirements: Sequence[RequirementItem],
    ) -> list[TestCase]:
        """根据结构化需求返回顺序稳定的测试用例。"""

        ...


class MockTestCaseGenerationProvider:
    """生成固定模板以验证流程，不承担真实语义分析。"""

    _SCENARIO_TEMPLATES = (
        (
            TestCaseScenarioType.NORMAL,
            TestCasePriority.P0,
            "正常场景",
            "在正常条件下执行需求描述的操作",
            "系统表现符合需求描述",
        ),
        (
            TestCaseScenarioType.EXCEPTION,
            TestCasePriority.P1,
            "异常场景",
            "模拟相关操作失败后执行需求描述的操作",
            "系统拒绝错误结果，并给出明确的失败反馈",
        ),
        (
            TestCaseScenarioType.BOUNDARY,
            TestCasePriority.P1,
            "边界场景",
            "使用允许范围边界附近的输入执行需求描述的操作",
            "系统按照明确的边界规则处理输入",
        ),
        (
            TestCaseScenarioType.STATE,
            TestCasePriority.P2,
            "状态场景",
            "在不同业务状态下执行需求描述的操作",
            "系统仅在允许的状态下完成操作",
        ),
    )

    def generate_test_cases(
        self,
        requirements: Sequence[RequirementItem],
    ) -> list[TestCase]:
        """为每条需求机械生成四类固定模板用例。"""

        test_cases: list[TestCase] = []

        for requirement in requirements:
            requirement_summary = requirement.content.strip()[:80]
            for scenario, priority, scenario_name, action, expected in (
                self._SCENARIO_TEMPLATES
            ):
                case_number = len(test_cases) + 1
                test_cases.append(
                    TestCase(
                        test_case_id=f"TC-{case_number:03d}",
                        title=(
                            f"{scenario_name}：需求 {requirement.sequence} - "
                            f"{requirement_summary}"
                        )[:200],
                        scenario_type=scenario,
                        priority=priority,
                        related_requirement_sequences=[requirement.sequence],
                        preconditions=[
                            f"已准备需求 {requirement.sequence} 对应的测试环境"
                        ],
                        steps=[
                            TestCaseStep(
                                sequence=1,
                                action=action,
                                expected_result=expected,
                            )
                        ],
                    )
                )

        return test_cases
