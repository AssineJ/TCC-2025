import os
from dotenv import load_dotenv

                                                                              
                                                
                                                                              

                                    
load_dotenv()


                                                                              
                        
                                                                              

class Config:
    """
    Classe que centraliza todas as configurações do sistema.
    Usa variáveis de ambiente quando disponíveis, senão usa valores padrão.
    """
    
                                                                              
                            
                                                                              
    
                                                                 
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
                                                 
    ENV = os.getenv('FLASK_ENV', 'development')
    
                           
    JSON_AS_ASCII = False                                          
    JSON_SORT_KEYS = False                                    
    
                       
    PORT = int(os.getenv('PORT', 5000))
    
                                                                   
    HOST = os.getenv('HOST', '0.0.0.0')
    
    
                                                                              
                                   
                                                                              
    
    TRUSTED_SOURCES = [
        {
            "nome": "G1",
            "dominio": "g1.globo.com",
            "url_base": "https://g1.globo.com",
            "url_busca": "https://g1.globo.com/busca/?q=",
            "confiabilidade": 0.95,                                     
            "ativo": True
        },
        {
            "nome": "Folha de S.Paulo",
            "dominio": "folha.uol.com.br",
            "url_base": "https://www.folha.uol.com.br",
            "url_busca": "https://busca.folha.uol.com.br/?q=",
            "confiabilidade": 0.95,
            "ativo": True
        },
        {
            "nome": "CNN Brasil",
            "dominio": "cnnbrasil.com.br",
            "url_base": "https://www.cnnbrasil.com.br",
            "url_busca": "https://www.cnnbrasil.com.br/busca/?q=",
            "confiabilidade": 0.90,
            "ativo": True
        },
        {
            "nome": "IstoÉ",
            "dominio": "istoe.com.br",
            "url_base": "https://istoe.com.br",
            "url_busca": "https://istoe.com.br/?s=",
            "confiabilidade": 0.92,
            "ativo": True
        },
        {
            "nome": "Estadão",
            "dominio": "estadao.com.br",
            "url_base": "https://www.estadao.com.br",
            "url_busca": "https://www.estadao.com.br/busca/?q=",
            "confiabilidade": 0.93,
            "ativo": True
        }
    ]
    
                                                      
    TRUSTED_DOMAINS = [fonte["dominio"] for fonte in TRUSTED_SOURCES]
    
                                                                      
    SOURCES_WITH_PAYWALL = ['Folha de S.Paulo', 'Estadão']
    
                                           
    MAX_RESULTS_PER_SOURCE = 2
    
    
                                                                              
                        
                                                                              
    
                                              
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 5))
    
                                                 
    SCRAPING_TIMEOUT = int(os.getenv('SCRAPING_TIMEOUT', 10))
    
                                                     
    ANALYSIS_TIMEOUT = int(os.getenv('ANALYSIS_TIMEOUT', 30))
    
                                                            
    DELAY_BETWEEN_REQUESTS = 1.0            
    
                                           
    MAX_RETRIES = 3
    
                                                  
    RETRY_DELAY = 2            
    
    
                                                                              
                         
                                                                              
    
                                                          
    MIN_CONTENT_LENGTH = int(os.getenv('MIN_CONTENT_LENGTH', 50))
    MIN_URL_LENGTH = int(os.getenv('MIN_URL_LENGTH', 10))
    MAX_URL_LENGTH = int(os.getenv('MAX_URL_LENGTH', 2048))
    
                                             
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 500))
    
                                               
    MAX_KEYWORDS = 10
    
                                                      
    MAX_ENTITIES = 15
    
    
                                                                              
                               
                                                                              
    
                                    
    SPACY_MODEL = "pt_core_news_lg"
    
                                                                 
    SENTENCE_TRANSFORMER_MODEL = "paraphrase-multilingual-mpnet-base-v2"
    
                                                                   
                                                      
    SIMILARITY_THRESHOLD_HIGH = 0.65                           
    SIMILARITY_THRESHOLD_MEDIUM = 0.45                           
    SIMILARITY_THRESHOLD_LOW = 0.30                               
    
                                           
    ENTITY_TYPES = ['PERSON', 'ORG', 'LOC', 'DATE', 'GPE', 'EVENT']
    
    
                                                                              
                                                      
                                                                              
    
                                               
    MIN_VERACITY_SCORE = 10
    MAX_VERACITY_SCORE = 95
    
                                 
    WEIGHT_STRONG_CONFIRMATION = 1.0                              
    WEIGHT_PARTIAL_CONFIRMATION = 0.5                               
    WEIGHT_MENTION = 0.2                                      
    
                 
    PENALTY_NO_SOURCES = 0.8                                        
    PENALTY_CONTRADICTION = 0.6                                  
    PENALTY_VERY_RECENT = 0.9                                                              
    
    
                                                                              
                                      
                                                                              
    
                                                            
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]
    
                                     
    DEFAULT_HEADERS = {
        'User-Agent': USER_AGENTS[0],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    
                                                                              
           
                                                                              
    
                                    
    ENABLE_CACHE = True
    
                                            
    CACHE_EXPIRATION = 3600          
    
                              
    CACHE_DB_NAME = 'news_verifier_cache'
    
    
                                                                              
                                             
                                                                              
    
                                               
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 5))
    
                                             
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', 30))
    
    
                                                                              
                            
                                                                              
    
                                                                          
    SEARCH_MODE = os.getenv('SEARCH_MODE', 'auto')
    
                                                                        
    ENABLE_SEARCH_FALLBACK = os.getenv('ENABLE_SEARCH_FALLBACK', 'False').lower() == 'true'
    
                                                            
    SEARCH_METHODS_PRIORITY = ['serpapi', 'google_rss', 'googlesearch', 'direct']
    
                                           
    MAX_SEARCH_RESULTS = 3
    
                                                 
    SEARCH_DELAY = 1.5

    DEFAULT_SOURCE_RELIABILITY = 0.9

    SOURCE_PRIORITY_BOOSTS = {
        'G1': 0.05
    }

    G1_STRONG_CONFIRMATION_BONUS = 0.08

    G1_PARTIAL_CONFIRMATION_BONUS = 0.04
    
    
                                                                              
                                       
                                                                              
    
                                    
    SERPAPI_KEY = os.getenv('SERPAPI_KEY', None)
    
                                                          
    SERPAPI_REQUESTS_COUNT = 0
    SERPAPI_REQUESTS_LIMIT = 100                            
    
                                            
                                                        
    
    
                                                                              
                                    
                                                                              
    
    ERROR_MESSAGES = {
        'INVALID_JSON': 'Nenhum dado JSON foi enviado',
        'MISSING_FIELDS': "Campos obrigatórios: 'tipo'e 'conteudo'",
        'INVALID_TYPE': "Tipo deve ser 'url'ou 'texto'",
        'EMPTY_CONTENT': 'Conteúdo não pode estar vazio',
        'CONTENT_TOO_SHORT': f'Conteúdo muito curto para análise (mínimo {MIN_CONTENT_LENGTH} caracteres)',
        'URL_TOO_SHORT': f'URL muito curta. Informe o endereço completo (mínimo {MIN_URL_LENGTH} caracteres)',
        'URL_TOO_LONG': f'URL muito longa (máximo {MAX_URL_LENGTH} caracteres)',
        'CONTENT_TOO_LONG': f'Conteúdo muito longo (máximo {MAX_CONTENT_LENGTH} caracteres)',
        'INVALID_URL': 'URL inválida ou inacessível',
        'TIMEOUT': 'Tempo limite excedido durante a análise',
        'NO_CONTENT_EXTRACTED': 'Não foi possível extrair conteúdo da URL',
        'ALL_SOURCES_FAILED': 'Todas as fontes falharam. Tente novamente mais tarde',
        'INTERNAL_ERROR': 'Erro interno do servidor',
        'RATE_LIMIT_EXCEEDED': 'Limite de requisições excedido. Tente novamente mais tarde'
    }
    
    
                                                                              
                                            
                                                                              
    
    JUSTIFICATION_TEMPLATES = {
        'high_veracity': 'Informação amplamente confirmada por múltiplas fontes confiáveis.',
        'medium_veracity': 'Informação parcialmente confirmada. Algumas fontes mencionam o tema.',
        'low_veracity': 'Pouca ou nenhuma confirmação encontrada em fontes confiáveis.',
        'no_sources': 'Tema não encontrado em portais de notícias confiáveis. Possível desinformação.',
        'contradiction': 'ATENÇÃO: Fontes apresentam informações contraditórias sobre o tema.',
        'very_recent': 'Notícia muito recente. Aguarde confirmação de fontes estabelecidas.',
        'satire_detected': 'ATENÇÃO: Conteúdo possivelmente satírico ou humorístico.',
        'ambiguous': 'Conteúdo vago ou ambíguo, dificultando verificação precisa.'
    }
    
    
                                                                              
                                           
                                                                              
    
                                                          
    LOG_LEVEL = 'INFO'if ENV == 'production'else 'DEBUG'
    
                                  
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    
                                                                              
                                
                                                                              
    
                                               
    CUSTOM_STOPWORDS = [
        'disse', 'afirmou', 'anunciou', 'informou', 'segundo',
        'acordo', 'através', 'ainda', 'apenas', 'assim',
        'hoje', 'ontem', 'amanhã', 'agora', 'então'
    ]
    
                                          
    SATIRE_INDICATORS = [
        'sensacionalista', 'piauí herald', 'the piauí',
        'infake news', 'velho oeste', 'satiria'
    ]


                                                                              
                                        
                                                                              

class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento"""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Configurações para ambiente de produção"""
    DEBUG = False
    ENV = 'production'
                                                             
    PROPAGATE_EXCEPTIONS = False


class TestingConfig(Config):
    """Configurações para testes"""
    TESTING = True
    DEBUG = True
                                     
    REQUEST_TIMEOUT = 2
    SCRAPING_TIMEOUT = 3


                                                                              
                                    
                                                                              

                                                     
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

                                                          
current_config = config_by_name.get(
    os.getenv('FLASK_ENV', 'development'),
    DevelopmentConfig
)


                                                                              
                                          
                                                                              

def get_config():
    """
    Retorna a configuração atual do sistema.
    
    Returns:
        Config: Objeto de configuração (DevelopmentConfig, ProductionConfig, etc)
    
    Exemplo:
        from config import get_config
        config = get_config()
        print(config.TRUSTED_SOURCES)
    """
    return current_config


                                                                              
                            
                                                                              

def validate_config():
    """
    Valida se todas as configurações necessárias estão corretas.
    Útil para rodar na inicialização e detectar problemas.
    
    Returns:
        tuple: (bool, list) - (sucesso, lista de erros)
    """
    errors = []
    
                      
    if Config.REQUEST_TIMEOUT < 1:
        errors.append("REQUEST_TIMEOUT deve ser >= 1 segundo")
    
    if Config.MIN_CONTENT_LENGTH < 10:
        errors.append("MIN_CONTENT_LENGTH deve ser >= 10 caracteres")

    if Config.MIN_URL_LENGTH < 5:
        errors.append("MIN_URL_LENGTH deve ser >= 5 caracteres")

    if Config.MAX_CONTENT_LENGTH < Config.MIN_CONTENT_LENGTH:
        errors.append("MAX_CONTENT_LENGTH deve ser maior que MIN_CONTENT_LENGTH")
    
                    
    if not (0 <= Config.MIN_VERACITY_SCORE < Config.MAX_VERACITY_SCORE <= 100):
        errors.append("MIN_VERACITY_SCORE e MAX_VERACITY_SCORE devem estar entre 0-100")
    
                                        
    if not (0 <= Config.SIMILARITY_THRESHOLD_LOW < Config.SIMILARITY_THRESHOLD_MEDIUM < Config.SIMILARITY_THRESHOLD_HIGH <= 1):
        errors.append("Thresholds de similaridade devem estar em ordem crescente entre 0-1")
    
                               
    if len(Config.TRUSTED_SOURCES) == 0:
        errors.append("Deve haver pelo menos uma fonte confiável configurada")
    
    return (len(errors) == 0, errors)


                                                                              
                                                            
                                                                              

if __name__ == "__main__":
                           
    success, errors = validate_config()
    
    if success:
        print("Todas as configurações estão corretas!")
        print(f"\n Ambiente: {current_config.ENV}")
        print(f"Debug: {current_config.DEBUG}")
        print(f"Fontes confiáveis: {len(current_config.TRUSTED_SOURCES)}")
        print(f"Timeout de requisições: {current_config.REQUEST_TIMEOUT}s")
    else:
        print("Erros encontrados nas configurações:")
        for error in errors:
            print(f"  - {error}")