# seed.py

from api.db.mongo import mongo

def run():
    quizzes = [
        # Fase 1 – Introdução à Computabilidade
        {
            "phase": 1,
            "question": "O que significa dizer que dois modelos de computação são equivalentes?",
            "options": [
                "A) Eles usam a mesma linguagem de programação.",
                "B) Eles podem simular um ao outro.",
                "C) Eles têm o mesmo número de estados."
            ],
            "answer": "B) Eles podem simular um ao outro.",
            "example": "📚 EXEMPLO: Assim como um livro pode ser traduzido do português para o inglês sem perder o significado, uma Máquina de Turing pode simular um autômato finito e vice-versa. É como diferentes idiomas expressando a mesma ideia!"
        },
        {
            "phase": 1,
            "question": "O que é uma Máquina de Turing?",
            "options": [
                "A) Um modelo teórico de computação capaz de simular qualquer algoritmo.",
                "B) Um computador mecânico criado no século XIX.",
                "C) Um algoritmo específico para resolver equações matemáticas."
            ],
            "answer": "A) Um modelo teórico de computação capaz de simular qualquer algoritmo.",
            "example": "🎯 EXEMPLO: Imagine uma fita infinita onde você pode ler, escrever e mover símbolos seguindo regras simples. É como resolver um quebra-cabeça passo a passo - cada movimento segue instruções específicas!"
        },
        {
            "phase": 1,
            "question": "O que é uma Máquina Universal de Turing?",
            "options": [
                "A) Uma máquina que resolve apenas problemas aritméticos.",
                "B) Uma máquina capaz de simular qualquer outra Máquina de Turing.",
                "C) Uma máquina com infinitos estados e símbolos."
            ],
            "answer": "B) Uma máquina capaz de simular qualquer outra Máquina de Turing.",
            "example": "💻 EXEMPLO: Assim como um computador moderno pode executar diferentes programas (Word, Excel, jogos), a Máquina Universal pode simular qualquer algoritmo específico. É o conceito por trás dos computadores que usamos hoje!"
        },
        
        # Fase 2 – Solucionabilidade e Problemas
        {
            "phase": 2,
            "question": "O que significa dizer que um problema é 'decidível'?",
            "options": [
                "A) Que ele pode ser resolvido por algum algoritmo.",
                "B) Que pode ser respondido apenas com lógica informal.",
                "C) Que sempre terá múltiplas soluções."
            ],
            "answer": "A) Que ele pode ser resolvido por algum algoritmo.",
            "example": "✅ EXEMPLO: Ordenar uma lista de números é decidível - sempre podemos escrever um algoritmo (como Bubble Sort ou QuickSort) que resolva esse problema para qualquer entrada!"
        },
        {
            "phase": 2,
            "question": "Qual é a principal limitação dos algoritmos em relação à solucionabilidade?",
            "options": [
                "A) Eles não conseguem calcular raízes quadradas.",
                "B) Existem problemas que nenhum algoritmo pode resolver.",
                "C) Todos os algoritmos são lentos."
            ],
            "answer": "B) Existem problemas que nenhum algoritmo pode resolver.",
            "example": "🚫 EXEMPLO: Imagine tentar criar um programa que sempre determine se OUTRO programa vai travar ou não. Assim como não podemos prever todas as situações da vida real, alguns problemas são fundamentalmente insolúveis!"
        },
        {
            "phase": 2,
            "question": "O que representa o Problema da Parada?",
            "options": [
                "A) Verificar se um algoritmo vai terminar ou entrar em loop infinito.",
                "B) A situação em que um computador é desligado inesperadamente.",
                "C) O tempo máximo que um algoritmo pode rodar."
            ],
            "answer": "A) Verificar se um algoritmo vai terminar ou entrar em loop infinito.",
            "example": "⏰ EXEMPLO: Pense em um programa que soma números - ele sempre para. Agora um programa que busca o maior número primo - pode nunca terminar! O Problema da Parada mostra que NÃO podemos criar um verificador universal para isso."
        },
        
        # Fase 3 – Complexidade de Algoritmos (base)
        {
            "phase": 3,
            "question": "O que significa a notação O (Big-O)?",
            "options": [
                "A) Uma forma de medir o tempo de execução ou espaço de um algoritmo.",
                "B) Uma linguagem de programação orientada a objetos.",
                "C) Um tipo de algoritmo recursivo."
            ],
            "answer": "A) Uma forma de medir o tempo de execução ou espaço de um algoritmo.",
            "example": "📊 EXEMPLO: Se procurar um nome em uma lista não ordenada (O(n)) é como verificar cada pessoa individualmente, procurar em uma lista ordenada (O(log n)) é como usar índice telefônico - muito mais eficiente!"
        },
        {
            "phase": 3,
            "question": "Qual a diferença entre classes P e NP?",
            "options": [
                "A) P são problemas fáceis de resolver, NP são fáceis de verificar.",
                "B) P são problemas indecidíveis, NP são decidíveis.",
                "C) P são algoritmos recursivos, NP são iterativos."
            ],
            "answer": "A) P são problemas fáceis de resolver, NP são fáceis de verificar.",
            "example": "🎪 EXEMPLO: Ordenar cartas (P) é rápido. Verificar se estão ordenadas (NP) é instantâneo! Mas encontrar a sequência perfeita no quebra-cabeça é difícil - fácil verificar, difícil resolver."
        },
        {
            "phase": 3,
            "question": "O que significa dizer que um problema é NP-Completo?",
            "options": [
                "A) Que ele é tão difícil quanto os mais difíceis problemas em NP.",
                "B) Que ele pode ser resolvido em tempo constante.",
                "C) Que ele pertence tanto a P quanto a NP."
            ],
            "answer": "A) Que ele é tão difícil quanto os mais difíceis problemas em NP.",
            "example": "🧩 EXEMPLO: O problema do caixeiro-viajante é NP-Completo. Se você conseguir resolvê-lo rapidamente, poderá resolver TODOS os problemas difíceis rapidamente! É o 'rei' dos problemas complexos."
        },
        
        # Fase 4 – O Enigma de Hilbert
        {
            "phase": 4,
            "question": "Qual era o objetivo do 'Programa de Hilbert'?",
            "options": [
                "A) Criar computadores quânticos.",
                "B) Formalizar toda a matemática em sistemas completos e consistentes.",
                "C) Resolver problemas de engenharia elétrica."
            ],
            "answer": "B) Formalizar toda a matemática em sistemas completos e consistentes.",
            "example": "🏛️ EXEMPLO: Hilbert queria criar uma 'constituição matemática' onde todas as verdades pudessem ser provadas seguindo regras claras, como um jogo de xadrez com regras perfeitas onde todo movimento pode ser analisado."
        },
        {
            "phase": 4,
            "question": "Qual das seguintes áreas está diretamente ligada ao Programa de Hilbert?",
            "options": [
                "A) A formalização da lógica e da matemática.",
                "B) O desenvolvimento da robótica industrial.",
                "C) A criação de redes de computadores."
            ],
            "answer": "A) A formalização da lógica e da matemática.",
            "example": "🔍 EXEMPLO: Assim como um detetive usa lógica para resolver mistérios, Hilbert queria criar um sistema onde toda verdade matemática pudesse ser 'descoberta' seguindo regras lógicas precisas, sem ambiguidades."
        },
        {
            "phase": 4,
            "question": "Por que o sonho de Hilbert foi desafiado?",
            "options": [
                "A) Porque Gödel mostrou que nem todos os problemas podem ser resolvidos dentro de um sistema formal.",
                "B) Porque Turing inventou o computador moderno.",
                "C) Porque Hilbert abandonou a matemática."
            ],
            "answer": "A) Porque Gödel mostrou que nem todos os problemas podem ser resolvidos dentro de um sistema formal.",
            "example": "⚡ EXEMPLO: É como tentar criar um dicionário que defina TODAS as palavras - mas para definir uma palavra, você precisa usar outras palavras! Sempre haverá conceitos que não podem ser completamente explicados dentro do próprio sistema."
        },
        
        # Fase 5 – O Labirinto de Gödel
        {
            "phase": 5,
            "question": "O que dizem os Teoremas da Incompletude de Gödel?",
            "options": [
                "A) Que sempre é possível encontrar uma prova para qualquer enunciado.",
                "B) Que todo sistema formal consistente tem enunciados indecidíveis.",
                "C) Que os sistemas formais não podem representar números."
            ],
            "answer": "B) Que todo sistema formal consistente tem enunciados indecidíveis.",
            "example": "🎭 EXEMPLO: Pense na frase 'Esta frase é falsa'. Se for verdadeira, é falsa; se for falsa, é verdadeira! Gödel mostrou que na matemática sempre existem essas 'paradoxos' que não podem ser provados verdadeiros ou falsos."
        },
        {
            "phase": 5,
            "question": "Por que os resultados de Gödel foram um choque para o Programa de Hilbert?",
            "options": [
                "A) Porque mostraram limites fundamentais à formalização da matemática.",
                "B) Porque provaram que computadores nunca existiriam.",
                "C) Porque Gödel contradisse as leis da lógica clássica."
            ],
            "answer": "A) Porque mostraram limites fundamentais à formalização da matemática.",
            "example": "🌌 EXEMPLO: Imagine que você quer mapear TODA uma floresta, mas descobre que sempre haverá áreas inexploradas que você não pode mapear sem sair da floresta. Gödel mostrou que a matemática tem esses 'pontos cegos' fundamentais."
        },
        {
            "phase": 5,
            "question": "O que significa afirmar que um sistema formal consistente não pode ser completo?",
            "options": [
                "A) Que ele pode provar todas as verdades possíveis.",
                "B) Que sempre existirão verdades matemáticas que ele não pode provar.",
                "C) Que ele nunca pode ser usado para resolver problemas práticos."
            ],
            "answer": "B) Que sempre existirão verdades matemáticas que ele não pode provar.",
            "example": "🧩 EXEMPLO: É como um quebra-cabeça onde algumas peças simplesmente não se encaixam - não importa o quanto você tente, sempre faltará completar algumas partes. O sistema é consistente (as peças não se contradizem), mas incompleto (não cobre tudo)."
        },
        
        # Fase 6 – O Guardião Turing
        {
            "phase": 6,
            "question": "Qual foi a principal contribuição de Turing para a computação?",
            "options": [
                "A) Definir um modelo formal de computação (Máquina de Turing).",
                "B) Criar a linguagem de programação Python.",
                "C) Desenvolver o método de branch and bound."
            ],
            "answer": "A) Definir um modelo formal de computação (Máquina de Turing).",
            "example": "💡 EXEMPLO: Turing criou o 'DNA' de todos os computadores modernos. Assim como todas as receitas culinárias usam ingredientes básicos, todos os programas de computador podem ser reduzidos às operações simples de uma Máquina de Turing!"
        },
        {
            "phase": 6,
            "question": "O que é o Problema da Parada?",
            "options": [
                "A) A prova de que não existe algoritmo capaz de decidir se outro algoritmo vai parar ou não.",
                "B) O tempo mínimo para encerrar um programa.",
                "C) O processo de desligar um computador corretamente."
            ],
            "answer": "A) A prova de que não existe algoritmo capaz de decidir se outro algoritmo vai parar ou não.",
            "example": "⏳ EXEMPLO: É como tentar criar um detector universal de loops infinitos. Você pode detectar loops óbvios, mas alguns programas são como labirintos - não dá para saber se saem sem executá-los até o fim!"
        },
        {
            "phase": 6,
            "question": "Como os estudos de Turing se conectam à questão P vs NP?",
            "options": [
                "A) Porque Turing já havia discutido limites da computação e eficiência de algoritmos.",
                "B) Porque ele criou os primeiros algoritmos NP-Completos.",
                "C) Porque ele provou que P = NP."
            ],
            "answer": "A) Porque Turing já havia discutido limites da computação e eficiência de algoritmos.",
            "example": "🔗 EXEMPLO: Turing mostrou que existem problemas que computadores NUNCA podem resolver. A questão P vs NP pergunta: existem problemas que computadores podem VERIFICAR rapidamente, mas não RESOLVER rapidamente? É uma extensão natural do seu trabalho!"
        }
    ]

    print("\n🔍 Verificando dados inseridos...")
    for phase in range(1, 4):
        questions = list(mongo.db["quiz"].find({"phase": phase}))
        print(f"Fase {phase}: {len(questions)} perguntas")
        if questions:
            first_q = questions[0]
            print(f"  Campos: {list(first_q.keys())}")
            if 'example' in first_q:
                print(f"  ✅ Tem exemplo: {first_q['example'][:50]}...")
            else:
                print("  ❌ SEM EXEMPLO!")

    mongo.disconnect()
    print("✅ Seed finalizado com TODOS os exemplos!")