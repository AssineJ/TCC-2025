"""
extractor.py - Módulo de Extração de Conteúdo (Melhorado)

Responsabilidade:
    Extrair conteúdo textual de URLs de notícias com múltiplas estratégias:
    1. newspaper3k (principal)
    2. trafilatura (fallback 1)
    3. AMP pages (fallback 2)
    4. readability (fallback 3)
    5. Globo-specific (fallback específico)
    6. BeautifulSoup genérico (último recurso)

Autor: Projeto Acadêmico
Data: 2025
"""

import requests
from newspaper import Article
from bs4 import BeautifulSoup
import validators
from datetime import datetime
from config import Config
import time
import random

                   
try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False
    print("  trafilatura não disponível")

try:
    from readability import Document
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False
    print("  readability-lxml não disponível")


class ContentExtractor:
    """Extrator com múltiplas estratégias de fallback."""
    
    def __init__(self):
        self.timeout = Config.REQUEST_TIMEOUT
        self.headers = Config.DEFAULT_HEADERS.copy()
        self.retry_attempts = Config.MAX_RETRIES
        self.retry_delay = Config.RETRY_DELAY
    
    def extract(self, url):
        """Extrai conteúdo com 6 estratégias de fallback."""
        
                     
        if not self._validar_url(url):
            return self._resultado_erro(url, 'URL inválida')
        
                    
        html = self._obter_html(url)
        if not html:
            return self._resultado_erro(url, 'Não foi possível obter HTML')
        
        melhor_resultado = None
        melhor_tamanho = 0
        
                                   
        resultado = self._extrair_newspaper(url)
        if resultado['sucesso']:
            tamanho = len(resultado['texto'].split())
            if tamanho >= 80:
                return resultado
            melhor_resultado = resultado
            melhor_tamanho = tamanho
        
                                   
        if TRAFILATURA_AVAILABLE:
            print("  Tentando trafilatura...")
            resultado = self._extrair_trafilatura(html, url)
            if resultado['sucesso']:
                tamanho = len(resultado['texto'].split())
                if tamanho > melhor_tamanho:
                    if tamanho >= 80:
                        return resultado
                    melhor_resultado = resultado
                    melhor_tamanho = tamanho
        
                           
        print("  Tentando AMP...")
        resultado = self._extrair_amp(html, url)
        if resultado['sucesso']:
            tamanho = len(resultado['texto'].split())
            if tamanho > melhor_tamanho:
                if tamanho >= 80:
                    return resultado
                melhor_resultado = resultado
                melhor_tamanho = tamanho
        
                                   
        if READABILITY_AVAILABLE:
            print("  Tentando readability...")
            resultado = self._extrair_readability(html, url)
            if resultado['sucesso']:
                tamanho = len(resultado['texto'].split())
                if tamanho > melhor_tamanho:
                    if tamanho >= 80:
                        return resultado
                    melhor_resultado = resultado
                    melhor_tamanho = tamanho
        
                                      
        if 'globo.com'in url.lower():
            print("  Site Globo, tentando extrator específico...")
            resultado = self._extrair_globo(html, url)
            if resultado['sucesso']:
                tamanho = len(resultado['texto'].split())
                if tamanho > melhor_tamanho:
                    if tamanho >= 80:
                        return resultado
                    melhor_resultado = resultado
                    melhor_tamanho = tamanho
        
                                              
        print("  Tentando BeautifulSoup genérico...")
        resultado = self._extrair_beautifulsoup(url, html)
        if resultado['sucesso']:
            tamanho = len(resultado['texto'].split())
            if tamanho > melhor_tamanho:
                melhor_resultado = resultado
                melhor_tamanho = tamanho
        
        return melhor_resultado or self._resultado_erro(url, 'Todas estratégias falharam')
    
    def _validar_url(self, url):
        """Valida se URL está no formato correto."""
        if not url:
            return False
        if not validators.url(url):
            return False
        if not url.startswith(('http://', 'https://')):
            return False
        return True
    
    def _obter_html(self, url):
        """Obtém HTML com retry."""
        for tentativa in range(self.retry_attempts):
            try:
                headers = self.headers.copy()
                headers['User-Agent'] = random.choice(Config.USER_AGENTS)
                response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
                response.raise_for_status()
                return response.text
            except Exception:
                if tentativa < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
        return ""
    
    def _extrair_newspaper(self, url):
        """Extração com newspaper3k."""
        for tentativa in range(self.retry_attempts):
            try:
                article = Article(url, language='pt')
                article.config.request_timeout = self.timeout
                article.config.headers = self.headers
                article.download()
                article.parse()
                
                titulo = article.title
                texto = article.text
                
                if not titulo or not texto or len(texto.split()) < 20:
                    raise Exception("Conteúdo insuficiente")
                
                data = article.publish_date.strftime('%Y-%m-%d') if article.publish_date else None
                autor = article.authors[0] if article.authors else None
                
                return {
                    'url': url, 'titulo': titulo.strip(), 'texto': texto.strip(),
                    'data_publicacao': data, 'autor': autor,
                    'metodo_extracao': 'newspaper3k', 'sucesso': True, 'erro': None
                }
            except Exception as e:
                if tentativa < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
        
        return self._resultado_erro(url, 'newspaper3k falhou', 'newspaper3k')
    
    def _extrair_trafilatura(self, html, url):
        """Extração com trafilatura."""
        try:
            metadata = trafilatura.extract_metadata(html, url=url)
            content = trafilatura.extract(html, include_comments=False, include_formatting=False, favor_recall=True, url=url)
            titulo = metadata.title if metadata and hasattr(metadata, 'title') else ""
            texto = content or ""
            
            if not texto or len(texto.split()) < 20:
                raise Exception("Texto insuficiente")
            
            return {
                'url': url, 'titulo': (titulo or "").strip(), 'texto': texto.strip(),
                'data_publicacao': None, 'autor': None,
                'metodo_extracao': 'trafilatura', 'sucesso': True, 'erro': None
            }
        except Exception as e:
            return self._resultado_erro(url, f'trafilatura: {e}', 'trafilatura')
    
    def _extrair_amp(self, html, url):
        """Extração de versão AMP."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            amp_link = soup.find('link', rel=lambda x: x and 'amphtml'in str(x).lower())
            
            if amp_link and amp_link.get('href'):
                amp_url = amp_link['href']
                if amp_url.startswith('/'):
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    amp_url = f"{parsed.scheme}://{parsed.netloc}{amp_url}"
                
                amp_html = self._obter_html(amp_url)
                if amp_html and TRAFILATURA_AVAILABLE:
                    return self._extrair_trafilatura(amp_html, amp_url)
            
            raise Exception("AMP não encontrado")
        except Exception as e:
            return self._resultado_erro(url, f'AMP: {e}', 'amp')
    
    def _extrair_readability(self, html, url):
        """Extração com readability."""
        try:
            doc = Document(html)
            titulo = (doc.short_title() or "").strip()
            summary_html = doc.summary(html_partial=True)
            soup = BeautifulSoup(summary_html, 'lxml')
            texto = soup.get_text("\n").strip()
            
            if not texto or len(texto.split()) < 20:
                raise Exception("Texto insuficiente")
            
            return {
                'url': url, 'titulo': titulo, 'texto': texto,
                'data_publicacao': None, 'autor': None,
                'metodo_extracao': 'readability', 'sucesso': True, 'erro': None
            }
        except Exception as e:
            return self._resultado_erro(url, f'readability: {e}', 'readability')
    
    def _extrair_globo(self, html, url):
        """Extrator específico para Globo."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            titulo = soup.find('h1').get_text(" ", strip=True) if soup.find('h1') else ""
            
            body = soup.find(attrs={"itemprop": "articleBody"})
            if not body:
                body = soup.find('article')
            if not body:
                body = soup.select_one("div[class*='content-text'], div[class*='mc-body']")
            
            if not body:
                raise Exception("Corpo não encontrado")
            
            paragrafos = [t.get_text(" ", strip=True) for t in body.find_all(['p', 'li']) if len(t.get_text(strip=True)) > 20]
            texto = "\n\n".join(paragrafos).strip()
            
            if not texto or len(texto.split()) < 20:
                raise Exception("Texto insuficiente")
            
            return {
                'url': url, 'titulo': titulo, 'texto': texto,
                'data_publicacao': None, 'autor': None,
                'metodo_extracao': 'globo_specific', 'sucesso': True, 'erro': None
            }
        except Exception as e:
            return self._resultado_erro(url, f'globo: {e}', 'globo_specific')
    
    def _extrair_beautifulsoup(self, url, html=None):
        """Extração genérica com BeautifulSoup."""
        for tentativa in range(self.retry_attempts):
            try:
                if not html:
                    html = self._obter_html(url)
                    if not html:
                        raise Exception("HTML vazio")
                
                soup = BeautifulSoup(html, 'lxml')
                
                        
                titulo = None
                meta_title = soup.find('meta', property='og:title')
                if meta_title and meta_title.get('content'):
                    titulo = meta_title.get('content')
                if not titulo:
                    title_tag = soup.find('title')
                    if title_tag:
                        titulo = title_tag.get_text()
                if not titulo:
                    h1 = soup.find('h1')
                    if h1:
                        titulo = h1.get_text()
                
                       
                texto = None
                article_tag = soup.find('article')
                if article_tag:
                    paragrafos = article_tag.find_all('p')
                    texto = '\n\n'.join([p.get_text().strip() for p in paragrafos if p.get_text().strip()])
                
                if not texto or len(texto.split()) < 20:
                    content_divs = soup.find_all('div', class_=['content', 'article-content', 'post-content', 'entry-content'])
                    for div in content_divs:
                        paragrafos = div.find_all('p')
                        texto_temp = '\n\n'.join([p.get_text().strip() for p in paragrafos if p.get_text().strip()])
                        if len(texto_temp.split()) > len((texto or '').split()):
                            texto = texto_temp
                
                if not texto or len(texto.split()) < 20:
                    paragrafos = soup.find_all('p')
                    texto = '\n\n'.join([p.get_text().strip() for p in paragrafos if len(p.get_text().strip()) > 50])
                
                if not titulo or not texto or len(texto.split()) < 20:
                    raise Exception("Conteúdo insuficiente")
                
                return {
                    'url': url, 'titulo': titulo.strip(), 'texto': texto.strip()[:Config.MAX_CONTENT_LENGTH],
                    'data_publicacao': None, 'autor': None,
                    'metodo_extracao': 'beautifulsoup', 'sucesso': True, 'erro': None
                }
            
            except Exception as e:
                if tentativa < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
        
        return self._resultado_erro(url, 'BeautifulSoup falhou', 'beautifulsoup')
    
    def _resultado_erro(self, url, erro, metodo=None):
        """Retorna resultado de erro padronizado."""
        return {
            'url': url, 'titulo': None, 'texto': None,
            'data_publicacao': None, 'autor': None,
            'metodo_extracao': metodo, 'sucesso': False, 'erro': erro
        }


def extrair_conteudo(url):
    """Função de conveniência."""
    extractor = ContentExtractor()
    return extractor.extract(url)


if __name__ == "__main__":
    print("=" * 70)
    print("TESTE DO EXTRACTOR MELHORADO")
    print("=" * 70)
    print()
    
    urls = [
        "https://g1.globo.com/",
        "https://istoe.com.br/"
    ]
    
    for url in urls:
        print(f"Testando: {url}")
        resultado = extrair_conteudo(url)
        if resultado['sucesso']:
            print(f"Sucesso ({resultado['metodo_extracao']})")
            print(f"   {len(resultado['texto'])} caracteres")
        else:
            print(f"Falhou: {resultado['erro']}")
        print()