from pathlib import Path
from fastapi import HTTPException, UploadFile, status
import os
from logging import getLogger

logger = getLogger('fixkg.image_service')

USER_AVATAR_DIR = Path("static/avatars")
COMPLAINT_IMAGE_DIR = Path("static/complaints")

USER_AVATAR_DIR.mkdir(parents=True, exist_ok=True)
COMPLAINT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

class ImageService:
    @staticmethod
    async def save_user_avatar_image(file: UploadFile, user_id: int) -> str:
        logger.info("Attempting to save avatar for user %d", user_id)
        return await ImageService._save_image(file, f"user_{user_id}", USER_AVATAR_DIR)

    @staticmethod
    async def save_complaint_image(file: UploadFile, complaint_id: int) -> str:
        logger.info("Attempting to save image for complaint %d", complaint_id)
        return await ImageService._save_image(file, f"complaint_{complaint_id}", COMPLAINT_IMAGE_DIR)

    @staticmethod
    async def _save_image(file: UploadFile, prefix: str, directory: Path) -> str:
        if not file.content_type.startswith('image/'):
            logger.warning("Invalid file type for image upload: %s", file.content_type)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed"
            )

        ext = Path(file.filename).suffix
        filename = f"{prefix}{ext}"
        file_path = directory / filename

        if file_path.exists():
            os.remove(file_path)
            logger.info("Existing file %s removed", file_path)

        try:
            logger.info("Saving image %s to path %s", filename, file_path)
            content = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(content)

            logger.info("Image saved successfully to %s", file_path)
        except Exception as e:
            logger.error("Error occurred while saving image: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while saving the image: {str(e)}"
            )

        image_url = f"/static/{directory.name}/{filename}"
        logger.info("Image URL generated: %s", image_url)
        return image_url
