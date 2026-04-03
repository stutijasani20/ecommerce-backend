from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel


T = TypeVar("T")


class ErrorDetail(BaseModel):
    message: str
    code: str
    details: Optional[List[Any]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
