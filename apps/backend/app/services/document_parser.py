"""TXT 需求文档的校验和解析逻辑。"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


# 单个上传文件最大允许 1 MB。
MAX_FILE_SIZE = 1024 * 1024

@dataclass(frozen=True)
class ParsedTextDocument:
    """业务层解析完成后的 TXT 文档数据。"""

    filename: str
    file_type: Literal["txt"]
    char_count: int
    content: str


class DocumentParserError(ValueError):
    """需求文档解析异常的基类。"""


class MissingFilenameError(DocumentParserError):
    """上传文件缺少文件名。"""


class UnsupportedFileTypeError(DocumentParserError):
    """上传文件不是支持的 TXT 类型。"""


class FileTooLargeError(DocumentParserError):
    """上传文件超过大小限制。"""


class EmptyFileError(DocumentParserError):
    """上传文件没有有效文本。"""


class InvalidEncodingError(DocumentParserError):
    """上传文件无法使用 UTF-8 解码。"""


def parse_txt_document(
    filename: str | None,
    raw_content: bytes,
) -> ParsedTextDocument:
    """校验并解析 UTF-8 编码的 TXT 需求文档。

    文件只在内存中处理，不写入磁盘。
    """

    if filename is None or not filename.strip():
        raise MissingFilenameError

    # 仅保留文件名，避免路径穿越形式的文件名进入响应。
    safe_filename = Path(filename.replace("\\", "/")).name

    if Path(safe_filename).suffix.lower() != ".txt":
        raise UnsupportedFileTypeError

    if len(raw_content) > MAX_FILE_SIZE:
        raise FileTooLargeError

    if not raw_content:
        raise EmptyFileError

    try:
        content = raw_content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidEncodingError from exc

    # 只有空格、换行或制表符的文件也视为空文件。
    if not content.strip():
        raise EmptyFileError

    return ParsedTextDocument(
        filename=safe_filename,
        file_type="txt",
        char_count=len(content),
        content=content,
    )