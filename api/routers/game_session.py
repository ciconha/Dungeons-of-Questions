# api/routers/game_session.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

from api.db.mongo import mongo

router = APIRouter(tags=["Game"])

#
# 1) Schemas de Entrada/Saída
#

class LaunchInput(BaseModel):
    player: str = Field(..., description="Identificador único do jogador")

class LaunchResponse(BaseModel):
    session_id: str = Field(..., description="ID da sessão (UUID ou ObjectId em string)")
    xp: int         = Field(..., description="XP atual da sessão")
    max_xp: int     = Field(..., description="XP necessário para o próximo nível")

class ScoreInput(BaseModel):
    session_id: str  = Field(..., description="ID da sessão retornado por /launch")
    added_xp: int    = Field(..., ge=0, description="Quantidade de XP a adicionar")

class ScoreResponse(BaseModel):
    session_id: str  = Field(..., description="ID da sessão atualizada")
    new_xp: int      = Field(..., description="XP após a atualização")
    message: str     = Field(..., description="Mensagem de confirmação")


#
# 2) Endpoint: /launch
#

@router.post("/launch", response_model=LaunchResponse)
def launch_game(input: LaunchInput):
    """
    Cria uma nova sessão para o jogador ou retorna a sessão existente.
    """
    # 2.1) Tenta buscar sessão existente no Mongo
    find_res = mongo.find("sessions", {"player": input.player})
    if not find_res["success"]:
        raise HTTPException(status_code=500, detail=find_res["error"])

    if find_res["data"]:
        # Pega a primeira sessão encontrada
        sess = find_res["data"][0]
        return LaunchResponse(
            session_id=str(sess["_id"]),
            xp=sess.get("xp", 0),
            max_xp=sess.get("max_xp", 100),
        )

    # 2.2) Se não encontrou, cria nova sessão
    new_sess = {
        "player": input.player,
        "xp": 0,
        "max_xp": 100,
        "started_at": datetime.utcnow(),
    }
    ins_res = mongo.insert("sessions", new_sess)
    if not ins_res["success"]:
        raise HTTPException(status_code=500, detail=ins_res["error"])

    # ins_res["id"] pode ser ObjectId ou string
    new_id = ins_res["id"]
    return LaunchResponse(
        session_id=str(new_id),
        xp=0,
        max_xp=100,
    )


#
# 3) Endpoint: /score
#

@router.post("/score", response_model=ScoreResponse)
def submit_score(input: ScoreInput):
    """
    Recebe session_id e XP a adicionar, atualiza a sessão e retorna o novo XP.
    """
    # 3.1) Valida session_id como ObjectId
    try:
        oid = ObjectId(input.session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="session_id inválido")

    # 3.2) Busca sessão existente
    find_res = mongo.find("sessions", {"_id": oid})
    if not find_res["success"]:
        raise HTTPException(status_code=500, detail=find_res["error"])
    if not find_res["data"]:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    sess = find_res["data"][0]
    current_xp = sess.get("xp", 0)
    new_xp = current_xp + input.added_xp

    # 3.3) Atualiza documento no Mongo
    upd_res = mongo.update(
        "sessions",
        {"_id": oid},
        {
            "xp": new_xp,
            "last_updated": datetime.utcnow()
        }
    )
    if not upd_res["success"]:
        raise HTTPException(status_code=500, detail=upd_res["error"])

    return ScoreResponse(
        session_id=input.session_id,
        new_xp=new_xp,
        message="XP atualizado com sucesso"
    )
