from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from apps.backend.app.schemas.requirement import RequirementItem


MAX_GENERATION_REQUIREMENTS = 100
MAX_GENERATION_REQUIREMENT_CHARACTERS = 5_000
MAX_GENERATION_REQUEST_CHARACTERS = 50_000


class TestCaseScenarioType(StrEnum):
    """测试用例覆盖的固定场景类型。"""

    NORMAL = "normal"
    EXCEPTION = "exception"
    BOUNDARY = "boundary"
    STATE = "state"


class TestCasePriority(StrEnum):
    """测试执行优先级，数字越小优先级越高。"""

    P0 = "p0"
    P1 = "p1"
    P2 = "p2"


class TestCaseStep(BaseModel):
    """一条可执行操作及其对应的预期结果。"""

    model_config = ConfigDict(extra="forbid")

    sequence: int = Field(ge=1, description="步骤序号")
    action: str = Field(min_length=1, max_length=2_000, description="执行动作")
    expected_result: str = Field(
        min_length=1,
        max_length=2_000,
        description="该步骤对应的预期结果",
    )

    @field_validator("action", "expected_result")
    @classmethod
    def validate_step_text_is_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("测试步骤和预期结果不能为空")
        return value


class TestCase(BaseModel):
    """可执行且能关联回来源需求的结构化测试用例。"""

    model_config = ConfigDict(extra="forbid")

    test_case_id: str = Field(
        pattern=r"^TC-\d{3,}$",
        description="请求内唯一的稳定测试用例编号",
    )
    title: str = Field(min_length=1, max_length=200, description="测试用例标题")
    scenario_type: TestCaseScenarioType = Field(description="测试场景类型")
    priority: TestCasePriority = Field(description="测试执行优先级")
    related_requirement_sequences: list[Annotated[int, Field(ge=1)]] = Field(
        min_length=1,
        description="来源需求序号，用于建立需求—测试追踪关系",
    )
    preconditions: list[str] = Field(
        max_length=20,
        description="执行测试前需要满足的条件；无条件时为空列表",
    )
    steps: list[TestCaseStep] = Field(
        min_length=1,
        max_length=50,
        description="测试步骤及每一步的预期结果",
    )

    @field_validator("title")
    @classmethod
    def validate_title_is_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("测试用例标题不能为空")
        return value

    @field_validator("preconditions")
    @classmethod
    def validate_preconditions_are_not_blank(cls, values: list[str]) -> list[str]:
        if any(not value.strip() for value in values):
            raise ValueError("前置条件不能是空白字符串")
        return values

    @model_validator(mode="after")
    def validate_traceability_and_step_sequences(self) -> Self:
        if len(self.related_requirement_sequences) != len(
            set(self.related_requirement_sequences)
        ):
            raise ValueError("关联需求序号不能重复")

        step_sequences = [step.sequence for step in self.steps]
        if step_sequences != list(range(1, len(self.steps) + 1)):
            raise ValueError("测试步骤序号必须从 1 开始连续递增")
        return self


class TestCaseGenerationRequest(BaseModel):
    """测试用例生成接口接收的结构化需求列表。"""

    requirements: list[RequirementItem] = Field(
        min_length=1,
        max_length=MAX_GENERATION_REQUIREMENTS,
        description="至少包含一条、序号不重复的结构化需求",
    )

    @model_validator(mode="after")
    def validate_requirements(self) -> Self:
        sequences = [requirement.sequence for requirement in self.requirements]
        if len(sequences) != len(set(sequences)):
            raise ValueError("需求序号不能重复")

        if any(
            len(requirement.content) > MAX_GENERATION_REQUIREMENT_CHARACTERS
            for requirement in self.requirements
        ):
            raise ValueError(
                "单条需求内容不能超过 "
                f"{MAX_GENERATION_REQUIREMENT_CHARACTERS} 个字符"
            )

        total_characters = sum(
            len(requirement.content) for requirement in self.requirements
        )
        if total_characters > MAX_GENERATION_REQUEST_CHARACTERS:
            raise ValueError(
                "单次生成的需求总字符数不能超过 "
                f"{MAX_GENERATION_REQUEST_CHARACTERS}"
            )
        return self


class TestCaseGenerationResponse(BaseModel):
    """测试用例生成接口返回的汇总结果。"""

    requirement_count: int = Field(ge=1, description="参与生成的需求数量")
    test_case_count: int = Field(ge=1, description="生成的测试用例数量")
    test_cases: list[TestCase] = Field(
        min_length=1,
        description="结构化测试用例列表",
    )
