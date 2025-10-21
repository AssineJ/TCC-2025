import requests
import json
import os

                    
os.environ['SEARCH_MODE'] = 'direct'

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("TESTE: MODO DIRECT (Busca Direta nos Sites)")
print("=" * 70)
print()

texto_teste = """
O presidente Lula realizou reunião com ministros para discutir 
economia e políticas públicas no Palácio do Planalto.
"""

dados = {
    "tipo": "texto",
    "conteudo": texto_teste
}

print("Enviando requisição (modo: direct)...")
print()

response = requests.post(f'{BASE_URL}/api/verificar', json=dados)

if response.status_code == 200:
    resultado = response.json()
    
    print(f"Status: {response.status_code}")
    print()
    print(f"Veracidade: {resultado['veracidade']}%")
    print()
    print(f"Modo de busca: {resultado['metadata']['modo_busca']}")
    print(f"Resultados encontrados: {resultado['metadata']['total_resultados_busca']}")
    print(f"Conteúdos extraídos: {resultado['metadata']['total_scraped']}")
    print(f"Análises realizadas: {resultado['metadata']['total_analisados']}")
    print()
    
    print("Análise Semântica:")
    sem = resultado['analise_semantica']
    print(f"   Confirmam forte: {sem['confirmam_forte']}")
    print(f"   Confirmam parcial: {sem['confirmam_parcial']}")
    print()
    
    if resultado['fontes_consultadas']:
        print(f"Fontes encontradas: {len(resultado['fontes_consultadas'])}")
        for i, fonte in enumerate(resultado['fontes_consultadas'][:3], 1):
            print(f"   {i}. {fonte['nome']} - Sim: {fonte['similaridade']:.2f}")
    
    print()
    print("=" * 70)
    print("MODO DIRECT FUNCIONANDO!"if resultado['metadata']['total_resultados_busca'] > 0 else "  MODO DIRECT: Poucos resultados")
    print("=" * 70)
else:
    print(f"Erro: {response.status_code}")
    print(response.json())