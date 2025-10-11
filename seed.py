# seed.py

from api.db.mongo import mongo

def run():
    quizzes = [
        {
            "phase": 1,
            "question": "O que significa dizer que dois modelos de computação são equivalentes?",
            "options": [
                "A) Eles usam a mesma linguagem de programação.",
                "B) Eles podem simular um ao outro.",
                "C) Eles têm o mesmo número de estados."
            ],
            "answer": "B) Eles podem simular um ao outro."
        },
        {
            "phase": 1,
            "question": "O que é uma Máquina de Turing?",
            "options": [
                "A) Um modelo teórico de computação capaz de simular qualquer algoritmo.",
                "B) Um computador mecânico criado no século XIX.",
                "C) Um algoritmo específico para resolver equações matemáticas."
            ],
            "answer": "A) Um modelo teórico de computação capaz de simular qualquer algoritmo."
        },
        # …
    ]

    print("🔄 Seed: conectando ao MongoDB…")
    if not mongo.connect():
        print("❌ Seed abortado: falha na conexão.")
        return

    print("🗑 Seed: limpando coleção 'quiz'…")
    mongo.db["quiz"].delete_many({})

    for q in quizzes:
        print("➕ Seed: inserindo:", q["question"])
        res = mongo.insert("quiz", q, use_uuid=True)
        if not res.get("success"):
            print("❌ Seed: erro ao inserir:", res.get("error"))

    mongo.disconnect()
    print("✅ Seed finalizado.")
