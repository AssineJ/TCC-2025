                     
from __future__ import annotations

import os
import re
import time
import json
import hashlib
import random
import unicodedata
from dataclasses import dataclass
from collections import Counter
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

from config import Config

                               
                                    
                               
try:
    from serpapi import GoogleSearch                         
    SERPAPI_AVAILABLE = True
except Exception:
    SERPAPI_AVAILABLE = False

try:
                         
    from googlesearch import search as google_search
    GSEARCH_AVAILABLE = True
except Exception:
    GSEARCH_AVAILABLE = False


                                                              
                                                    
                                                              

def _cache_dir() -> str:
    d = os.path.join(".cache", "search")
    os.makedirs(d, exist_ok=True)
    return d

def _cache_key(query: str, site: str) -> str:
    key_str = f"{query}||{site}".lower().strip()
    return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

def _cache_path(query: str, site: str) -> str:
    return os.path.join(_cache_dir(), f"{_cache_key(query, site)}.json")

def cache_get(query: str, site: str) -> Optional[List[Dict[str, Any]]]:
    if not Config.ENABLE_CACHE:
        return None
    path = _cache_path(query, site)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
                   
        ttl = getattr(Config, "CACHE_EXPIRATION", 3600)
        if time.time() - payload.get("_ts", 0) > ttl:
            return None
        return payload.get("results", None)
    except Exception:
        return None

def cache_set(query: str, site: str, results: List[Dict[str, Any]]) -> None:
    if not Config.ENABLE_CACHE:
        return
    path = _cache_path(query, site)
    payload = {"_ts": time.time(), "results": results}
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


                                                              
                            
                                                              

def _norm_result(title: str, url: str, snippet: str = "") -> Dict[str, Any]:
    return {
        "title": title.strip() if title else "",
        "url": url.strip() if url else "",
        "snippet": snippet.strip() if snippet else ""
    }

def _clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s


STOPWORDS_PT = {
    "a", "o", "os", "as", "um", "uma", "uns", "umas", "de", "da", "do",
    "das", "dos", "para", "por", "com", "sem", "em", "no", "na", "nos",
    "nas", "sobre", "entre", "que", "quem", "onde", "quando", "como",
    "porque", "porquê", "porque", "qual", "quais", "se", "e", "ou", "mas",
    "ser", "sera", "será", "foi", "era", "sao", "são", "tem", "têm", "ter",
    "vai", "serao", "serão", "este", "esta", "estes", "estas", "isso", "isto",
    "aquele", "aquela", "aqueles", "aquelas", "dessa", "desse", "deste", "desta",
    "pelo", "pela", "pelos", "pelas", "ja", "já", "ainda", "muito", "muita",
    "muitos", "muitas", "mais", "menos", "desde", "apos", "após", "ate", "até",
    "sua", "seu", "suas", "seus", "segundo", "seg", "contra", "pode", "podem",
    "podera", "poderá", "deve", "devem", "ha", "há", "houve", "foram", "novo",
    "nova", "novos", "novas", "antes"
}


def _normalize_for_match(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _tokenize_keywords(query: str) -> List[str]:
    normalized = _normalize_for_match(query)
    if not normalized:
        return []
    tokens = [t for t in normalized.split() if len(t) > 2 and t not in STOPWORDS_PT]
    if not tokens:
        return normalized.split()
    freq = Counter(tokens)
    ordered = [token for token, _ in freq.most_common()]
    return ordered


def _extract_focus_phrases(query: str, keywords: List[str]) -> Tuple[List[str], List[str]]:
    """Identifica expressões relevantes do texto original e combinações de keywords."""

    raw_phrases: List[str] = []
    norm_phrases: List[str] = []

    base = _clean_text(query)
    if base:
                                                                     
        padrao = r"((?:[A-ZÁÂÃÀÉÊÍÓÔÕÚÜ][\wÁ-ú]+(?:\s+[A-ZÁÂÃÀÉÊÍÓÔÕÚÜ][\wÁ-ú]+)+))"
        for match in re.finditer(padrao, query):
            trecho = match.group(1).strip()
            if len(trecho.split()) > 1 and len(trecho.split()) <= 6:
                raw_phrases.append(trecho)
                norm = _normalize_for_match(trecho)
                if norm:
                    norm_phrases.append(norm)

                                                                
    for tamanho in range(min(4, len(keywords)), 1, -1):
        for idx in range(0, len(keywords) - tamanho + 1):
            trecho = " ".join(keywords[idx : idx + tamanho])
            if len(trecho) < 5:
                continue
            if trecho not in raw_phrases:
                raw_phrases.append(trecho)
            norm = _normalize_for_match(trecho)
            if norm and norm not in norm_phrases:
                norm_phrases.append(norm)

                                         
    def _unique(seq: List[str]) -> List[str]:
        vistos = set()
        saida = []
        for item in seq:
            if item in vistos:
                continue
            vistos.add(item)
            saida.append(item)
        return saida

    return _unique(raw_phrases), _unique(norm_phrases)


def _gerar_variacoes_query(query: str, keywords: List[str], focus_phrases: List[str]) -> List[str]:
    variantes: List[str] = []
    base = _clean_text(query)
    if base:
        variantes.append(base)

    if keywords:
        palavras_principais = " ".join(keywords[:4]).strip()
        if palavras_principais and palavras_principais not in variantes:
            variantes.append(palavras_principais)
        if len(keywords) >= 2:
            frase = " \"" + " ".join(keywords[:2]) + "\""
            frase = frase.strip()
            if frase and frase not in variantes:
                variantes.append(frase)

    for frase in focus_phrases[:5]:
        frase_limpa = _clean_text(frase)
        if frase_limpa and frase_limpa not in variantes:
            variantes.append(frase_limpa)
        quoted = f'"{frase_limpa}"'if frase_limpa else ""
        if quoted and quoted not in variantes:
            variantes.append(quoted)

    return variantes or ([base] if base else [])


def _rank_results_by_keywords(
    results: List[Dict[str, Any]],
    keywords: List[str],
    query_norm: str,
    focus_phrases_norm: List[str],
    limit: int,
) -> List[Dict[str, Any]]:
    if not results:
        return []

    if not keywords:
        return results[:limit]

    scored = []
    total_keywords = len(keywords)
    query_tokens = set(query_norm.split()) if query_norm else set()

    for res in results:
        texto = f"{res.get('title', '')} {res.get('snippet', '')}"
        texto_norm = _normalize_for_match(texto)
        if not texto_norm:
            continue

        matches = sum(1 for kw in keywords if kw in texto_norm)
        if matches == 0:
            continue

        cobertura = matches / total_keywords if total_keywords else 0.0
        overlap_tokens = 0.0
        if query_tokens:
            tokens_resultado = set(texto_norm.split())
            overlap_tokens = len(tokens_resultado & query_tokens) / len(query_tokens)

        frase_hits = sum(1 for frase in focus_phrases_norm if frase in texto_norm)

        snippet_bonus = 0.05 if res.get("snippet") else 0.0

        titulo = _normalize_for_match(res.get("title", ""))
        title_overlap = 0.0
        if titulo and query_tokens:
            tokens_titulo = set(titulo.split())
            if tokens_titulo:
                title_overlap = len(tokens_titulo & query_tokens) / len(tokens_titulo)

        ano_bonus = 0.0
        ano_query = re.findall(r"20\d{2}", query_norm)
        if ano_query:
            ano_resultado = re.findall(r"20\d{2}", texto)
            if any(a in ano_resultado for a in ano_query):
                ano_bonus = 0.05

        base_score = (cobertura * 0.55) + (overlap_tokens * 0.2) + (title_overlap * 0.15)
        frase_bonus = min(frase_hits * 0.08, 0.16)
        score = base_score + frase_bonus + snippet_bonus + ano_bonus

        scored.append((score, cobertura, matches, res))

    if not scored:
        return results[:limit]

    scored.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    ordenados: List[Dict[str, Any]] = []
    for _, _, _, res in scored:
        if not any(res.get("url") and res.get("url") == existente.get("url") for existente in ordenados):
            ordenados.append(res)
        if len(ordenados) >= limit:
            break

    return ordenados


                                                              
                              
                                                              

@dataclass
class SearchEngine:
    headers: Dict[str, str] = None
    max_per_source: int = Config.MAX_RESULTS_PER_SOURCE
    delay_between: float = getattr(Config, "SEARCH_DELAY", 1.0)

    def __post_init__(self):
        if self.headers is None:
            self.headers = dict(Config.DEFAULT_HEADERS)

                                         

    def buscar(self, query: str, dominio: str) -> List[Dict[str, Any]]:
        """Busca resultados para um domínio específico."""
        query = _clean_text(query)
        if not query or not dominio:
            return []

        keywords = _tokenize_keywords(query)
        focus_raw, focus_norm = _extract_focus_phrases(query, keywords)
        query_norm = _normalize_for_match(query)

        cached = cache_get(query, dominio)
        if cached is not None:
            return _rank_results_by_keywords(cached, keywords, query_norm, focus_norm, self.max_per_source)

        methods = getattr(Config, "SEARCH_METHODS_PRIORITY", ["serpapi", "googlesearch", "direct"])
        methods = list(dict.fromkeys(list(methods) + ["google_rss"]))
        mode = getattr(Config, "SEARCH_MODE", "mock").lower()

        variantes = _gerar_variacoes_query(query, keywords, focus_raw)
        max_coleta = max(self.max_per_source * 3, 6)
        resultados_final: List[Dict[str, Any]] = []

        for variante in variantes:
            raw = cache_get(variante, dominio)
            if raw is None:
                raw = self._buscar_raw(variante, dominio, mode, methods, max_coleta)
                cache_set(variante, dominio, raw)
            if not raw:
                raw = []

            ranqueados = _rank_results_by_keywords(raw, keywords, query_norm, focus_norm, max_coleta)
            for item in ranqueados:
                if not item.get("url"):
                    continue
                if not any(item["url"] == existente.get("url") for existente in resultados_final):
                    resultados_final.append(item)
                if len(resultados_final) >= self.max_per_source:
                    break
            if len(resultados_final) >= self.max_per_source:
                break

        if not resultados_final:
            raw_fallback = self._buscar_raw(query, dominio, mode, methods, max_coleta)
            if not raw_fallback:
                raw_fallback = []
            ranqueados_fallback = _rank_results_by_keywords(
                raw_fallback, keywords, query_norm, focus_norm, self.max_per_source
            )
            resultados_final = ranqueados_fallback or raw_fallback[: self.max_per_source]

        cache_set(query, dominio, resultados_final)
        time.sleep(self.delay_between)
        return resultados_final[: self.max_per_source]

                                               

    def _search_serpapi(self, query: str, dominio: str) -> List[Dict[str, Any]]:
        key = getattr(Config, "SERPAPI_KEY", None)
        if not SERPAPI_AVAILABLE or not key:
            return []
        params = {
            "engine": "google",
            "q": f"site:{dominio} " + query,
            "hl": "pt-BR",
            "num": max(5, self.max_per_source),
            "api_key": key
        }
        search = GoogleSearch(params)
        data = search.get_dict()
        out = []
        for item in data.get("organic_results", [])[: max(5, self.max_per_source)]:
            title = item.get("title", "")
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            if link and dominio in link:
                out.append(_norm_result(title, link, snippet))
        return out

    def _search_googlesearch(self, query: str, dominio: str) -> List[Dict[str, Any]]:
        if not GSEARCH_AVAILABLE:
            return []
                                                        
        q = f"site:{dominio} {query}"
        out = []
        try:
            for url in google_search(q, lang="pt", num=10, stop=10, pause=1.5):
                if dominio not in url:
                    continue
                title, snippet = self._fetch_title_snippet(url)
                out.append(_norm_result(title or url, url, snippet))
                if len(out) >= max(5, self.max_per_source):
                    break
        except Exception:
            pass
        return out

    def _search_google_rss(self, query: str, dominio: str) -> List[Dict[str, Any]]:
        """Consulta o RSS do Google News filtrando pelo domínio confiável."""

        rss_url = (
            "https://news.google.com/rss/search?q="
            + requests.utils.quote(f"site:{dominio} {query}")
            + "&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        )

        session = requests.Session()
        session.headers.update(self.headers)

        try:
            resp = session.get(rss_url, timeout=Config.REQUEST_TIMEOUT)
            if not resp.ok:
                return []

            soup = BeautifulSoup(resp.text, "xml")
            out: List[Dict[str, Any]] = []
            for item in soup.find_all("item"):
                link_tag = item.find("link")
                title_tag = item.find("title")
                if not link_tag or not title_tag:
                    continue
                link = link_tag.get_text(strip=True)
                title = title_tag.get_text(strip=True)
                if "url="in link:
                    m = re.search(r"url=(.*?)&", link)
                    if m:
                        link = requests.utils.unquote(m.group(1))
                if dominio not in link:
                    continue
                description = item.find("description")
                snippet = description.get_text(strip=True) if description else ""
                out.append(_norm_result(title, link, snippet))
                if len(out) >= max(6, self.max_per_source * 2):
                    break
            return out
        except Exception:
            return []

    def _search_direct(self, query: str, dominio: str) -> List[Dict[str, Any]]:
        """
        Tentativa simples: se a fonte tem 'url_busca'configurado, usa.
        Caso contrário, tenta homepage + filtro por query na âncora.
        """
        url_busca = None
        for f in Config.TRUSTED_SOURCES:
            if f.get("dominio") == dominio:
                url_busca = f.get("url_busca")
                break

        out = []
        session = requests.Session()
        session.headers.update(self.headers)

        try:
            if url_busca:
                resp = session.get(url_busca + requests.utils.quote(query), timeout=Config.REQUEST_TIMEOUT)
                if resp.ok:
                    out.extend(self._parse_links_from_html(resp.text, dominio))
            else:
                                    
                resp = session.get(f"https://{dominio}", timeout=Config.REQUEST_TIMEOUT)
                if resp.ok:
                    out.extend(self._parse_links_from_html(resp.text, dominio))

                                           
            final = []
            for r in out:
                title, snippet = self._fetch_title_snippet(r["url"], session=session)
                final.append(_norm_result(title or r["title"], r["url"], snippet))
                if len(final) >= max(5, self.max_per_source):
                    break
            return final
        except Exception:
            return []

    def _buscar_raw(self, query: str, dominio: str, mode: str,
                    methods: List[str], max_coleta: int) -> List[Dict[str, Any]]:
        resultados: List[Dict[str, Any]] = []

        modo = mode or "mock"
        modo = modo.lower()

        if modo == "mock":
            return self._mock_results(dominio, query)

        for metodo in methods:
            try:
                if metodo == "serpapi":
                    encontrados = self._search_serpapi(query, dominio)
                elif metodo == "googlesearch":
                    encontrados = self._search_googlesearch(query, dominio)
                elif metodo == "google_rss":
                    encontrados = self._search_google_rss(query, dominio)
                else:
                    encontrados = self._search_direct(query, dominio)
            except Exception:
                continue

            if not encontrados:
                continue

            for item in encontrados:
                if not item.get("url"):
                    continue
                if any(item["url"] == existente.get("url") for existente in resultados):
                    continue
                resultados.append(item)
                if len(resultados) >= max_coleta:
                    break

            if len(resultados) >= max_coleta:
                break

        if resultados:
            return resultados

        if modo in {"auto", "hybrid"} and getattr(Config, "ENABLE_SEARCH_FALLBACK", True):
            return self._mock_results(dominio, query)

        return resultados

                                             

    def _fetch_title_snippet(self, url: str, session: Optional[requests.Session] = None) -> (str, str):
        sess = session or requests.Session()
        sess.headers.update(self.headers)
        try:
            r = sess.get(url, timeout=Config.REQUEST_TIMEOUT, allow_redirects=True)
            if not r.ok:
                return "", ""
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("title").get_text(strip=True) if soup.find("title") else url
            ogdesc = soup.find("meta", attrs={"property": "og:description"})
            desc = ogdesc["content"] if ogdesc and ogdesc.get("content") else ""
            if not desc:
                mdesc = soup.find("meta", attrs={"name": "description"})
                desc = mdesc["content"] if mdesc and mdesc.get("content") else ""
            return _clean_text(title), _clean_text(desc)
        except Exception:
            return "", ""

    def _parse_links_from_html(self, html: str, dominio: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        out = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href.startswith("http"):
                continue
            if dominio not in href:
                continue
            title = a.get_text(" ", strip=True)[:120]
            out.append(_norm_result(title or href, href, ""))
            if len(out) >= 20:
                break
        return out

    def _mock_results(self, dominio: str, query: str) -> List[Dict[str, Any]]:
                                                                    
        base = f"https://{dominio}"
        seeds = [
            ("Matéria relacionada: " + query[:50], f"{base}/noticia-simulada-1", "Resumo simulado 1"),
            ("Análise sobre " + query[:40], f"{base}/noticia-simulada-2", "Resumo simulado 2"),
            ("Entrevista: " + query[:40], f"{base}/noticia-simulada-3", "Resumo simulado 3"),
        ]
        random.shuffle(seeds)
        return [_norm_result(t, u, s) for (t, u, s) in seeds[: self.max_per_source]]


                                                              
                                       
                                                              

def buscar_noticias(query_busca: str) -> Dict[str, Any]:
    """
    Realiza busca SEQUENCIAL nas fontes confiáveis e devolve
    um dicionário por fonte + metadata consolidada.
    """
    engine = SearchEngine()
    resultados: Dict[str, Any] = {}
    total = 0
    fontes_ok = 0

    fontes = [f for f in Config.TRUSTED_SOURCES if f.get("ativo", True)]

    for fonte in fontes:
        dominio = fonte["dominio"]
        nome = fonte["nome"]
        res = engine.buscar(query_busca, dominio) or []
        resultados[nome] = res
        if res:
            fontes_ok += 1
            total += len(res)

    resultados["metadata"] = {
        "total_resultados": total,
        "fontes_com_sucesso": fontes_ok,
        "total_fontes": len(fontes),
        "query_original": query_busca,
        "modo_busca": getattr(Config, "SEARCH_MODE", "mock")
    }
    return resultados


                                                              
                                     
                                                              

def _buscar_em_fonte(fonte: Dict[str, Any], query_busca: str) -> (str, List[Dict[str, Any]]):
    engine = SearchEngine()
    dominio = fonte.get("dominio")
    nome = fonte.get("nome", dominio)
    if not dominio:
        return nome, []
    res = engine.buscar(query_busca, dominio) or []
    return nome, res

def buscar_noticias_paralelo(query_busca: str) -> Dict[str, Any]:
    """
    Busca em TODAS as fontes simultaneamente, retornando no mesmo formato
    de buscar_noticias(), mas com 'modo_busca'indicando 'parallel/...'.
    """
    fontes = [f for f in Config.TRUSTED_SOURCES if f.get("ativo", True)]
    inicio = time.time()
    resultados: Dict[str, Any] = {}
    total = 0
    fontes_ok = 0

    max_workers = min(5, len(fontes) or 1)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_buscar_em_fonte, f, query_busca): f for f in fontes}
        for fut in as_completed(futures):
            nome, res = fut.result()
            resultados[nome] = res
            if res:
                fontes_ok += 1
                total += len(res)

    dur = time.time() - inicio
    resultados["metadata"] = {
        "total_resultados": total,
        "fontes_com_sucesso": fontes_ok,
        "total_fontes": len(fontes),
        "query_original": query_busca,
        "modo_busca": f"parallel/{getattr(Config, 'SEARCH_MODE', 'mock')}",
        "duracao_s": round(dur, 2)
    }
    return resultados


                                                              
                              
                                                              

if __name__ == "__main__":
    q = "Lula ONU FAO Roma"
    print("Teste de buscar_noticias()")
    out = buscar_noticias(q)
    print(json.dumps(out["metadata"], ensure_ascii=False, indent=2))
    for fonte, itens in out.items():
        if fonte == "metadata":
            continue
        print(f"\n== {fonte} ==")
        for it in itens:
            print("-", it["title"], "|", it["url"])

    print("\n Teste de buscar_noticias_paralelo()")
    outp = buscar_noticias_paralelo(q)
    print(json.dumps(outp["metadata"], ensure_ascii=False, indent=2))
