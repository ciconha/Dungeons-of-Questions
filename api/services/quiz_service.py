from api.models.quiz_model import QuizQuestion
from api.utils.scraper_utils import fetch_mt_articles

def generate_quiz():
    texts = fetch_mt_articles()
    questions = []

    for text in texts:
        if "fita" in text and "estado" in text:
            question = QuizQuestion(
                pergunta="Qual é a função da fita em uma Máquina de Turing?",
                alternativas=[
                    "Armazenar dados e instruções",
                    "Controlar os estados da máquina",
                    "Executar operações matemáticas"
                ],
                correta=0
            )
            questions.append(question)

    return questions

