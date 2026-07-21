"""需求文档接口使用的 Pydantic 数据模型。"""

# 从 typing 导入 Literal，用于限定字段为特定字面量值
from typing import Literal

# 从 pydantic 导入 BaseModel，作为数据模型基类
from pydantic import BaseModel


# 定义上传响应的数据模型，继承自 Pydantic 的 BaseModel
class DocumentUploadResponse(BaseModel):
    """TXT 需求文档上传成功后的结构化响应。"""

    filename: str
    # 文件类型，这里限定为字面量 'txt'，便于前端/后端校验
    file_type: Literal["txt"]
    # 文本总字符数，整型，用于快速统计和显示
    char_count: int
    # 上传后保存或返回的文档文本内容
    content: str