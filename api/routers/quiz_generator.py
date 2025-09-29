from fastapi import APIRouter, HTTPException

router = APIRouter()


QUIZ_DB = {
    1: [
        {"question": "O que significa dizer que dois modelos de computação são equivalentes?", "options": ["A) Eles usam a mesma linguagem de programação.","B) Eles podem simular um ao outro.","C) Eles têm o mesmo número de estados."], "answer": "B) Eles podem simular um ao outro."},
        {"question": "O que é uma Máquina de Turing?", "options": ["A) Um modelo teórico de computação capaz de simular qualquer algoritmo.","B) Um computador mecânico criado no século XIX.","C) Um algoritmo específico para resolver equações matemáticas."], "answer": "A) Um modelo teórico de computação capaz de simular qualquer algoritmo."},
    ],
    2: [
        
    ],
    3: [
        
    ],
    4: [
        
    ],
    5: [
        
    ],
    6: [
        
    ],
}

@router.get("/quiz/{phase}", tags=["Quiz"])
def get_quiz(phase: int):
    if phase not in QUIZ_DB:
        raise HTTPException(status_code=404, detail="Fase não encontrada")
    return QUIZ_DB[phase]
