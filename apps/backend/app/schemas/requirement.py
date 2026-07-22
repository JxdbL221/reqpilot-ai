from pydantic import BaseModel, Field


class RequirementPreprocessRequest(BaseModel):
    """需求文本预处理请求。"""

    content: str = Field(description="待预处理的原始需求文本")


class RequirementItem(BaseModel):
    """预处理后的一条结构化需求。"""

    sequence: int = Field(ge=1, description="需求条目的连续序号")
    content: str = Field(description="清理后的需求内容")


class RequirementPreprocessResponse(BaseModel):
    """需求文本预处理响应。"""

    requirement_count: int = Field(ge=0, description="需求条目总数")
    requirements: list[RequirementItem] = Field(description="结构化需求条目列表")