"""
nlp_processor.py - Módulo de Processamento de Linguagem Natural

VERSÃO CORRIGIDA - Aceita título opcional para melhorar query

Autor: Projeto Acadêmico
Data: 2025
"""

import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import re
from config import Config


                                                     
_nlp_model = None
_stopwords_pt = None


def _carregar_spacy():
    """Carrega o modelo spaCy apenas uma vez (lazy loading)."""
    global _nlp_model
    
    if _nlp_model is None:
        print("Carregando modelo spaCy (pt_core_news_lg)...")
        try:
            _nlp_model = spacy.load(Config.SPACY_MODEL)
            print("Modelo spaCy carregado!")
        except OSError:
            print("ERRO: Modelo spaCy não encontrado!")
            print("Execute: python -m spacy download pt_core_news_lg")
            raise
    
    return _nlp_model


def _carregar_stopwords():
    """Carrega stopwords do NLTK + customizadas."""
    global _stopwords_pt
    
    if _stopwords_pt is None:
        print("Carregando stopwords...")
        try:
            nltk_stopwords = set(stopwords.words('portuguese'))
            custom_stopwords = set(Config.CUSTOM_STOPWORDS)
            _stopwords_pt = nltk_stopwords.union(custom_stopwords)
            print(f" {len(_stopwords_pt)} stopwords carregadas!")
        except LookupError:
            print("ERRO: Stopwords do NLTK não encontradas!")
            print("Execute: python -c \"import nltk; nltk.download('stopwords')\"")
            raise
    
    return _stopwords_pt


class NLPProcessor:
    """Classe responsável por processar texto usando IA."""
    
    def __init__(self):
        """Inicializa processador com modelos de IA"""
        self.nlp = _carregar_spacy()
        self.stopwords = _carregar_stopwords()
    
    
    def processar(self, texto, titulo=None):
        """
        Processa texto completo e extrai todas as informações.
        
        Args:
            texto (str): Texto da notícia
            titulo (str, optional): Título da notícia (melhora a query)
            
        Returns:
            dict: Informações extraídas
        """
                       
        texto_limpo = self._limpar_texto(texto)
        titulo_limpo = self._limpar_texto(titulo) if titulo else None
        
                             
        print("Processando texto com IA (spaCy)...")
        doc = self.nlp(texto_limpo)
        
                                                     
        entidades = self._extrair_entidades(doc)
        palavras_chave = self._extrair_palavras_chave(doc)
        
                                           
        if titulo_limpo:
            doc_titulo = self.nlp(titulo_limpo)
            entidades_titulo = self._extrair_entidades(doc_titulo)
            palavras_titulo = self._extrair_palavras_chave(doc_titulo)
            
                                            
            query_busca = self._gerar_query_com_titulo(
                entidades_titulo, palavras_titulo,
                entidades, palavras_chave
            )
        else:
                                          
            query_busca = self._gerar_query(entidades, palavras_chave)
        
                           
        texto_sem_stopwords = self._remover_stopwords(texto_limpo)
        
                      
        estatisticas = {
            'total_tokens': len(doc),
            'total_entidades': len(entidades),
            'total_palavras_chave': len(palavras_chave),
            'tamanho_texto_original': len(texto),
            'tamanho_texto_limpo': len(texto_limpo)
        }
        
        return {
            'entidades': entidades,
            'palavras_chave': palavras_chave,
            'query_busca': query_busca,
            'texto_limpo': texto_sem_stopwords,
            'estatisticas': estatisticas
        }
    
    
    def _limpar_texto(self, texto):
        """Limpa texto removendo caracteres especiais."""
        if not texto:
            return ""
        
        texto = re.sub(r'http\S+|www\S+', '', texto)
        texto = re.sub(r'\S+@\S+', '', texto)
        texto = re.sub(r'\s+', ' ', texto)
        texto = texto.strip()
        return texto
    
    
    def _extrair_entidades(self, doc):
        """Extrai entidades nomeadas usando spaCy."""
        entidades = []
        
        for ent in doc.ents:
            if ent.label_ in Config.ENTITY_TYPES:
                entidades.append({
                    'texto': ent.text,
                    'tipo': ent.label_,
                    'importancia': self._calcular_importancia_entidade(ent)
                })
        
                            
        entidades_unicas = {}
        for ent in entidades:
            texto_lower = ent['texto'].lower()
            if texto_lower not in entidades_unicas or ent['importancia'] > entidades_unicas[texto_lower]['importancia']:
                entidades_unicas[texto_lower] = ent
        
        entidades = list(entidades_unicas.values())
        entidades.sort(key=lambda x: x['importancia'], reverse=True)
        entidades = entidades[:Config.MAX_ENTITIES]
        
        return entidades
    
    
    def _calcular_importancia_entidade(self, ent):
        """Calcula importância de uma entidade."""
        posicao_relativa = ent.start / len(ent.doc) if len(ent.doc) > 0 else 0
        importancia_posicao = 1 - (posicao_relativa * 0.5)
        tamanho = len(ent.text.split())
        importancia_tamanho = min(tamanho / 3, 1.0)
        importancia = (importancia_posicao * 0.7) + (importancia_tamanho * 0.3)
        return round(importancia, 2)
    
    
    def _extrair_palavras_chave(self, doc):
        """Extrai palavras-chave relevantes."""
        palavras_relevantes = []
        
        for token in doc:
            if (not token.is_stop and 
                token.pos_ in ['NOUN', 'VERB', 'PROPN', 'ADJ'] and
                len(token.text) >= 3 and
                token.is_alpha):
                
                palavra = token.lemma_.lower()
                palavras_relevantes.append(palavra)
        
        contador = Counter(palavras_relevantes)
        palavras_chave = [palavra for palavra, freq in contador.most_common(Config.MAX_KEYWORDS)]
        
        return palavras_chave
    
    
    def _gerar_query_com_titulo(self, entidades_titulo, palavras_titulo, entidades_texto, palavras_texto):
        """
        Gera query priorizando informações do título.
        Título tem mais peso por ser mais específico e relevante.
        """
                          
        top_ent_titulo = [e['texto'] for e in entidades_titulo[:2]]
        top_pal_titulo = palavras_titulo[:3]
        
                                
        top_ent_texto = [e['texto'] for e in entidades_texto[:1]]
        top_pal_texto = palavras_texto[:2]
        
                                    
        termos = top_ent_titulo + top_pal_titulo + top_ent_texto + top_pal_texto
        
                                           
        termos_unicos = []
        for termo in termos:
            if termo.lower() not in [t.lower() for t in termos_unicos]:
                termos_unicos.append(termo)
        
                            
        query = ' '.join(termos_unicos[:6])
        return query
    
    
    def _gerar_query(self, entidades, palavras_chave):
        """Gera query apenas com informações do texto."""
        top_entidades = [ent['texto'] for ent in entidades[:3]]
        top_palavras = palavras_chave[:5]
        
        termos_busca = top_entidades + top_palavras
        
                            
        termos_unicos = []
        for termo in termos_busca:
            if termo.lower() not in [t.lower() for t in termos_unicos]:
                termos_unicos.append(termo)
        
        termos_unicos = termos_unicos[:6]
        query = ' '.join(termos_unicos)
        return query
    
    
    def _remover_stopwords(self, texto):
        """Remove stopwords do texto."""
        palavras = word_tokenize(texto.lower(), language='portuguese')
        palavras_filtradas = [
            palavra for palavra in palavras 
            if palavra.isalpha() and palavra not in self.stopwords and len(palavra) >= 3
        ]
        texto_filtrado = ' '.join(palavras_filtradas)
        return texto_filtrado


def processar_texto(texto, titulo=None):
    """
    Função simplificada para processar texto.
    
    Args:
        texto (str): Texto a processar
        titulo (str, optional): Título para melhorar query
        
    Returns:
        dict: Resultado do processamento
    """
    processor = NLPProcessor()
    return processor.processar(texto, titulo)


if __name__ == "__main__":
    print("=" * 70)
    print("TESTANDO MÓDULO NLP PROCESSOR")
    print("=" * 70)
    print()
    
    texto_teste = """
    O presidente Luiz Inácio Lula da Silva anunciou ontem em Brasília uma 
    importante reforma tributária que reduzirá os impostos sobre alimentos 
    básicos em todo o Brasil.
    """
    
    titulo_teste = "Lula anuncia reforma tributária em Brasília"
    
    print("Texto de teste:")
    print(texto_teste.strip())
    print()
    print(f"Título: {titulo_teste}")
    print()
    
                       
    print("Teste 1: COM título")
    print("-" * 70)
    resultado = processar_texto(texto_teste, titulo=titulo_teste)
    print(f"Query gerada: {resultado['query_busca']}")
    print()
    
                       
    print("Teste 2: SEM título")
    print("-" * 70)
    resultado2 = processar_texto(texto_teste)
    print(f"Query gerada: {resultado2['query_busca']}")
    print()
    
    print("Testes concluídos!")