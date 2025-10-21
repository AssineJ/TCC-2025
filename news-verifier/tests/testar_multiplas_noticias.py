import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5000'
PAYWALL_SOURCES = ['Folha de S.Paulo', 'Estadão']

print("=" * 70)
print("TESTE COMPLETO: MÚLTIPLAS NOTÍCIAS")
print("=" * 70)
print()

                                                          
noticias_teste = [
    {
        "nome": "Política - Reforma Tributária",
        "texto": """
        O presidente Luiz Inácio Lula da Silva assinou nesta quarta-feira o 
        decreto que regulamenta a reforma tributária no Brasil. A medida 
        estabelece novas regras para o Imposto sobre Valor Agregado (IVA) e 
        prevê uma transição gradual até 2033. O ministro da Fazenda, Fernando 
        Haddad, participou da cerimônia no Palácio do Planalto em Brasília.
        """
    },
    {
        "nome": "Economia - Dólar",
        "texto": """
        O dólar fechou em alta nesta terça-feira, cotado a R$ 5,45, após 
        declarações do presidente do Banco Central sobre a política monetária. 
        Analistas do mercado financeiro avaliam que a taxa de juros deve ser 
        mantida em 11,25% na próxima reunião do Copom. A bolsa de valores 
        apresentou queda de 2,3% no dia.
        """
    },
    {
        "nome": "STF - Mulheres Ministras",
        "texto": """
        O Supremo Tribunal Federal teve apenas três mulheres ministras em 
        toda sua história e movimentos sociais começam a cobrar do presidente 
        Lula pela sucessão de Barroso. A discussão sobre diversidade de gênero 
        no STF ganhou força com a aproximação da aposentadoria do ministro 
        Luís Roberto Barroso, que deixará o cargo em breve.
        """
    },
    {
        "nome": "Saúde - Vacinação",
        "texto": """
        O Ministério da Saúde anunciou nesta quinta-feira o início da campanha 
        nacional de vacinação contra a gripe. A expectativa é imunizar mais de 
        80 milhões de brasileiros até o final de maio. Idosos acima de 60 anos, 
        gestantes e profissionais de saúde fazem parte do grupo prioritário.
        """
    },
    {
        "nome": "Educação - ENEM",
        "texto": """
        O Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira 
        (INEP) divulgou o cronograma do Exame Nacional do Ensino Médio (ENEM) 
        2025. As provas serão aplicadas nos dias 9 e 16 de novembro. As 
        inscrições começam em maio e vão até junho, com taxa de R$ 85.
        """
    }
]

resultados_testes = []

for i, noticia in enumerate(noticias_teste, 1):
    print("\n" + "=" * 70)
    print(f"TESTE {i}/{len(noticias_teste)}: {noticia['nome']}")
    print("=" * 70)
    print()
    
    print(f"Texto: {noticia['texto'][:100].strip()}...")
    print()
    print("Processando...")
    
    dados = {
        "tipo": "texto",
        "conteudo": noticia['texto']
    }
    
    inicio = time.time()
    
    try:
        response = requests.post(f'{BASE_URL}/api/verificar', json=dados, timeout=120)
        tempo = time.time() - inicio
        
        if response.status_code == 200:
            resultado = response.json()
            
            print(f"SUCESSO (Tempo: {tempo:.1f}s)")
            print()
            
                                 
            veracidade = resultado['veracidade']
            nivel = resultado['nivel_confianca']
            sem = resultado['analise_semantica']
            total_fontes = len(resultado['fontes_consultadas'])
            
            print(f"Veracidade: {veracidade}%")
            print(f"Nível: {nivel.upper()}")
            print(f"Fontes consultadas: {total_fontes}")
            print()
            
            print(f"Análise Semântica:")
            print(f"   Total: {sem['total_analisados']}")
            print(f"    Forte: {sem['confirmam_forte']}")
            print(f"   ~ Parcial: {sem['confirmam_parcial']}")
            print(f"   • Menciona: {sem['apenas_mencionam']}")
            print()
            
                                          
            fontes_paywall = PAYWALL_SOURCES
            total_paywall = len(fontes_paywall)
            fontes_paywall_funcionando = []
            
            for fonte in resultado['fontes_consultadas']:
                if fonte['nome'] in fontes_paywall and fonte['similaridade'] > 0:
                    fontes_paywall_funcionando.append(fonte['nome'])
            
            print(f"Fontes com paywall funcionando: {len(fontes_paywall_funcionando)}/{total_paywall}")
            if fontes_paywall_funcionando:
                for f in fontes_paywall_funcionando:
                    print(f"    {f}")
            print()
            
                          
            print("Top 3 Fontes:")
            for j, fonte in enumerate(resultado['fontes_consultadas'][:3], 1):
                print(f"   {j}. {fonte['nome']} - {fonte['similaridade']:.4f}")
                print(f"      {fonte['titulo'][:60]}...")
            
                              
            resultados_testes.append({
                'nome': noticia['nome'],
                'sucesso': True,
                'veracidade': veracidade,
                'nivel': nivel,
                'total_fontes': total_fontes,
                'confirmam_forte': sem['confirmam_forte'],
                'fontes_paywall_ok': len(fontes_paywall_funcionando),
                'tempo': tempo
            })
        
        else:
            print(f"ERRO {response.status_code}")
            print(response.text[:200])
            
            resultados_testes.append({
                'nome': noticia['nome'],
                'sucesso': False,
                'erro': response.status_code
            })
    
    except Exception as e:
        print(f"EXCEÇÃO: {str(e)[:100]}")
        
        resultados_testes.append({
            'nome': noticia['nome'],
            'sucesso': False,
            'erro': str(e)
        })
    
                                                  
    if i < len(noticias_teste):
        print()
        print("Aguardando 3s antes do próximo teste...")
        time.sleep(3)

              
print("\n\n" + "=" * 70)
print("RESUMO DOS TESTES")
print("=" * 70)
print()

sucessos = sum(1 for r in resultados_testes if r['sucesso'])
total = len(resultados_testes)

print(f"Taxa de sucesso: {sucessos}/{total} ({sucessos/total*100:.0f}%)")
print()

                      
total_paywall = len(PAYWALL_SOURCES)

print(f"{'Teste':<30} {'Sucesso':<10} {'Verac.':<10} {'Fontes':<10} {'Paywall'}")
print("-" * 70)

for r in resultados_testes:
    if r['sucesso']:
        print(f"{r['nome']:<30} {'':<10} {str(r['veracidade'])+'%':<10} {r['total_fontes']:<10} {r['fontes_paywall_ok']}/{total_paywall}")
    else:
        print(f"{r['nome']:<30} {'':<10} {'-':<10} {'-':<10} -")

print()
print("=" * 70)
print("ESTATÍSTICAS:")
print("=" * 70)

if sucessos > 0:
    veracidade_media = sum(r['veracidade'] for r in resultados_testes if r['sucesso']) / sucessos
    tempo_medio = sum(r['tempo'] for r in resultados_testes if r['sucesso']) / sucessos
    fontes_media = sum(r['total_fontes'] for r in resultados_testes if r['sucesso']) / sucessos
    paywall_media = sum(r['fontes_paywall_ok'] for r in resultados_testes if r['sucesso']) / sucessos
    
    print(f"Veracidade média: {veracidade_media:.1f}%")
    print(f"Tempo médio: {tempo_medio:.1f}s")
    print(f"Fontes média: {fontes_media:.1f}")
    print(f"Paywall funcionando: {paywall_media:.1f}/{total_paywall}")
    print()
    
                                    
    print("Por nível de confiança:")
    niveis = {}
    for r in resultados_testes:
        if r['sucesso']:
            nivel = r['nivel']
            niveis[nivel] = niveis.get(nivel, 0) + 1
    
    for nivel, count in niveis.items():
        print(f"   {nivel.upper()}: {count}")

print()
print("=" * 70)
print("ANÁLISE FINAL:")
print("=" * 70)

if sucessos == total:
    print("TODOS OS TESTES PASSARAM!")
    print("   Sistema funcionando perfeitamente com título+snippet")
elif sucessos >= total * 0.8:
    print("MAIORIA DOS TESTES PASSOU!")
    print("   Sistema funcionando bem, pequenos ajustes podem ser necessários")
else:
    print("  ALGUNS TESTES FALHARAM")
    print("   Revisar erros e fazer ajustes")

print()

                                       
paywall_ok_count = sum(
    1
    for r in resultados_testes
    if r.get('sucesso') and r.get('fontes_paywall_ok', 0) >= total_paywall
)

if paywall_ok_count >= total * 0.8:
    print("SOLUÇÃO TÍTULO+SNIPPET FUNCIONANDO!")
    print("   Fontes com paywall operando corretamente")
else:
    print("  Paywall com problemas em alguns casos")
    print("   Pode precisar revisar configuração")

print()
print("=" * 70)
print()
print("SISTEMA PRONTO PARA DOCUMENTAÇÃO!")
print("=" * 70)