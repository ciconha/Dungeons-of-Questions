from pydantic import BaseModel
from typing import List

class QuizQuestion(BaseModel):
    pergunta: str
    alternativas: List[str]
    correta: int
