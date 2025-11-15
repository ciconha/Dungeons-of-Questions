# api/app.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.db.mongo import mongo
from api.routers.root           import router as root_router
from api.routers.health         import router as health_router
from api.routers.quiz import router as quiz_router
from api.routers.web_scraper    import router as scraper_router
from api.routers.favicon        import router as favicon_router
from api.routers.game_session   import router as game_router
from api.routers.game_session import router as game_router

app = FastAPI(
    title="RPG Quiz API",
    description="API para quiz estilo RPG e gerenciamento de partidas",
    version="1.0.0"
)

@app.on_event("startup")
def startup_db():
    mongo.connect()

@app.on_event("shutdown")
def shutdown_db():
    mongo.disconnect()

@app.get("/", tags=["Root"])
def read_root():
    return JSONResponse({"message": "API está rodando"})

# infraestrutura
app.include_router(health_router,   prefix="")
app.include_router(favicon_router,  prefix="")

# quiz e scraping
app.include_router(quiz_router,    prefix="/api")
app.include_router(scraper_router, prefix="/api")

# sessões de jogo (salvar XP, etc)
app.include_router(game_router,    prefix="/api")

app.include_router(game_router, prefix="/api")
