import requests

response = requests.post('http://127.0.0.1:5000/api/verificar', json={
    "tipo": "texto",
    "conteudo": "O presidente anunciou reforma tributária que beneficiará milhões de brasileiros."
})

print(f"Status: {response.status_code}")
print(f"Resposta: {response.text}")