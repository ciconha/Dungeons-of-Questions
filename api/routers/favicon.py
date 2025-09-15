from fastapi import APIRouter, Response
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/favicon.ico", include_in_schema=False)
def favicon():

    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    ico_path = os.path.join(project_root, "assets", "ui", "favicon.ico")
    if os.path.exists(ico_path):
        return FileResponse(ico_path)
 
    return Response(status_code=204)
