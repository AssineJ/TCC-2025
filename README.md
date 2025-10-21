# TCC-2025

# ConfereAí! — Sistema de Verificação de Notícias com IA

## Sumário
- [Visão geral](#visão-geral)
- [Arquitetura e fluxo de verificação](#arquitetura-e-fluxo-de-verificação)
- [Tecnologias e ferramentas](#tecnologias-e-ferramentas)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Configuração do ambiente](#configuração-do-ambiente)
  - [Backend (Flask)](#backend-flask)
  - [Guia rápido: venv do zero (CPU/GPU)](#guia-rápido-venv-do-zero-cpugpu)
  - [Frontend (React + Vite)](#frontend-react--vite)
- [Como executar](#como-executar)
  - [Subir a API](#subir-a-api)
  - [Rodar a interface web](#rodar-a-interface-web)
- [Uso da API](#uso-da-api)
- [Uso da interface web](#uso-da-interface-web)
- [Principais módulos do backend](#principais-módulos-do-backend)
- [Principais componentes do frontend](#principais-componentes-do-frontend)
- [Resolução de problemas e dicas](#resolução-de-problemas-e-dicas)

## Visão geral
O projeto **ConfereAí!** disponibiliza uma API Flask com recursos de NLP e busca semântica para verificar a veracidade de notícias e uma interface web em React para uso amigável. A API expõe endpoints REST, detalha o fluxo completo da checagem e fornece métricas de confiança, incluindo alerta para contradições encontradas nas fontes consultadas.

## Arquitetura e fluxo de verificação
O backend orquestra as etapas abaixo sempre que o endpoint `/api/verificar` recebe um conteúdo textual ou URL de notícia.

1. **Validação de entrada** — Garante que o corpo contenha `tipo` (`url` ou `texto`) e `conteudo`, além de respeitar limites mínimos/máximos definidos em `Config`.
2. **Extração de conteúdo** — Para URLs, baixa e interpreta a página antes de seguir; para texto puro, usa o texto enviado. A extração usa múltiplas estratégias de fallback (newspaper3k, trafilatura, AMP, readability, parser específico Globo e BeautifulSoup).
3. **Processamento NLP** — Limpa o texto, extrai entidades/palavras-chave e monta a consulta de busca usando spaCy e NLTK.
4. **Busca em fontes confiáveis** — Interroga portais configurados, com cache, diferentes estratégias e modo paralelo opcional.
5. **Filtros inteligentes** — Remove URLs com paywall, páginas genéricas ou sem correlação; replica a filtragem após o scraping.
6. **Scraping paralelo** — Extrai textos das URLs mantidas respeitando paywalls e reutilizando cache; há wrapper `scrape_noticias` que o app usa direto.
7. **Análise semântica & contradições** — Calcula similaridade via sentence-transformers, detecta padrões de desmentido, quantifica confirmações/parciais/menções e registra evidências de contradição.
8. **Cálculo de veracidade** — Converte a análise em percentual (10–95%), gera justificativa e nível de confiança, penalizando fortemente contradições.
9. **Resposta enriquecida** — Retorna resumo, fontes ranqueadas, estatísticas de NLP, detalhamento do score e metadados gerais.

## Tecnologias e ferramentas
### Backend (Python)
- Frameworks e utilitários: Flask, Flask-CORS, python-dotenv, logging com rotacionamento.
- Coleta de conteúdo: requests, newspaper3k, trafilatura, readability-lxml, BeautifulSoup, validators.
- NLP e IA: spaCy, NLTK, sentence-transformers, scikit-learn, torch, transformers, accelerate, sentencepiece.
- Busca e scraping: google-search-results (SerpAPI), googlesearch-python, multithreading com ThreadPoolExecutor, caches em disco.
- Configuração centralizada: classe `Config` com fontes confiáveis, limites, modelos e parâmetros de scoring.

### Frontend (JavaScript)
- React 18 com Vite como bundler/dev server e React Icons para ícones.
- Hooks personalizados, componentes reutilizáveis e estilização CSS modular para UX informativa.

## Estrutura de pastas
```
news-verifier/
|-- app.py               API Flask principal
|-- config.py            Parâmetros globais do sistema
|-- modules/             Núcleo de IA, busca, scraping e scoring
|-- frontend/            Aplicação React (Vite)
|-- requirements.txt     Dependências Python
`-- tests/               Scripts utilitários e diagnósticos
```

## Configuração do ambiente
## Requisitos mínimos
Os requisitos abaixo garantem uma experiência fluida para desenvolvimento local e execução das análises de veracidade:

### Backend
- **Sistema operacional**: Linux, macOS ou Windows 10/11 (com WSL recomendado).
- **Python**: versão 3.10 ou superior.
- **Processador**: CPU moderna com suporte a instruções AVX (necessário para alguns modelos de embeddings).
- **Memória RAM**: mínimo 8 GB (recomendado 12 GB para processamento de múltiplas fontes).
- **Armazenamento**: pelo menos 5 GB livres para dependências Python, caches e modelos spaCy/sentence-transformers.

### Frontend
- **Node.js**: versão 18 LTS ou superior.
- **Memória RAM**: mínimo 4 GB para rodar o servidor de desenvolvimento do Vite sem travamentos.
- **Navegador**: versão recente do Chrome, Firefox ou Edge com suporte a ES2020.

### Dependências externas
- **Conexão com a internet** para baixar modelos de NLP e consultar fontes reais.
- **Chave SerpAPI** (opcional) para habilitar buscas no Google; sem a chave, utilize modo mock ou fontes locais.

### Backend (Flask)
1. Crie e ative um ambiente virtual Python 3.10+.
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\Activate.ps1
   # Linux/macOS
   source venv/bin/activate
   ```
2. Atualize ferramentas básicas:
   ```bash
   pip install -U pip setuptools wheel
   ```
3. **Instale o PyTorch** conforme o alvo (CPU/GPU) — veja o guia rápido abaixo.
4. Instale as dependências do projeto (exceto `torch`,no momento comentado em requirements.txt, que recomendamos instalar separado conforme CPU/GPU):
   ```bash
   pip install -r requirements.txt
   ```
5. Garanta que o modelo spaCy `pt_core_news_lg` esteja disponível. Caso a instalação via `requirements.txt` falhe, execute:
   ```bash
   python -m spacy download pt_core_news_lg
   ```
6. Configure variáveis opcionais em `.env` (porta, host, chaves SerpAPI, etc.) seguindo os atributos da classe `Config`.

### Guia rápido: venv do zero (CPU/GPU)
> Use **apenas um** dos blocos de PyTorch abaixo.

**0) Criar e ativar venv**
```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux/macOS
source venv/bin/activate
pip install -U pip setuptools wheel
```

**1) PyTorch — CPU (Windows/Linux/macOS CPU)**
```bash
pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu
```

**1) PyTorch — GPU (Windows/Linux com CUDA)**
- CUDA **12.1**:
  ```bash
  pip install torch==2.3.1+cu121 --index-url https://download.pytorch.org/whl/cu121
  ```
- CUDA **11.8**:
  ```bash
  pip install torch==2.3.1+cu118 --index-url https://download.pytorch.org/whl/cu118
  ```

**2) Demais dependências compatíveis**
```bash
pip install   Flask==3.0.0 flask-cors==4.0.0 requests==2.31.0 python-dotenv==1.0.0   newspaper3k==0.2.8 lxml==4.9.3 beautifulsoup4==4.12.2 validators==0.22.0   spacy==3.7.2 nltk==3.8.1   google-search-results==2.4.2 googlesearch-python==1.2.3   sentence-transformers==3.0.1 transformers==4.41.2   huggingface_hub==0.23.5 tokenizers==0.19.1 accelerate==0.30.1 sentencepiece==0.2.0   scikit-learn==1.3.2 numpy==1.26.2 trafilatura==1.6.2 readability-lxml==0.8.1
```

**3) Baixar modelo spaCy (se necessário)**
```bash
python -m spacy download pt_core_news_lg
# alternativa offline:
# pip install https://github.com/explosion/spacy-models/releases/download/pt_core_news_lg-3.7.0/pt_core_news_lg-3.7.0.tar.gz
```

**4) Verificação do ambiente**
```bash
python - << 'PY'
import torch
print("torch:", torch.__version__)
print("cuda disponível?", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
PY

python - << 'PY'
import sentence_transformers, transformers, huggingface_hub, tokenizers
print("st", sentence_transformers.__version__,
      "tr", transformers.__version__,
      "hub", huggingface_hub.__version__,
      "tok", tokenizers.__version__)
PY
```

> **Dica:** mantenha o `torch` **fora** do `requirements.txt` e instale-o separadamente (CPU ou CUDA). Assim, o mesmo `requirements.txt` serve para máquinas diferentes.

### Frontend (React + Vite)
1. Instale Node.js 18+.
2. Na pasta `frontend`, instale as dependências:
   ```bash
   npm install
   ```
   Os scripts `dev`, `build` e `preview` são fornecidos pelo Vite.

## Como executar
### Subir a API
1. Ative seu ambiente virtual.
2. (Opcional) Ajuste `FLASK_ENV`, `PORT` ou `HOST` conforme necessário.
3. Execute:
   ```bash
   python app.py
   ```

   
### Subir a API
1. Ative seu ambiente virtual.
2. (Opcional) Ajuste `FLASK_ENV`, `PORT` ou `HOST` conforme necessário no `.env`.
3. **(Opcional, recomendado) Habilitar buscas reais com SerpAPI**
   > Por padrão o backend pode rodar em modo `mock` para testes. Para buscar notícias reais no Google, use SerpAPI.
   - **Criar conta**
     1. Acesse o site da **SerpAPI** e crie sua conta (e-mail/senha ou OAuth).
     2. Confirme o e-mail e faça login no **Dashboard**.
   - **Obter a API Key**
     1. No Dashboard, copie sua **API Key** (chave privada).
   - **Configurar o `.env` do projeto (raiz)**
     Crie (ou edite) um arquivo `.env` na pasta do projeto.
	 
     # Flask
     ```
     FLASK_ENV=development
     HOST=0.0.0.0
     PORT=5000
     ```

     # Busca (SerpAPI)
     SEARCH_MODE=serpapi
     SERPAPI_KEY=coloque_sua_chave_aqui
	 
	 **Importante:** não faça commit do `.env`. Adicione `*.env` ao `.gitignore`.
   - **Verificar se a API leu a chave**
     Ao iniciar, as chamadas de verificação devem mostrar `modo_busca: serpapi` no JSON de retorno (`metadata`).  
     Você também pode checar rapidamente:
     ```bash
     python - << 'PY'
     import os; print("SERPAPI_KEY set?", bool(os.getenv("SERPAPI_KEY")))
     print("SEARCH_MODE:", os.getenv("SEARCH_MODE"))
     PY
     ```
4. Execute:
   ```bash
   python app.py
   ```
   
 A aplicação inicializa com CORS liberado, logging estruturado e informações de versão/endpoints no console.

### Rodar a interface web
1. Em outro terminal, acesse `frontend/`.
2. Execute o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```
3. Acesse o endereço indicado (por padrão `http://127.0.0.1:5173`). Certifique-se de que a API esteja disponível em `http://127.0.0.1:5000`.

## Uso da API
- **Health check**: `GET /api/health` — retorna status, versão e módulos ativos.
- **Verificar notícia**: `POST /api/verificar`
  - Corpo:
    ```json
    {
      "tipo": "url" | "texto",
      "conteudo": "..."
    }
    ```
  - Erros retornam mensagens padronizadas (`codigo`, `erro`).
  - Sucesso retorna campos como `veracidade`, `nivel_confianca`, `justificativa`, `fontes_consultadas`, estatísticas de NLP e metadados (incluindo alerta de contradição).

## Uso da interface web
A aplicação React organiza a experiência em três blocos principais:
1. **Formulário de verificação** — Permite alternar entre URL e texto, valida tamanho mínimo (alinhado ao backend), mostra contagem de caracteres e botão de limpeza.
2. **Resultado** — Exibe o percentual de veracidade, justificativas, sinais adicionais, fontes consultadas com modal detalhado e nível de confiança colorido.
3. **Feedback em tempo real** — Enquanto a análise roda, um indicador animado explica cada estágio do processamento (extração, busca, análise semântica, detecção de contradições, etc.).

O hook `useNewsVerification` centraliza chamadas à API, estado de carregamento/erro e data da última requisição, reaproveitando a função `verifyNewsRequest` que constrói o payload adequado (`url`/`texto`) e normaliza a resposta antes de repassar para a UI.

## Principais módulos do backend
- **`modules/extractor.py`** — Classe `ContentExtractor` com seis estratégias de fallback para extrair texto estruturado de URLs; a função `extrair_conteudo` é usada diretamente pela API.
- **`modules/nlp_processor.py`** — Classe `NLPProcessor` carrega spaCy e stopwords, normaliza o texto, extrai entidades/palavras-chave e monta queries; `processar_texto` encapsula o uso padrão.
- **`modules/searcher.py`** — `buscar_noticias` e `buscar_noticias_paralelo` executam buscas em portais confiáveis, respeitando cache, prioridades de métodos e threads para paralelismo.
- **`modules/filters.py`** — `ContentFilter` remove URLs problemáticas e conteúdos desconexos; funções helper `filtrar_busca` e `filtrar_scraping` aplicam rapidamente os filtros dentro do fluxo do app.
- **`modules/scraper.py`** — `scrape_noticias_paralelo` lida com extração em larga escala, cuidando de paywalls, cache e agrupamento por fonte; `scrape_noticias` mantém a interface sequencial usada pelo endpoint.
- **`modules/semantic_analyzer.py`** — `analisar_semantica` gera embeddings, calcula similaridade, detecta contradições por padrões linguísticos e agrega estatísticas por fonte.
- **`modules/scorer.py`** — `VeracityScorer.calcular_veracidade` aplica pesos, penalidades e bônus para gerar o score final, justificativa e nível de confiança; penaliza severamente contradições.
- **`config.py`** — Consolida fontes confiáveis, limites de requisição/conteúdo, parâmetros de IA, mensagens padrão e ambientes (desenvolvimento, produção, teste).

## Principais componentes do frontend
- **`App.jsx`** — Monta a página com cabeçalho, formulário, painel de resultados e seção "Como utilizar" que instrui o usuário passo a passo.
- **`VerificationForm.jsx`** — Controla modo URL/texto, validações, mensagens auxiliares, botões e chama `onSubmit` com payload normalizado.
- **`VerificationResult.jsx`** — Renderiza estado inicial/erro, painel de resultados, lista de sinais, grade de fontes e modal detalhado por fonte.
- **`VeracityGauge.jsx`** — Gauge circular responsivo que colore o arco conforme o score de veracidade e indica a confiança.
- **`LoadingIndicator.jsx`** — Spinner temporal que descreve cada fase do backend e sinaliza tempos maiores que o esperado.
- **`useNewsVerification.js` + `services/api.js`** — Hook de orquestração de estado + cliente fetch com timeout e normalização de resposta, garantindo que o frontend continue funcionando mesmo em timeouts (gera mensagens orientativas).

## Resolução de problemas e dicas
- **CPU x GPU**: quem define é o **wheel do PyTorch** instalado. Use `--index-url` conforme CPU ou CUDA (11.8/12.1). No código, use `device="cuda" if torch.cuda.is_available() else "cpu"`.
- **Conflitos de versão (pip)**: mantenha estes pares compatíveis:  
  `sentence-transformers 3.0.1`, `transformers 4.41.2`, `huggingface_hub 0.23.5`, `tokenizers 0.19.1`, `torch 2.3.1`.
- **Timeouts longos**: a chamada é abortada após ~4min; tente textos menores/URLs acessíveis.
- **Modelo spaCy ausente**: `python -m spacy download pt_core_news_lg` (ou instale o `.tar.gz` do release).
- **Chave SerpAPI**: defina `SERPAPI_KEY` no `.env` para buscas reais; sem chave, use modo `mock`(resultado pode nao ser o mesmo!).
- **CORS/Portas**: a API já habilita CORS; ajuste `HOST`/`PORT` em `.env` e `VITE_API_BASE` no frontend.
- **Primeira execução lenta**: o backend baixa **uma vez** o snapshot do modelo de embeddings; depois roda do disco (modo offline).
