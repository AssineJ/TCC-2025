"""
contradiction_analyzer.py - Detecta se fontes contradizem a notícia

Este módulo usa análise de palavras-chave negativas e padrões linguísticos
para identificar quando uma fonte CONTRADIZ a informação verificada.

Autor: Projeto Acadêmico
Data: 2025
"""

import re
from typing import Dict, List

                                          
NEGATION_WORDS = [
    'não', 'nao', 'nunca', 'jamais', 'nenhum', 'nenhuma',
    'falso', 'falsa', 'mentira', 'fake', 'desmentido',
    'incorreto', 'incorreta', 'errado', 'errada',
    'sem comprovação', 'sem evidências', 'não comprovado',
    'boato', 'rumor', 'desinformação', 'fake news'
]

                                        
CONFIRMATION_WORDS = [
    'confirma', 'confirmou', 'comprova', 'comprovado',
    'verdadeiro', 'verdade', 'oficial', 'oficialmente',
    'anunciou', 'anunciado', 'declarou', 'afirmou'
]

                                
DEBUNK_PATTERNS = [
    r'é\s+falso',
    r'não\s+é\s+verdade',
    r'checagem.*falso',
    r'fact.*check.*falso',
    r'desmente.*',
    r'desmentiram.*',
    r'não\s+há\s+evidências',
    r'sem\s+comprovação'
]


def detectar_contradicao(texto_original: str, texto_fonte: str) -> Dict:
    """
    Analisa se o texto da fonte contradiz o texto original.
    
    Args:
        texto_original: Texto da notícia a ser verificada
        texto_fonte: Texto da fonte consultada
        
    Returns:
        Dict com:
        - contradiz (bool): Se há contradição
        - confianca (float): Confiança na detecção (0-1)
        - motivo (str): Explicação da detecção
        - palavras_negacao (list): Palavras de negação encontradas
    """
    
    texto_fonte_lower = texto_fonte.lower()
    texto_original_lower = texto_original.lower()
    
                                
    palavras_negacao_encontradas = []
    for word in NEGATION_WORDS:
        if word in texto_fonte_lower:
            palavras_negacao_encontradas.append(word)
    
                                     
    patterns_encontrados = []
    for pattern in DEBUNK_PATTERNS:
        if re.search(pattern, texto_fonte_lower):
            patterns_encontrados.append(pattern)
    
                                   
    score_contradicao = 0.0
    
                                               
    score_contradicao += min(len(palavras_negacao_encontradas) * 0.2, 1.0)
    
                                         
    score_contradicao += len(patterns_encontrados) * 0.5
    
                          
    score_contradicao = min(score_contradicao, 1.0)
    
                                          
    contradiz = score_contradicao >= 0.3
    
                  
    motivo = ""
    if contradiz:
        if patterns_encontrados:
            motivo = "Fonte contém padrões de desmentido"
        elif len(palavras_negacao_encontradas) >= 3:
            motivo = f"Múltiplas palavras de negação: {', '.join(palavras_negacao_encontradas[:3])}"
        else:
            motivo = "Indicadores de contradição detectados"
    else:
        motivo = "Sem contradição clara detectada"
    
    return {
        "contradiz": contradiz,
        "confianca": score_contradicao,
        "motivo": motivo,
        "palavras_negacao": palavras_negacao_encontradas,
        "patterns": patterns_encontrados
    }


def analisar_sentimento_fonte(texto_fonte: str, entidades_originais: List[str]) -> Dict:
    """
    Analisa o sentimento da fonte em relação às entidades da notícia original.
    
    Args:
        texto_fonte: Texto da fonte
        entidades_originais: Entidades mencionadas na notícia original
        
    Returns:
        Dict com análise de sentimento
    """
    
    texto_lower = texto_fonte.lower()
    
                                                     
    contextos_negativos = 0
    contextos_positivos = 0
    
    for entidade in entidades_originais:
        entidade_lower = entidade.lower()
        
                                           
        ocorrencias = [m.start() for m in re.finditer(re.escape(entidade_lower), texto_lower)]
        
        for pos in ocorrencias:
                                                        
            inicio = max(0, pos - 100)
            fim = min(len(texto_lower), pos + len(entidade_lower) + 100)
            contexto = texto_lower[inicio:fim]
            
                                                   
            neg_count = sum(1 for word in NEGATION_WORDS if word in contexto)
            pos_count = sum(1 for word in CONFIRMATION_WORDS if word in contexto)
            
            if neg_count > pos_count:
                contextos_negativos += 1
            elif pos_count > neg_count:
                contextos_positivos += 1
    
                               
    total = contextos_negativos + contextos_positivos
    if total == 0:
        sentimento = "neutro"
        confianca = 0.0
    elif contextos_negativos > contextos_positivos:
        sentimento = "negativo"
        confianca = contextos_negativos / total
    else:
        sentimento = "positivo"
        confianca = contextos_positivos / total
    
    return {
        "sentimento": sentimento,
        "confianca": confianca,
        "contextos_negativos": contextos_negativos,
        "contextos_positivos": contextos_positivos
    }


def ajustar_score_por_contradicao(
    score_original: float,
    analise_contradicao: Dict
) -> Dict:
    """
    Ajusta o score de veracidade baseado na análise de contradição.
    
    Args:
        score_original: Score calculado originalmente (0-100)
        analise_contradicao: Resultado de detectar_contradicao()
        
    Returns:
        Dict com score ajustado e justificativa
    """
    
    if not analise_contradicao["contradiz"]:
        return {
            "score_ajustado": score_original,
            "penalidade": 0,
            "justificativa": "Nenhuma contradição detectada"
        }
    
                                              
    confianca = analise_contradicao["confianca"]
    
                                            
    penalidade = int(confianca * 60)
    
                        
    score_ajustado = max(5, score_original - penalidade)             
    
    justificativa = f"ALERTA: Fontes contradizem a informação. {analise_contradicao['motivo']}. Score reduzido em {penalidade} pontos."
    
    return {
        "score_ajustado": score_ajustado,
        "penalidade": penalidade,
        "justificativa": justificativa
    }


                 
if __name__ == "__main__":
                                
    texto_fake = "Vacinas contra COVID-19 matam instantaneamente"
    texto_fonte = "É falso que vacinas contra COVID-19 causam morte instantânea. Não há evidências científicas."
    
    resultado = detectar_contradicao(texto_fake, texto_fonte)
    print("Teste 1 - Fake News:")
    print(f"  Contradiz: {resultado['contradiz']}")
    print(f"  Confiança: {resultado['confianca']:.2f}")
    print(f"  Motivo: {resultado['motivo']}")
    print()
    
                          
    texto_real = "Presidente anuncia aumento do salário mínimo"
    texto_fonte2 = "Presidente confirmou oficialmente o aumento do salário mínimo em coletiva"
    
    resultado2 = detectar_contradicao(texto_real, texto_fonte2)
    print("Teste 2 - Notícia Real:")
    print(f"  Contradiz: {resultado2['contradiz']}")
    print(f"  Confiança: {resultado2['confianca']:.2f}")
    print(f"  Motivo: {resultado2['motivo']}")
    print()
    
                              
    ajuste = ajustar_score_por_contradicao(49, resultado)
    print("Teste 3 - Ajuste de Score:")
    print(f"  Score original: 49%")
    print(f"  Score ajustado: {ajuste['score_ajustado']}%")
    print(f"  Penalidade: -{ajuste['penalidade']} pontos")
    print(f"  Justificativa: {ajuste['justificativa']}")