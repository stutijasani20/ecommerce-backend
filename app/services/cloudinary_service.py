import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings


def _configure():
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


async def upload_image(file: UploadFile, folder: str = "products") -> str:
    """Upload an image to Cloudinary and return the secure URL."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: jpeg, png, webp, gif.",
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5 MB limit.",
        )

    _configure()

    try:
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type="image",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Cloudinary upload failed: {str(e)}",
        )

    return result["secure_url"]
