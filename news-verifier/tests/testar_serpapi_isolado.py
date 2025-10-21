from config import Config

print("=" * 70)
print("TESTE ISOLADO DO SERPAPI")
print("=" * 70)
print()

                                     
if not Config.SERPAPI_KEY:
    print("SERPAPI_KEY não configurada!")
    print()
    print("Para testar:")
    print("1. Crie conta em https://serpapi.com/")
    print("2. Copie sua API Key")
    print("3. Cole no arquivo .env:")
    print("   SERPAPI_KEY=sua_chave_aqui")
    exit()

print(f"SERPAPI_KEY configurada!")
print(f"   Chave: {Config.SERPAPI_KEY[:10]}...{Config.SERPAPI_KEY[-5:]}")
print()

                      
from modules.searcher import SearchEngine

engine = SearchEngine()

query = "Lula Brasil reforma"
site = "g1.globo.com"

print(f"Testando busca:")
print(f"   Query: {query}")
print(f"   Site: {site}")
print()

                         
Config.SEARCH_MODE = 'serpapi'

try:
    print("Buscando...")
    resultados = engine.buscar(query, site)
    
    if resultados:
        print(f"SUCESSO! Encontrados {len(resultados)} resultados")
        print()
        
        for i, r in enumerate(resultados, 1):
            print(f"{i}. {r['title'][:60]}...")
            print(f"   URL: {r['url']}")
            print(f"   Snippet: {r['snippet'][:80]}...")
            print()
        
        print("=" * 70)
        print("SERPAPI FUNCIONANDO PERFEITAMENTE!")
        print("=" * 70)
        print()
        print(f"Requisições usadas: {engine.serpapi_count}/100")
    
    else:
        print("  Nenhum resultado encontrado")
        print("   Isso pode ser normal se não há notícias sobre o tema")

except Exception as e:
    print(f"ERRO: {e}")
    print()
    print("Possíveis causas:")
    print("   • Chave API inválida")
    print("   • Limite de requisições atingido (100/mês)")
    print("   • Problema de conexão")