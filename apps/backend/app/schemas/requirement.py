from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, Field, field_validator, model_validator


class RequirementPreprocessRequest(BaseModel):
    """需求文本预处理请求。"""

    content: str = Field(description="待预处理的原始需求文本")


class RequirementItem(BaseModel):
    """预处理后的一条结构化需求。"""

    sequence: int = Field(ge=1, description="需求条目的连续序号")
    content: str = Field(description="清理后的需求内容")

    @field_validator("content")
    @classmethod
    def validate_content_is_not_blank(cls, value: str) -> str:
        """拒绝只包含空格、制表符等空白字符的需求。"""

        if not value.strip():
            raise ValueError("需求内容不能为空")
        return value


class RequirementPreprocessResponse(BaseModel):
    """需求文本预处理响应。"""

    requirement_count: int = Field(ge=0, description="需求条目总数")
    requirements: list[RequirementItem] = Field(description="结构化需求条目列表")


class RequirementIssueType(StrEnum):
    """需求质量问题的固定分类。"""

    AMBIGUITY = "ambiguity"
    OMISSION = "omission"
    CONFLICT = "conflict"
    UNTESTABLE = "untestable"


class RequirementIssueSeverity(StrEnum):
    """需求质量问题的严重程度。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RequirementQualityCheckRequest(BaseModel):
    """质量检测接口接收的结构化需求列表。"""

    requirements: list[RequirementItem] = Field(
        min_length=1,
        description="至少包含一条、序号不重复的结构化需求",
    )

    @model_validator(mode="after")
    def validate_sequences_are_unique(self) -> Self:
        """同一次检测中的每条需求必须有唯一序号。"""

        sequences = [requirement.sequence for requirement in self.requirements]
        if len(sequences) != len(set(sequences)):
            raise ValueError("需求序号不能重复")
        return self


class RequirementQualityIssue(BaseModel):
    """质量检测发现的一条结构化问题。"""

    issue_type: RequirementIssueType = Field(description="问题类型")
    severity: RequirementIssueSeverity = Field(description="问题严重程度")
    related_sequences: list[Annotated[int, Field(ge=1)]] = Field(
        description="与问题相关的需求序号；文档级遗漏可以为空列表"
    )
    description: str = Field(min_length=1, description="问题说明")
    suggestion: str = Field(min_length=1, description="修改建议")


class RequirementQualityCheckResponse(BaseModel):
    """质量检测接口返回的汇总结果。"""

    requirement_count: int = Field(ge=0, description="参与检测的需求数量")
    issue_count: int = Field(ge=0, description="发现的质量问题数量")
    issues: list[RequirementQualityIssue] = Field(description="质量问题列表")
