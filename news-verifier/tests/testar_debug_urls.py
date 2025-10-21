import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

print("=" * 70)
print("TESTE COM DEBUG DE URLs")
print("=" * 70)
print()

texto = "Lula Haddad reforma tributária Brasil"

dados = {"tipo": "texto", "conteudo": texto}

print("Enviando requisição...")
print("Aguarde... Veja os logs do servidor para debug")
print()

response = requests.post(f'{BASE_URL}/api/verificar', json=dados, timeout=120)

if response.status_code == 200:
    resultado = response.json()
    
    print("=" * 70)
    print("RESPOSTA RECEBIDA")
    print("=" * 70)
    print()
    
    fontes = resultado.get('fontes_consultadas', [])
    
    print(f"Total de fontes: {len(fontes)}")
    print()
    
    urls_curtas = []
    urls_ok = []
    
    for i, fonte in enumerate(fontes[:10], 1):
        url = fonte.get('url', '')
        tamanho = len(url)
        
        print(f"{i}. {fonte['nome']}")
        print(f"   Tamanho: {tamanho} caracteres")
        print(f"   URL: {url}")
        
        if tamanho < 80:
            print(f"     SUSPEITA DE TRUNCAMENTO!")
            urls_curtas.append((fonte['nome'], url, tamanho))
        else:
            urls_ok.append((fonte['nome'], url, tamanho))
        
        print()
    
    print("=" * 70)
    print("ANÁLISE:")
    print("=" * 70)
    print(f"URLs OK (>= 80 chars): {len(urls_ok)}")
    print(f"URLs curtas (< 80 chars): {len(urls_curtas)}")
    
    if urls_curtas:
        print()
        print("  URLs SUSPEITAS DE TRUNCAMENTO:")
        for nome, url, tam in urls_curtas:
            print(f"  • {nome}: {tam} chars")
            print(f"    {url}")

else:
    print(f"Erro: {response.status_code}")