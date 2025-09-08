from fastapi import APIRouter
from api.services.quiz_service import generate_quiz

router = APIRouter()

@router.get("/quiz")
def get_quiz():
    return {"quiz": generate_quiz()}
