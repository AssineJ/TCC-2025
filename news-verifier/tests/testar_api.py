import requests
import json

                       
print("=== Teste 1: Health Check ===")
response = requests.get('http://127.0.0.1:5000/api/health')
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
print()

                                    
print("=== Teste 2: Verificar Notícia (Texto) ===")
dados = {
    "tipo": "texto",
    "conteudo": "O presidente anunciou ontem a redução de impostos sobre alimentos básicos em todo o país."
}
response = requests.post('http://127.0.0.1:5000/api/verificar', json=dados)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
print()

                                  
print("=== Teste 3: Verificar Notícia (URL) ===")
dados = {
    "tipo": "url",
    "conteudo": "https://g1.globo.com/rj/rio-de-janeiro/noticia/2025/10/08/secretaria-de-seguranca-publica-do-rj-alerta-para-golpe-com-uso-de-voz.ghtml"
}
response = requests.post('http://127.0.0.1:5000/api/verificar', json=dados)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))