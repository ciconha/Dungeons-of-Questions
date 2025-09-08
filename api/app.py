# api/app.py
from fastapi import FastAPI
from api.routers.quiz_generator import router as quiz_router
from api.routers.web_scraper import router as scraper_router

app = FastAPI()

app.include_router(quiz_router, prefix="/api")
app.include_router(scraper_router, prefix="/api")
