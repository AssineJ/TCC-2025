from modules.scraper import scrape_noticias

print("=" * 70)
print("TESTE SCRAPER COM URLs REAIS")
print("=" * 70)
print()

                                                                        
resultados_busca_real = {
    'G1': [
        {
            'title': 'G1 - Home',
            'url': 'https://g1.globo.com/',
            'snippet': 'Portal G1'
        }
    ],
    'IstoÉ': [
        {
            'title': 'IstoÉ - Home',
            'url': 'https://istoe.com.br/',
            'snippet': 'Portal IstoÉ'
        }
    ],
    'metadata': {
        'total_resultados': 2,
        'fontes_com_sucesso': 2
    }
}

print("Testando com 2 URLs REAIS (home pages)...")
print()

                
conteudos = scrape_noticias(resultados_busca_real)

                    
print("\n" + "=" * 70)
print("RESULTADOS:")
print("=" * 70)
print()

for fonte_nome, fonte_conteudos in conteudos.items():
    if fonte_nome == 'metadata':
        continue
    
    for conteudo in fonte_conteudos:
        print(f" {fonte_nome}:")
        print(f"   URL: {conteudo['url']}")
        if conteudo['sucesso']:
            print(f"    SUCESSO!")
            print(f"   Título: {conteudo['titulo'][:60]}...")
            print(f"   Texto: {len(conteudo['texto'])} caracteres")
        else:
            print(f"    FALHOU: {conteudo['erro'][:50]}")
        print()

meta = conteudos['metadata']
print("ESTATÍSTICAS:")
print(f"  Sucessos: {meta['total_sucesso']}/{meta['total_scraped']}")
print(f"  Taxa: {meta['taxa_sucesso']:.1f}%")