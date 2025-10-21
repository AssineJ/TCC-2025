import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("TESTES COM CONFIGURAÇÕES DO config.py")
print("=" * 70)
print()

                                              
print("Teste 1: Texto muito curto")
dados = {
    "tipo": "texto",
    "conteudo": "Texto pequeno"                        
}
response = requests.post(f'{BASE_URL}/api/verificar', json=dados)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
print()

                                                 
print("Teste 2: Texto muito longo")
dados = {
    "tipo": "texto",
    "conteudo": "a" * 11000                    
}
response = requests.post(f'{BASE_URL}/api/verificar', json=dados)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
print()

                                              
print("Teste 3: Texto válido com fontes do config.py")
dados = {
    "tipo": "texto",
    "conteudo": "O presidente brasileiro anunciou ontem uma importante reforma tributária que reduzirá impostos sobre alimentos básicos."
}
response = requests.post(f'{BASE_URL}/api/verificar', json=dados)
print(f"Status: {response.status_code}")
resultado = response.json()
print(json.dumps(resultado, indent=2, ensure_ascii=False))
print()
print(f"Fontes disponíveis no sistema: {resultado['metadata']['fontes_disponiveis']}")