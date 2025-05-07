import uuid
from pathlib import Path

from fastapi import HTTPException
from starlette import status
from starlette.datastructures import UploadFile

AVATAR_DIR = Path("static/avatars")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

class ImageService:
    @staticmethod
    async def save_image(file: UploadFile, user_id: int) -> str:
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed"
            )

        ext = Path(file.filename).suffix
        filename = f"user_{user_id}_{uuid.uuid4()}{ext}"
        file_path = AVATAR_DIR / filename

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        avatar_url = f"/static/avatars/{filename}"
        return avatar_url

    @staticmethod
    def get_image_path(filename: str) -> Path:
        return AVATAR_DIR / filename