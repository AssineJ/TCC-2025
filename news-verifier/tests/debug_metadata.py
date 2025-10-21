from modules.searcher import buscar_noticias

query = "teste debug"
resultado = buscar_noticias(query)

print("=" * 70)
print("DEBUG: Estrutura do resultado")
print("=" * 70)
print()

print("Chaves principais:")
for chave in resultado.keys():
    print(f"  - {chave}")
print()

print("Conteúdo de metadata:")
if 'metadata'in resultado:
    for chave, valor in resultado['metadata'].items():
        print(f"  {chave}: {valor}")
else:
    print("  METADATA NÃO ENCONTRADO!")
print()

                                 
import json
print("Estrutura JSON completa:")
print(json.dumps(resultado, indent=2, ensure_ascii=False)[:500])