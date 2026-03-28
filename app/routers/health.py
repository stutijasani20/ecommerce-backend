from fastapi import APIRouter

router = APIRouter()


@router.get("/health", status_code=200)
def health_check():
    """
    Check if the service is alive and healthy.
    """
    return {"status": "ok"}
