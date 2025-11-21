const DEFAULT_HEADERS = {
  'Content-Type': 'application/json'
};

// Lê da env em produção (Render) e cai pra localhost em desenvolvimento
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
  const timeoutId = setTimeout(() => controller.abort(), 240000);

  try {
    const requestBody = buildPayload(type, payload);
    
    // IMPORTANTE: agora chamando /api/verificar
    const response = await fetch(`${baseURL}/api/verificar`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(requestBody),
      signal: controller.signal,
      mode: 'cors'
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.erro || `Falha na API: ${response.status}`);
    }

    const data = await response.json();
    
    const vRaw = data?.veracidade ?? 0;
    const veracidade =
      typeof vRaw === 'number'
        ? vRaw
        : parseFloat(String(vRaw).replace(',', '.').replace(/[^\d.-]/g, '')) || 0;

    const signals = [];
    if (data?.justificativa) signals.push(data.justificativa);
    
    if (data?.analise_semantica) {
      const sem = data.analise_semantica;
      if (sem.confirmam_forte > 0)
        signals.push(`${sem.confirmam_forte} fonte(s) confirmam fortemente a informação`);
      if (sem.confirmam_parcial > 0)
        signals.push(`${sem.confirmam_parcial} fonte(s) confirmam parcialmente`);
      if (sem.apenas_mencionam > 0)
        signals.push(`${sem.apenas_mencionam} fonte(s) apenas mencionam o tema`);
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
      signals: signals.length > 0 ? signals : ['Nenhum sinal adicional identificado'],
      main_source: data?.titulo_analisado || '',
      metadata: data?.metadata || {},
      nlp: data?.analise_nlp || {},
      semantic: data?.analise_semantica || {}
    };
  } catch (error) {
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}
