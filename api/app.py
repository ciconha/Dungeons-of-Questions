# api/app.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.routers.root            import router as root_router
from api.routers.health          import router as health_router
from api.routers.quiz_generator  import router as quiz_router
from api.routers.web_scraper     import router as scraper_router
from api.routers.favicon         import router as favicon_router
from api.routers.game_session    import router as game_router   # NOVO

app = FastAPI(
    title="RPG Quiz API",
    description="API para quiz estilo RPG e gerenciamento de partidas",
    version="1.0.0"
)

@app.get("/", tags=["Root"])
def read_root():
    return JSONResponse({"message": "API está rodando"})

# Rotas de infraestrutura
app.include_router(health_router,  prefix="")
app.include_router(favicon_router, prefix="")

# Rotas de quiz e scraping
app.include_router(quiz_router,    prefix="/api")
app.include_router(scraper_router, prefix="/api")

# Rotas de partida e pontuação
app.include_router(game_router,    prefix="/api")
