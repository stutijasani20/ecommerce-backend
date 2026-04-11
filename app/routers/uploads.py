from fastapi import APIRouter, Depends, UploadFile, File
from app.api import deps
from app.models.user import User
from app.services.cloudinary_service import upload_image

router = APIRouter()


@router.post("/image")
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_admin),
) -> dict:
    """
    Upload a product image to Cloudinary and return its URL. (Admin Only)
    Use the returned `url` as the `image_url` when creating or updating a product.
    """
    url = await upload_image(file, folder="products")
    return {"url": url}
