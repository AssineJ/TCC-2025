const DEFAULT_HEADERS = {
  'Content-Type': 'application/json'
};

// Em produção (Render) usa VITE_API_URL; em dev cai para localhost
const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

function buildPayload(type, payload) {
  const tipoBackend = type === 'text' ? 'texto' : 'url';

  return {
    tipo: tipoBackend,
    conteudo: payload
  };
}

export async function verifyNewsRequest(type, payload) {
  const controller = new AbortController();
  // 240s (4min) – pode ajustar se quiser
  const timeoutId = setTimeout(() => controller.abort(), 240000);

  try {
    const requestBody = buildPayload(type, payload);

    console.log('[API] Enviando para backend:', {
      baseURL,
      endpoint: '/api/verificar',
      tipo: requestBody.tipo
    });

    const response = await fetch(`${baseURL}/api/verificar`, {
      method: 'POST',
      headers: {
        ...DEFAULT_HEADERS
        // <<< removido o 'ngrok-skip-browser-warning'
      },
      body: JSON.stringify(requestBody),
      signal: controller.signal,
      mode: 'cors'
    });

    if (!response.ok) {
      let errorData = {};
      try {
        errorData = await response.json();
      } catch (_) {}

      console.error('[API] Erro HTTP da API:', response.status, errorData);
      throw new Error(
        errorData.erro ||
          errorData.message ||
          `Falha na API: ${response.status}`
      );
    }

    const data = await response.json();

    const vRaw = data?.veracidade ?? 0;
    const veracidade =
      typeof vRaw === 'number'
        ? vRaw
        : parseFloat(
            String(vRaw)
              .replace(',', '.')
              .replace(/[^\d.-]/g, '')
          ) || 0;

    const signals = [];
    if (data?.justificativa) signals.push(data.justificativa);

    if (data?.analise_semantica) {
      const sem = data.analise_semantica;
      if (sem.confirmam_forte > 0)
        signals.push(
          `${sem.confirmam_forte} fonte(s) confirmam fortemente a informação`
        );
      if (sem.confirmam_parcial > 0)
        signals.push(
          `${sem.confirmam_parcial} fonte(s) confirmam parcialmente`
        );
      if (sem.apenas_mencionam > 0)
        signals.push(
          `${sem.apenas_mencionam} fonte(s) apenas mencionam o tema`
        );
    }

    const fontes = (data?.fontes_consultadas || []).map(fonte => ({
      name: fonte.nome || 'Fonte desconhecida',
      url: fonte.url || '',
      title: fonte.titulo || '',
      similarity: fonte.similaridade || 0,
      status: fonte.status || ''
    }));

    return {
      veracity_score: veracidade,
      summary: data?.justificativa || 'Análise concluída.',
      confidence_level: data?.nivel_confianca || 'Desconhecido',
      related_sources: fontes,
      signals:
        signals.length > 0 ? signals : ['Nenhum sinal adicional identificado'],
      main_source: data?.titulo_analisado || '',
      metadata: data?.metadata || {},
      nlp: data?.analise_nlp || {},
      semantic: data?.analise_semantica || {}
    };
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('[API] Requisição cancelada por timeout');
      throw new Error(
        'A análise demorou demais. Tente novamente com um texto/URL menor.'
      );
    }

    console.error('[API] Erro na verifyNewsRequest:', error);
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}
