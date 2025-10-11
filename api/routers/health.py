from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return JSONResponse({"status": "ok"})
