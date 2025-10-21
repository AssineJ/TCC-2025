import { useEffect, useState } from 'react';

const LOADING_STAGES = [
  { time: 0, message: 'Extraindo conteúdo e processando com IA...' },
  { time: 30, message: 'Buscando em múltiplas fontes confiáveis...' },
  { time: 60, message: 'Analisando similaridade semântica...' },
  { time: 90, message: 'Detectando contradições e padrões...' },
  { time: 120, message: 'Calculando veracidade final...' },
  { time: 150, message: 'Finalizando análise detalhada...'},
  { time: 180, message: 'Aguarde, processamento complexo em andamento...' }
];

export default function LoadingIndicator() {
  const [currentStage, setCurrentStage] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    
    const timer = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    
    const stage = LOADING_STAGES.findIndex((s, i) => {
      const nextStage = LOADING_STAGES[i + 1];
      return elapsedTime >= s.time && (!nextStage || elapsedTime < nextStage.time);
    });
    
    if (stage !== -1 && stage !== currentStage) {
      setCurrentStage(stage);
    }
  }, [elapsedTime, currentStage]);

  const currentMessage = LOADING_STAGES[currentStage];
  const progress = Math.min((elapsedTime / 180) * 100, 95); 

  return (
    <div className="loading">
      <div className="loading__spinner">
        {Array.from({ length: 12 }).map((_, index) => (
          <span key={index} style={{ '--index': index }} />
        ))}
      </div>
      
      <div className="loading__text">
        <strong className="loading__title">Verificando autenticidade</strong>
        <p className="loading__message">
          {currentMessage.message}
        </p>

        <div className="loading__progress">
          <div className="loading__progress-bar" style={{ width: `${progress}%` }} />
        </div>

        <p className="loading__elapsed">
          {elapsedTime}s decorridos - Tempo estimado: 1-3 minutos
        </p>

        {elapsedTime > 120 && (
          <p className="loading__warning">
             Análise mais demorada que o normal, aguarde...
          </p>
        )}
      </div>
    </div>
  );
}