from modules.searcher import buscar_noticias
import time

print("=" * 70)
print("TESTE DE CACHE")
print("=" * 70)
print()

query = "teste cache busca"

                                  
print("1ª Busca (cria cache):")
inicio = time.time()
resultado1 = buscar_noticias(query)
tempo1 = time.time() - inicio
print(f"  Tempo: {tempo1:.2f}s")
print()

                                 
print("2ª Busca (usa cache):")
inicio = time.time()
resultado2 = buscar_noticias(query)
tempo2 = time.time() - inicio
print(f"  Tempo: {tempo2:.2f}s")
print()

if tempo2 < tempo1:
    print(f"Cache funcionando! {tempo2:.2f}s vs {tempo1:.2f}s")
    print(f"Aceleração: {tempo1/tempo2:.1f}x mais rápido")
else:
    print("  Cache pode não estar funcionando")