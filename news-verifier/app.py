import builtins
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from modules.extractor import extrair_conteudo
from modules.nlp_processor import processar_texto
from modules.searcher import buscar_noticias
from modules.filters import filtrar_busca, filtrar_scraping
from modules.scraper import scrape_noticias
from modules.semantic_analyzer import analisar_semantica
from modules.scorer import calcular_veracidade
from modules.text_validator import validar_qualidade_texto, validar_url              
import sys

sys.stdout.reconfigure(encoding='utf-8')

                          
app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def home():
    return jsonify({"status": "online"}), 200

CORS(app, 
     resources={r"/api/*": {
         "origins": "*",
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type"]
     }})

                         
log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.DEBUG)
logging.basicConfig(level=log_level, format=Config.LOG_FORMAT)

if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler(
    'logs/app.log', maxBytes=1_048_576, backupCount=3, encoding='utf-8'
)
file_handler.setLevel(log_level)
file_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))

app.logger.setLevel(log_level)

if not any(isinstance(handler, RotatingFileHandler) for handler in app.logger.handlers):
    app.logger.addHandler(file_handler)


def log_info(message: str = ""):
    """Registra mensagens informativas no logger e mantém saída no console."""
    if message:
        app.logger.info(message)
        builtins.print(message)
    else:
        builtins.print()

                                     
app.config.from_object(Config)


@app.route('/api/verificar', methods=['POST'])
def verificar_noticia():
    """
    Endpoint principal que recebe uma notícia e retorna análise de veracidade.
     COM VALIDAÇÃO DE QUALIDADE DE TEXTO
    """

    try:
                                
        dados = request.get_json()

        if not dados:
            return jsonify({
                "erro": "Nenhum dado JSON foi enviado",
                "codigo": "INVALID_JSON"
            }), 400

        if 'tipo'not in dados or 'conteudo'not in dados:
            return jsonify({
                "erro": "Campos obrigatórios: 'tipo'e 'conteudo'",
                "codigo": "MISSING_FIELDS"
            }), 400

        tipo = dados['tipo']
        conteudo = dados['conteudo']
        conteudo_limpo = conteudo.strip()

        if tipo not in ['url', 'texto']:
            return jsonify({
                "erro": "Tipo deve ser 'url'ou 'texto'",
                "codigo": "INVALID_TYPE"
            }), 400

        if not conteudo_limpo:
            return jsonify({
                "erro": "Conteúdo não pode estar vazio",
                "codigo": "EMPTY_CONTENT"
            }), 400

        if tipo == 'url':
            if len(conteudo_limpo) < Config.MIN_URL_LENGTH:
                return jsonify({
                    "erro": Config.ERROR_MESSAGES['URL_TOO_SHORT'],
                    "codigo": "URL_TOO_SHORT"
                }), 422

            if len(conteudo_limpo) > Config.MAX_URL_LENGTH:
                return jsonify({
                    "erro": Config.ERROR_MESSAGES['URL_TOO_LONG'],
                    "codigo": "URL_TOO_LONG"
                }), 422
        else:
            if len(conteudo_limpo) < Config.MIN_CONTENT_LENGTH:
                return jsonify({
                    "erro": Config.ERROR_MESSAGES['CONTENT_TOO_SHORT'],
                    "codigo": "CONTENT_TOO_SHORT"
                }), 422

            if len(conteudo_limpo) > Config.MAX_CONTENT_LENGTH:
                return jsonify({
                    "erro": Config.ERROR_MESSAGES['CONTENT_TOO_LONG'],
                    "codigo": "CONTENT_TOO_LONG"
                }), 422

        log_info(
            f"Requisição recebida: tipo={tipo} | tamanho_conteudo={len(conteudo_limpo)}"
        )




        if tipo == 'url':

            validacao_url = validar_url(conteudo_limpo)
            if not validacao_url['valido']:
                log_info(f"URL inválida: {validacao_url['motivo']}")
                return jsonify({
                    "erro": "URL inválida",
                    "detalhes": validacao_url['motivo'],
                    "codigo": "INVALID_URL"
                }), 422
        else:
                                        
            log_info(f"Validando qualidade do texto...")
            validacao_texto = validar_qualidade_texto(conteudo)
            
            log_info(f"   Score qualidade: {validacao_texto['score_qualidade']}")
            log_info(f"   Problemas: {len(validacao_texto['problemas'])}")
            
            if not validacao_texto['valido']:
                log_info(f"Texto REJEITADO: {validacao_texto['motivo']}")
                return jsonify({
                    "erro": "Dados fornecidos insuficientes para validação",
                    "detalhes": validacao_texto['motivo'],
                    "problemas": validacao_texto['problemas'],
                    "score_qualidade": validacao_texto['score_qualidade'],
                    "codigo": "INVALID_TEXT_QUALITY"
                }), 422
            
            log_info(f"Texto validado com sucesso (qualidade: {validacao_texto['score_qualidade']})")

                                                
        texto_para_analise = ""
        titulo_noticia = ""
        url_original = conteudo_limpo if tipo == 'url'else None

        if tipo == 'url':
            log_info(f"Extraindo conteúdo de: {conteudo_limpo}")
            resultado_extracao = extrair_conteudo(conteudo_limpo)

            if not resultado_extracao['sucesso']:
                return jsonify({
                    "erro": "Não foi possível extrair conteúdo da URL",
                    "detalhes": resultado_extracao['erro'],
                    "codigo": "EXTRACTION_FAILED"
                }), 422

            texto_para_analise = resultado_extracao['texto']
            titulo_noticia = resultado_extracao['titulo']
            log_info(f"Conteúdo extraído: {len(texto_para_analise)} caracteres")

        else:
            texto_para_analise = conteudo_limpo
            titulo_noticia = texto_para_analise[:100] + "..."

                                          
        log_info(f"Processando texto com IA...")
        resultado_nlp = processar_texto(texto_para_analise)

        log_info(f"NLP concluído:")
        log_info(f"   - {len(resultado_nlp['entidades'])} entidades encontradas")
        log_info(f"   - {len(resultado_nlp['palavras_chave'])} palavras-chave extraídas")
        log_info(f"   - Query de busca: {resultado_nlp['query_busca']}")

                                               
        log_info(f"Buscando nas fontes confiáveis...")
        resultado_busca = buscar_noticias(resultado_nlp['query_busca'])

        log_info(f"Busca concluída:")
        log_info(f"   - Total de resultados: {resultado_busca['metadata']['total_resultados']}")
        log_info(f"   - Fontes com sucesso: {resultado_busca['metadata']['fontes_com_sucesso']}/{resultado_busca['metadata']['total_fontes']}")

                                  
        resultado_busca_filtrado = filtrar_busca(resultado_busca)

        log_info(f"Filtros aplicados:")
        log_info(f"   - Mantidos: {resultado_busca_filtrado['metadata']['total_resultados']}")
        log_info(f"   - Filtrados: {resultado_busca_filtrado['metadata'].get('total_filtrados', 0)}")

                                                        
        log_info(f"Extraindo conteúdo das notícias encontradas...")
        resultado_scraping = scrape_noticias(resultado_busca_filtrado)

        log_info(f"Scraping concluído:")
        log_info(f"   - Total processado: {resultado_scraping['metadata']['total_scraped']}")
        log_info(f"   - Sucessos: {resultado_scraping['metadata']['total_sucesso']}")
        log_info(f"   - Taxa: {resultado_scraping['metadata']['taxa_sucesso']:.1f}%")

                                     
        resultado_scraping_filtrado = filtrar_scraping(resultado_scraping, texto_para_analise)

        log_info(f"Filtros aplicados:")
        log_info(f"   - Mantidos: {resultado_scraping_filtrado['metadata']['total_sucesso']}")
        log_info(f"   - Filtrados: {resultado_scraping_filtrado['metadata'].get('total_filtrados', 0)}")

                                                                         
        log_info(f"Analisando similaridade semântica com IA...")
        resultado_analise = analisar_semantica(texto_para_analise, resultado_scraping_filtrado)

        log_info(f"Análise semântica concluída:")
        
        contradizem = resultado_analise['metadata'].get('contradizem', 0)
        if contradizem > 0:
            log_info(f"   -   CONTRADIZEM: {contradizem}")
        
        log_info(f"   - Confirmam forte: {resultado_analise['metadata']['confirmam_forte']}")
        log_info(f"   - Confirmam parcial: {resultado_analise['metadata']['confirmam_parcial']}")
        log_info(f"   - Apenas mencionam: {resultado_analise['metadata']['apenas_mencionam']}")

                                                                               
        log_info(f"Calculando veracidade final...")
        resultado_score = calcular_veracidade(resultado_analise, {
            'tipo_entrada': tipo,
            'tamanho_conteudo': len(texto_para_analise),
            'total_fontes_buscadas': resultado_busca['metadata']['total_resultados']
        })

        log_info(f"Score calculado: {resultado_score['veracidade']}%")
        log_info(f"   Nível de confiança: {resultado_score['nivel_confianca']}")
        
        if contradizem > 0:
            log_info(f"     ALERTA: {contradizem} fonte(s) contradizem a informação!")

                                     
        fontes_consultadas = []

        urls_originais_busca = {}
        for fonte_nome, fonte_resultados in resultado_busca_filtrado.items():
            if fonte_nome == 'metadata':
                continue
            for res in fonte_resultados:
                url = res.get('url', '')
                titulo_chave = res.get('title', '')[:50]
                urls_originais_busca[titulo_chave] = url

        for fonte_nome, fonte_analises in resultado_analise.items():
            if fonte_nome == 'metadata':
                continue

            for analise in fonte_analises:
                if analise.get('sucesso'):
                    titulo = analise.get('titulo', '')
                    titulo_chave = titulo[:50]
                    url_analise = analise.get('url', '')

                    if len(url_analise) < 80 and titulo_chave in urls_originais_busca:
                        url_final = urls_originais_busca[titulo_chave]
                        log_info(f"[RECUPERADO] URL completa de {fonte_nome}: {len(url_final)} chars")
                    else:
                        url_final = url_analise

                    fontes_consultadas.append({
                        "nome": fonte_nome,
                        "url": url_final,
                        "titulo": titulo,
                        "similaridade": analise.get('similaridade', 0),
                        "status": analise.get('status', ''),
                        "motivo": analise.get('motivo', ''),
                        "contradiz": analise.get('contradiz', False),
                        "confianca_contradicao": analise.get('confianca_contradicao', 0.0)
                    })

        fontes_consultadas.sort(key=lambda x: x['similaridade'], reverse=True)

                               
        meta_analise = resultado_analise['metadata']

        resposta = {
            "veracidade": resultado_score['veracidade'],
            "justificativa": resultado_score['justificativa'],
            "nivel_confianca": resultado_score['nivel_confianca'],
            "titulo_analisado": titulo_noticia,
            "tamanho_texto_analisado": len(texto_para_analise),
            "alerta_contradicao": contradizem > 0,
            "total_contradicoes": contradizem,
            "calculo_detalhado": resultado_score['detalhes'],
            "analise_nlp": {
                "entidades_encontradas": resultado_nlp['entidades'][:5],
                "palavras_chave": resultado_nlp['palavras_chave'][:8],
                "query_busca": resultado_nlp['query_busca'],
                "estatisticas": resultado_nlp['estatisticas']
            },
            "analise_semantica": {
                "total_analisados": meta_analise['total_analisados'],
                "contradizem": meta_analise.get('contradizem', 0),
                "confirmam_forte": meta_analise['confirmam_forte'],
                "confirmam_parcial": meta_analise['confirmam_parcial'],
                "apenas_mencionam": meta_analise['apenas_mencionam'],
                "nao_relacionados": meta_analise['nao_relacionados']
            },
            "fontes_consultadas": fontes_consultadas[:10],
            "metadata": {
                "tipo_entrada": tipo,
                "url_original": url_original,
                "tamanho_conteudo": len(texto_para_analise),
                "versao_sistema": "1.0-final-validation",
                "total_fontes_consultadas": len(fontes_consultadas),
                "fontes_disponiveis": len(Config.TRUSTED_SOURCES),
                "processamento_nlp_completo": True,
                "busca_realizada": True,
                "filtros_aplicados": True,
                "scraping_realizado": True,
                "analise_semantica_realizada": True,
                "deteccao_contradicao_ativa": True,
                "validacao_texto_ativa": True,         
                "scoring_completo": True,
                "total_resultados_busca": resultado_busca['metadata']['total_resultados'],
                "total_scraped": resultado_scraping_filtrado['metadata']['total_scraped'],
                "total_analisados": meta_analise['total_analisados'],
                "modo_busca": resultado_busca['metadata']['modo_busca']
            }
        }

        log_info(
            f"Análise concluída com sucesso | veracidade={resposta['veracidade']}% | fontes={len(fontes_consultadas)}"
        )
        
        if contradizem > 0:
            log_info(f"ALERTA FINAL: Detectada provável FAKE NEWS!")

        return jsonify(resposta), 200

    except Exception as e:
        app.logger.exception("Erro interno ao verificar notícia")
        return jsonify({
            "erro": "Erro interno do servidor",
            "detalhes": str(e),
            "codigo": "INTERNAL_ERROR"
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está online."""
    return jsonify({
        "status": "online",
        "versao": "1.0-final-validation",
        "mensagem": "News Verifier API com validação de texto!",
        "modulos_ativos": [
            "extractor",
            "nlp_processor",
            "searcher",
            "filters",
            "scraper",
            "semantic_analyzer (com detecção de contradição)",
            "scorer (com penalidade por contradição)",
            "text_validator (validação de qualidade)"         
        ]
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Rota raiz - Informações sobre a API"""
    return jsonify({
        "nome": "News Verifier API",
        "versao": "1.0-complete-validation",
        "descricao": "Sistema de Verificação de Veracidade com IA e Validação de Texto",
        "endpoints": {
            "POST /api/verificar": "Verificar veracidade de notícia",
            "GET /api/health": "Verificar status da API",
            "GET /": "Informações da API"
        },
        "fontes_confiaveis": [fonte['nome'] for fonte in Config.TRUSTED_SOURCES],
        "tecnologias": [
            "Flask",
            "spaCy (NLP)",
            "sentence-transformers (IA Semântica)",
            "newspaper3k",
            "BeautifulSoup",
            "Detecção de Contradição",
            "Validação de Qualidade de Texto"         
        ],
        "novidades": [
            "Detecção automática de contradições",
            "Penalidade severa para fake news",
            "Validação de qualidade de texto",         
            "Rejeita textos repetitivos/inválidos"         
        ]
    }), 200


if __name__ == '__main__':
    log_info("=" * 70)
    log_info("Iniciando News Verifier API...")
    log_info("=" * 70)
    log_info(f"Servidor rodando em: http://127.0.0.1:{Config.PORT}")
    log_info(f"Versão: 1.0-final-validation (COM VALIDAÇÃO DE TEXTO)")
    log_info(f"Pressione Ctrl+C para parar o servidor")
    log_info("=" * 70)
    log_info()
    log_info("Módulos carregados:")
    log_info("   1.  Extractor (URLs)")
    log_info("   2.  NLP Processor (spaCy)")
    log_info("   3.  Searcher (Busca Híbrida)")
    log_info("   4.  Filters (Anti-paywall/404)")
    log_info("   5.  Scraper (Conteúdo)")
    log_info("   6.  Semantic Analyzer (IA + Detecção de Contradição)")
    log_info("   7.  Scorer (Veracidade + Penalidade por Fake News)")
    log_info("   8.  Text Validator (Validação de Qualidade)")         
    log_info("=" * 70)
    log_info()

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
