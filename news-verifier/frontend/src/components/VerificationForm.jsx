import { useMemo, useState, useEffect } from 'react';
import { FiLink, FiFileText, FiRefreshCw, FiSend } from 'react-icons/fi';

const sanitizeText = (value) =>
  value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[^\w\s-]/g, '')
    .replace(/[\u0300-\u036f]/g, '');

const enforceMaxLength = (value, maxLength) =>
  typeof maxLength === 'number' ? value.slice(0, maxLength) : value;

const PROFANITY_PATTERNS = [
  /\bporra\b/,
  /\bcaralho\b/,
  /\bmerda\b/,
  /\bbosta\b/,
  /\bcacete\b/,
  /\bputa\b/,
  /\bputo\b/,
  /\bputaria\b/,
  /\bputinha\b/,
  /\bdesgraca\b/,
  /\bdesgracado\b/,
  /\bdesgracada\b/,
  /\barrombado\b/,
  /\barrombada\b/,
  /\bviado\b/,
  /\bvadia\b/,
  /\bcuz(o|ao)\b/,
  /\bcuzinho\b/,
  /\bfoder\b/,
  /\bfodido\b/,
  /\bfodida\b/,
  /foda[-\s]?se/,
  /\bfoda\b/,
  /\bvsf\b/,
  /\bcorno\b/,
  /\bcorna\b/,
  /\bfilh[oa]\s+da\s+puta\b/,
  /\bseu?\s+(merda|lixo)/
];

const INPUT_TYPES = {
  url: {
    label: 'Validar por URL',
    placeholder: 'https://exemplo.com/noticia-importante',
    minLength: 10,
    maxLength: 500,  
    helpText: 'Informe o endereço completo da notícia que será analisada.',
    errorText: 'Informe uma URL válida com pelo menos 10 caracteres.'
  },
  text: {
    label: 'Validar por texto',
    placeholder: 'Cole o conteúdo da notícia que deseja analisar...',
    minLength: 50,
    maxLength: 500,  
    helpText: 'Insira o texto completo da notícia. Mínimo 50, máximo 500 caracteres e sem palavrões.',
    errorText: 'Insira entre 50 e 500 caracteres sem palavras de baixo calão.'
  }
};

const INITIAL_FORM = {
  mode: 'url',
  value: ''
};

export default function VerificationForm({ status, onSubmit, onReset, lastRequest }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [touched, setTouched] = useState(false);
  const [textQualityWarning, setTextQualityWarning] = useState('');
  const [profanityWarning, setProfanityWarning] = useState('');

  const isLoading = status === 'loading';

  const rawCharCount = form.value.length;
  const charCount = useMemo(() => form.value.trim().length, [form.value]);
  const currentConfig = INPUT_TYPES[form.mode];
  const containsProfanity = useMemo(() => {
    if (form.mode !== 'text' || !form.value) {
      return false;
    }

    const normalizedText = sanitizeText(form.value);
    return PROFANITY_PATTERNS.some((pattern) => pattern.test(normalizedText));
  }, [form.mode, form.value]);

  const isWithinMax =
    typeof currentConfig.maxLength === 'number' ? rawCharCount <= currentConfig.maxLength : true;
  const isFormValid =
    charCount >= currentConfig.minLength && isWithinMax && !containsProfanity;

  
  useEffect(() => {
    if (form.mode === 'text' && charCount >= 50) {
      const text = form.value.trim();
      
      
      const hasExcessiveRepetition = /(.)\1{5,}/.test(text);
      
      
      const words = text.toLowerCase().match(/\b\w+\b/g) || [];
      const uniqueWords = new Set(words).size;
      const repetitionRatio = words.length > 0 ? uniqueWords / words.length : 1;
      
      if (hasExcessiveRepetition) {
        setTextQualityWarning('Texto com caracteres repetidos excessivamente');
      } else if (repetitionRatio < 0.3 && words.length > 5) {
        setTextQualityWarning('Texto parece ter muitas palavras repetidas');
      } else {
        setTextQualityWarning('');
      }
    } else {
      setTextQualityWarning('');
    }
  }, [form.value, form.mode, charCount]);

  useEffect(() => {
    if (form.mode === 'text' && containsProfanity) {
      setProfanityWarning('Texto contém palavras de baixo calão. Remova-as para continuar.');
    } else {
      setProfanityWarning('');
    }
  }, [containsProfanity, form.mode]);

  const handleModeChange = (mode) => {
    setForm({ mode, value: '' });
    setTouched(false);
    setTextQualityWarning('');
    setProfanityWarning('');
    if (onReset) onReset();
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setTouched(true);

    if (!isFormValid || isLoading) {
      return;
    }

    console.log('Enviando verificação:', {
      mode: form.mode,
      type: form.mode,
      payload: form.value.trim(),
      length: form.value.trim().length
    });

    onSubmit({
      type: form.mode,
      payload: form.value.trim()
    });
  };

  const handleReset = () => {
    setForm(INITIAL_FORM);
    setTouched(false);
    setTextQualityWarning('');
    setProfanityWarning('');
    if (onReset) onReset();
  };

  const isAtMaxLength =
    form.mode === 'text' && typeof currentConfig.maxLength === 'number'
      ? rawCharCount >= currentConfig.maxLength
      : false;

  return (
    <form className="card" onSubmit={handleSubmit}>
      <header className="card__header">
        <h2>Valide uma notícia agora</h2>
        <p>
          Escolha validar por URL ou texto completo. O NewsTrust retornará um percentual de veracidade com justificativas baseadas em fontes confiáveis.
        </p>
        {isLoading && (
          <p className="form__loading-hint">
             <strong>Tempo estimado:</strong> 1-3 minutos. Aguarde enquanto analisamos múltiplas fontes confiáveis.
          </p>
        )}
      </header>

      <div className="toggle">
        {Object.entries(INPUT_TYPES).map(([mode, config]) => (
          <button
            key={mode}
            type="button"
            className={`toggle__option ${form.mode === mode ? 'toggle__option--active' : ''}`}
            onClick={() => handleModeChange(mode)}
            disabled={isLoading}
          >
            {mode === 'url' ? <FiLink /> : <FiFileText />} {config.label}
          </button>
        ))}
      </div>

      <label className="field">
        <span>
          {currentConfig.label}
          <small>{currentConfig.helpText}</small>
        </span>
        {form.mode === 'url' ? (
          <input
            type="url"
            placeholder={currentConfig.placeholder}
            value={form.value}
            onChange={(event) =>
              setForm((prev) => ({
                ...prev,
                value: enforceMaxLength(event.target.value, currentConfig.maxLength)
              }))
            }
            disabled={isLoading}
            maxLength={currentConfig.maxLength}
            required
          />
        ) : (
          <textarea
            placeholder={currentConfig.placeholder}
            value={form.value}
            onChange={(event) =>
              setForm((prev) => ({
                ...prev,
                value: enforceMaxLength(event.target.value, currentConfig.maxLength)
              }))
            }
            disabled={isLoading}
            minLength={currentConfig.minLength}
            maxLength={currentConfig.maxLength}
            rows={8}
            required
          />
        )}
      </label>

      <div className="form__footer">
        <div className="form__status">
          <strong>{charCount}</strong> caracteres
          <span className="form__hint">
            (mínimo: {currentConfig.minLength}
            {typeof currentConfig.maxLength === 'number' ? `, máximo: ${currentConfig.maxLength}` : ''})
          </span>
          {touched && !isFormValid && (
            <span className="form__warning">
              {currentConfig.errorText}
            </span>
          )}
          {textQualityWarning && (
            <span className="form__warning">
              {textQualityWarning}
            </span>
          )}
          {profanityWarning && (
            <span className="form__warning">
              {profanityWarning}
            </span>
          )}
          {isAtMaxLength && (
            <span className="form__warning">
               Limite máximo de 500 caracteres atingido.
            </span>
          )}
          {lastRequest && (
            <span className="form__last">
              Última análise: <time dateTime={lastRequest.toISOString()}>{lastRequest.toLocaleString('pt-BR')}</time>
            </span>
          )}
        </div>

        <div className="form__actions">
          <button type="button" className="ghost" onClick={handleReset} disabled={isLoading}>
            <FiRefreshCw /> Limpar
          </button>
          <button type="submit" className="primary" disabled={!isFormValid || isLoading}>
            <FiSend /> {isLoading ? 'Verificando...' : 'Verificar notícia'}
          </button>
        </div>
      </div>
    </form>
  );
}
