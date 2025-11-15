# api/routers/quiz_generator.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
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
    example: Optional[str] = None  # ← ADICIONADO campo example

class QuestionCreate(BaseModel):
    """
    Modelo de requisição para criar uma nova pergunta.
    """
    phase: int
    question: str
    options: List[str]
    answer: str
    example: Optional[str] = None  # ← ADICIONADO campo example

@router.get(
    "/quiz/{phase}",
    response_model=List[Question],
    summary="Buscar perguntas de uma fase",
    description="Retorna todas as questões cadastradas para a fase indicada"
)
def get_quiz(phase: int):
    # Busca TODOS os campos incluindo 'example'
    res = mongo.find("quiz", {"phase": phase})
    if not res["success"]:
        raise HTTPException(status_code=500, detail=res["error"])
    
    # Log para debug
    questions = res["data"]
    print(f"🔍 API: Retornando {len(questions)} perguntas para fase {phase}")
    if questions:
        first_question = questions[0]
        print(f"🔍 API: Primeira pergunta - {first_question.get('question', '')[:50]}...")
        print(f"🔍 API: Campos disponíveis: {list(first_question.keys())}")
        if 'example' in first_question:
            print(f"✅ API: Campo 'example' encontrado: {first_question['example'][:100]}...")
        else:
            print("❌ API: Campo 'example' NÃO encontrado!")
    
    return questions

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