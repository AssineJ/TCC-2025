from modules.nlp_processor import processar_texto

print("=" * 70)
print("TESTES DO NLP PROCESSOR COM DIFERENTES TEXTOS")
print("=" * 70)
print()

                             
textos_teste = [
    {
        "nome": "Notícia Política",
        "texto": "O presidente Jair Bolsonaro se reuniu com o ministro da Economia Paulo Guedes no Palácio do Planalto em Brasília para discutir a reforma da previdência."
    },
    {
        "nome": "Notícia Econômica",
        "texto": "A Petrobras anunciou aumento no preço da gasolina e diesel nas refinarias. A decisão foi tomada após reunião com o Conselho de Administração."
    },
    {
        "nome": "Notícia de Saúde",
        "texto": "O Ministério da Saúde confirmou novos casos de dengue em São Paulo e Rio de Janeiro. A campanha de vacinação será intensificada nas próximas semanas."
    }
]

for i, item in enumerate(textos_teste, 1):
    print(f"Teste {i}: {item['nome']}")
    print("-" * 70)
    print(f"Texto: {item['texto'][:80]}...")
    print()
    
    resultado = processar_texto(item['texto'])
    
    print(f"  Entidades: {[e['texto'] for e in resultado['entidades'][:3]]}")
    print(f"Palavras-chave: {resultado['palavras_chave'][:5]}")
    print(f"Query: {resultado['query_busca']}")
    print()