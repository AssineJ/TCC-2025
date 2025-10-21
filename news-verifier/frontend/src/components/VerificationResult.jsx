import { useState } from 'react';
import VeracityGauge from './VeracityGauge.jsx';
import LoadingIndicator from './LoadingIndicator.jsx';

const STATUS_COPY = {
  idle: {
    title: 'O resultado aparecerá aqui após a verificação.',
    description: ''
  },
  error: {
    title: 'Não foi possível concluir a análise',
    description: 'A análise pode ter excedido o tempo limite ou houve um erro. Tente novamente.'
  }
};


export const PORTAL_LOGOS = {
  'G1': { src: '/assets/g1-logo.png', alt: 'G1' },
  'Folha de S.Paulo': { src: '/assets/logo-folha.png', alt: 'Folha de S.Paulo' },
  'CNN Brasil': { src: '/assets/cnn-logo.svg', alt: 'CNN Brasil' },
  'IstoÉ': { src: '/assets/istoe-logo.jpeg', alt: 'IstoÉ' },
  'Estadão': { src: '/assets/estadao-logo.png', alt: 'Estadão' }
};

function renderLogo(sourceName) {
  const logo = PORTAL_LOGOS[sourceName];

  if (!logo) {
    return (
      <span aria-label="Fonte não cadastrada">Fonte</span>
    );
  }

  return (
    <img
      className="portal-logo-image"
      src={logo.src}
      alt={logo.alt || sourceName}
      loading="lazy"
    />
  );
}

function SourceModal({ source, onClose }) {
  if (!source) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-logo">
            {renderLogo(source.name)}
          </div>
          <div>
            <h3>{source.name}</h3>
            <p className="modal-similarity">
              Similaridade {Math.round(source.similarity * 100)}%
            </p>
          </div>
        </div>

        <div className="modal-body">
          <div className="modal-field">
            <label>Título</label>
            <p>{source.title || 'Sem título disponível'}</p>
          </div>

          <div className="modal-field">
            <label>URL</label>
            <a 
              href={source.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="modal-url"
            >
              {source.url}
            </a>
          </div>
        </div>

        <div className="modal-footer">
          <button className="modal-button" onClick={onClose}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}

export default function VerificationResult({ status, result }) {
  const [selectedSource, setSelectedSource] = useState(null);

  if (status === 'loading') {
    return (
      <div className="card card--glass">
        <LoadingIndicator />
      </div>
    );
  }

  
  if (!result) {
    const { title, description } = STATUS_COPY[status] ?? STATUS_COPY.idle;
    return (
      <div className="card card--glass empty">
        <div className={`result__empty ${status === 'error' ? 'result__empty--error' : ''}`}>
          {status === 'error' && <div className="result__empty-icon">!</div>}
          <h3 className="result__empty-title">{title}</h3>
          {description && <p className="result__empty-description">{description}</p>}
        </div>
      </div>
    );
  }

  
  const {
    veracity_score,
    summary,
    signals,
    related_sources,
    confidence_level
  } = result;

  
  if (veracity_score === 0 || (veracity_score < 15 && summary && summary.includes('insuficientes'))) {
    return (
      <div className="card card--result">
        <div className="result__content">
          <div className="result__label">RESULTADO DA ANÁLISE</div>

          <div className="result__alert">
            <div className="result__alert-icon">!</div>
            <div>
              <h3 className="result__alert-title">
                Dados insuficientes para validação
              </h3>
              <p className="result__alert-text">
                {summary}
              </p>
            </div>
          </div>

          {Array.isArray(signals) && signals.length > 0 && (
            <ul className="result__signals result__signals--spaced">
              {signals.map((signal, index) => (
                <li key={index}>{signal}</li>
              ))}
            </ul>
          )}

          <div className="confidence-badge confidence-badge--baixo">
            O texto fornecido não atende aos requisitos mínimos para análise
          </div>
        </div>
      </div>
    );
  }

  
  const getConfidenceLevel = (score) => {
    if (score >= 70) return 'alto';
    if (score >= 40) return 'medio';
    return 'baixo';
  };

  const nivel = getConfidenceLevel(veracity_score);

  return (
    <>
      <div className="card card--result">
        <div className="result__content">
          <div className="result__label">PERCENTUAL DE VERACIDADE</div>
          
          <div className="result__score-section">
            <h2 className="result__score">{Math.round(veracity_score)}%</h2>
            <VeracityGauge score={veracity_score} nivel={nivel} />
          </div>

          <p className="result__summary">
            {summary || 'Análise concluída.'}
          </p>

          {Array.isArray(signals) && signals.length > 0 && (
            <ul className="result__signals">
              {signals.map((signal, index) => (
                <li key={index}>{signal}</li>
              ))}
            </ul>
          )}

          {Array.isArray(related_sources) && related_sources.length > 0 && (
            <div className="result__sources">
              <h3>Fontes consultadas</h3>
              <div className="sources-grid">
                {related_sources.slice(0, 6).map((source, index) => (
                  <button
                    key={index}
                    className="source-card"
                    onClick={() => setSelectedSource(source)}
                  >
                    <div className="source-logo">
                      {renderLogo(source.name)}
                    </div>
                    <div className="source-name">{source.name}</div>
                    <div className="source-similarity">
                      {Math.round(source.similarity * 100)}%
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className={`confidence-badge confidence-badge--${nivel}`}>
            Nível de confiança: <strong>{confidence_level || nivel.toUpperCase()}</strong>
          </div>
        </div>
      </div>
      {selectedSource && (
        <SourceModal 
          source={selectedSource} 
          onClose={() => setSelectedSource(null)} 
        />
      )}
    </>
  );
}
