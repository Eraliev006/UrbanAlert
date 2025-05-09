from pathlib import Path
from fastapi import HTTPException, UploadFile, status
import os

USER_AVATAR_DIR = Path("static/avatars")
COMPLAINT_IMAGE_DIR = Path("static/complaints")

USER_AVATAR_DIR.mkdir(parents=True, exist_ok=True)
COMPLAINT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

class ImageService:
    @staticmethod
    async def save_user_avatar_image(file: UploadFile, user_id: int) -> str:
        return await ImageService._save_image(file, f"user_{user_id}", USER_AVATAR_DIR)

    @staticmethod
    async def save_complaint_image(file: UploadFile, complaint_id: int) -> str:
        return await ImageService._save_image(file, f"complaint_{complaint_id}", COMPLAINT_IMAGE_DIR)

    @staticmethod
    async def _save_image(file: UploadFile, prefix: str, directory: Path) -> str:
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed"
            )

        ext = Path(file.filename).suffix
        filename = f"{prefix}{ext}"
        file_path = directory / filename

        if file_path.exists():
            os.remove(file_path)

        try:
            content = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(content)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while saving the image: {str(e)}"
            )

        image_url = f"/static/{directory.name}/{filename}"
        return image_url
