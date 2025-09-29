# api/routers/game_session.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Game"])

@router.post("/launch")
def launch_game():
    """
    Inicia uma nova partida/sessão.
    """
    # Aqui você poderia gerar um game_id, salvar em banco, etc.
    return {"message": "Partida iniciada com sucesso"}

class ScoreInput(BaseModel):
    player: str
    points: int

@router.post("/score")
def submit_score(score: ScoreInput):
    """
    Recebe e registra a pontuação de um jogador.
    """
    # Aqui você poderia validar, somar em leaderboard, etc.
    return {
        "message": "Pontuação registrada",
        "player": score.player,
        "points": score.points
    }
