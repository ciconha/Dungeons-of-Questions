from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["Root"])
def read_root():
    return {"message": "API is running"}
