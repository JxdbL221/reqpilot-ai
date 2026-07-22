from apps.backend.app.schemas.requirement import RequirementItem


class EmptyRequirementTextError(ValueError):
    """需求文本经过清理后没有有效内容。"""


def preprocess_requirements(content: str) -> list[RequirementItem]:
    """清理原始需求文本，并按非空行生成结构化需求条目。"""

    # 统一 Windows、Linux 和旧式 Mac 的换行符
    normalized_content = content.replace("\r\n", "\n").replace("\r", "\n")

    # 清理每行首尾空白，并过滤空行
    cleaned_lines = [
        line.strip()
        for line in normalized_content.split("\n")
        if line.strip()
    ]

    if not cleaned_lines:
        raise EmptyRequirementTextError("需求文本不能为空")

    return [
        RequirementItem(sequence=index, content=line)
        for index, line in enumerate(cleaned_lines, start=1)
    ]

# 统一不同系统的换行符；
# 去除每行首尾空白；
# 过滤空行；
# 生成从 1 开始的连续序号；
# 拒绝全空白文本。