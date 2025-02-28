from logging import getLogger
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi.responses import (
    FileResponse,
    RedirectResponse,
)
from libcloud.storage.drivers.local import LocalStorageDriver
from libcloud.storage.types import ObjectDoesNotExistError
from sqlalchemy_file.storage import StorageManager
from src.core.config import settings
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy_file.stored_file import StoredFile

router = APIRouter()



def serve_local_file(file: StoredFile) -> FileResponse:
    """Handle local file serving"""
    return FileResponse(
        path=file.get_cdn_url() or "",
        media_type=file.content_type,
        filename=file.filename,
    )


def serve_streaming_file(file: StoredFile) -> StreamingResponse:
    """Handle streaming file serving"""
    return StreamingResponse(
        file.object.as_stream(),
        media_type=file.content_type,
        headers={"Content-Disposition": f"attachment;filename={file.filename}"},
    )


@router.get("/media/{id}", response_class=FileResponse)
def serve_media_files(id: UUID = Path(..., description="Unique identifier of the media file"),) -> Any:
    """Serve media files"""

    try:
        storage_path = (
            f"{settings.FILE_STORAGE_CONTAINER_NAME}/{id}"
        )
        file = StorageManager.get_file(storage_path)
        file_url = file.get_cdn_url()

        if file_url and isinstance(file.object.driver, LocalStorageDriver):
            # The file is stored on local storage; serve it directly from disk.
            return serve_local_file(file)
        elif file_url:
            # The file has a public URL and is not stored locally, so we redirect.
            return RedirectResponse(file_url)

        # No public URL, and the file is not in local storage; stream the file
        return serve_streaming_file(file)

    except ObjectDoesNotExistError as error:
        raise HTTPException(status_code=404, detail='Not Found') from error