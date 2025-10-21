import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("TESTE INTEGRAÇÃO COMPLETA: APP + EXTRACTOR + NLP + SEARCHER")
print("=" * 70)
print()

texto_teste = """
O presidente Luiz Inácio Lula da Silva anunciou nesta terça-feira uma 
importante reforma tributária que vai reduzir impostos sobre alimentos 
básicos em todo o Brasil. A medida, que será implementada pelo 
Ministério da Fazenda a partir de 2025, deve beneficiar milhões de 
famílias brasileiras de baixa renda. Segundo economistas, a reforma 
pode ajudar a reduzir a inflação e estimular o consumo.
"""

dados = {
    "tipo": "texto",
    "conteudo": texto_teste
}

print("Enviando requisição...")
print()

response = requests.post(f'{BASE_URL}/api/verificar', json=dados)

print(f"Status: {response.status_code}")
print()

if response.status_code == 200:
    resultado = response.json()
    
    print("=" * 70)
    print("ANÁLISE COMPLETA DO SISTEMA")
    print("=" * 70)
    print()
    
    print(f"VERACIDADE: {resultado['veracidade']}%")
    print()
    
    print(f"TÍTULO:")
    print(f"   {resultado['titulo_analisado'][:80]}...")
    print()

                             

if response.status_code == 200:
    resultado = response.json()
    
                                        
    print("=" * 70)
    print("DEBUG: Estrutura da resposta")
    print("=" * 70)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print()
    print("=" * 70)
    print("Chaves presentes:", list(resultado.keys()))
    print("=" * 70)
    print()
    
                        
    
    print("ANÁLISE NLP (IA):")
    nlp = resultado['analise_nlp']
    print(f"   Query gerada: {nlp['query_busca']}")
    print(f"   Entidades: {[e['texto'] for e in nlp['entidades_encontradas'][:3]]}")
    print(f"   Palavras-chave: {nlp['palavras_chave'][:5]}")
    print()
    
    print("BUSCA REALIZADA:")
    meta = resultado['metadata']
    print(f"   Modo: {meta['modo_busca']}")
    print(f"   Total de resultados: {meta['total_resultados_busca']}")
    print(f"   Fontes consultadas: {meta['total_fontes_consultadas']}")
    print()
    
    print("FONTES ENCONTRADAS:")
    for i, fonte in enumerate(resultado['fontes_consultadas'], 1):
        print(f"\n   {i}. {fonte['nome']}")
        print(f"       {fonte['titulo'][:60]}...")
        print(f"       {fonte['url']}")
        print(f"       {fonte['total_resultados']} resultado(s) encontrado(s)")
        if fonte.get('snippet'):
            print(f"       {fonte['snippet'][:80]}...")
    
    print()
    print("=" * 70)
    print("SISTEMA FUNCIONANDO PERFEITAMENTE!")
    print("=" * 70)
    print()
    print("Módulos ativos:")
    print("   1.  Extractor (extração de conteúdo)")
    print("   2.  NLP Processor (análise com IA)")
    print("   3.  Searcher (busca nas fontes)")
    print("   4.  Scraper (próximo)")
    print("   5.  Semantic Analyzer (próximo)")
    print("   6.  Scorer (próximo)")
    
else:
    print(f"Erro: {response.json()}")
print()
input("Pressione ENTER para fechar...")

