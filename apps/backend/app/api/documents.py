"""需求文档上传接口。"""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from apps.backend.app.schemas.document import DocumentUploadResponse
from apps.backend.app.services.document_parser import (
    MAX_FILE_SIZE,
    EmptyFileError,
    FileTooLargeError,
    InvalidEncodingError,
    MissingFilenameError,
    UnsupportedFileTypeError,
    parse_txt_document,
)


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="上传并解析 TXT 需求文档",
)
async def upload_txt_document(
    file: Annotated[
        UploadFile,
        File(description="UTF-8 编码且不超过 1 MB 的 TXT 需求文档"),
    ],
) -> DocumentUploadResponse:
    """接收 TXT 文件，在内存中完成校验和解析。"""

    try:
        # 多读取 1 字节，用于判断文件是否超过限制。
        raw_content = await file.read(MAX_FILE_SIZE + 1)

        parsed_document = parse_txt_document(
            filename=file.filename,
            raw_content=raw_content,
        )
    except MissingFilenameError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="上传文件缺少文件名",
        ) from exc
    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="只支持 .txt 格式的需求文档",
        ) from exc
    except FileTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="文件大小不能超过 1 MB",
        ) from exc
    except EmptyFileError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="上传文件不能为空",
        ) from exc
    except InvalidEncodingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TXT 文件必须使用 UTF-8 编码",
        ) from exc
    finally:
        await file.close()

    return DocumentUploadResponse(
        filename=parsed_document.filename,
        file_type=parsed_document.file_type,
        char_count=parsed_document.char_count,
        content=parsed_document.content,
    )