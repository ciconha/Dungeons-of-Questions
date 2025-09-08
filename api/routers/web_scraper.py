# api/routers/web_scraper.py
from fastapi import APIRouter

router = APIRouter()

def fetch_mt_articles():
    urls = [
        "https://www.inf.ufsc.br/~j.barreto/trabaluno/MaqT01.pdf",
        "https://www.ufrgs.br/alanturingbrasil2012/Maquina_de_Turing.pdf"
    ]
    # Aqui você pode implementar a lógica real de scraping
    return ["Texto relevante sobre Máquina de Turing..."]

@router.get("/scrape")
def scrape():
    return {"artigos": fetch_mt_articles()}
