# api/routers/quiz_generator.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from api.db.mongo import mongo

router = APIRouter(tags=["Quiz"])

class Question(BaseModel):
    """
    Modelo de resposta para uma pergunta já persistida.
    """
    id: str = Field(..., alias="_id")
    phase: int
    question: str
    options: List[str]
    answer: str

class QuestionCreate(BaseModel):
    """
    Modelo de requisição para criar uma nova pergunta.
    """
    phase: int
    question: str
    options: List[str]
    answer: str

@router.get(
    "/quiz/{phase}",
    response_model=List[Question],
    summary="Buscar perguntas de uma fase",
    description="Retorna todas as questões cadastradas para a fase indicada"
)
def get_quiz(phase: int):
    res = mongo.find("quiz", {"phase": phase})
    if not res["success"]:
        raise HTTPException(status_code=500, detail=res["error"])
    # Se não houver nenhum documento para essa fase, devolve lista vazia
    return res["data"]

@router.post(
    "/quiz",
    response_model=Question,
    status_code=201,
    summary="Criar nova pergunta",
    description="Insere uma nova questão no banco e retorna o registro criado"
)
def create_question(q: QuestionCreate):
    payload = q.dict()
    # use_uuid=True faz _id = uuid4().hex
    ins = mongo.insert("quiz", payload, use_uuid=True)
    if not ins["success"]:
        raise HTTPException(status_code=500, detail=ins["error"])
    # Anexa o _id retornado ao payload para enviar como resposta
    payload["_id"] = ins["id"]
    return payload
