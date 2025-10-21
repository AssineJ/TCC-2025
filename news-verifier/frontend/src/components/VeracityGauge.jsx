const COLORS = [
  { threshold: 30, stroke: '#f87171', glow: 'rgba(248, 113, 113, 0.35)' },
  { threshold: 60, stroke: '#fbbf24', glow: 'rgba(251, 191, 36, 0.35)' },
  { threshold: 80, stroke: '#34d399', glow: 'rgba(52, 211, 153, 0.35)' },
  { threshold: 100, stroke: '#38bdf8', glow: 'rgba(56, 189, 248, 0.35)' }
];

function getGaugeStyle(score) {
  const color = COLORS.find(({ threshold }) => score <= threshold) ?? COLORS[COLORS.length - 1];
  return color;
}

export default function VeracityGauge({ score = 0 }) {
  const normalized = Math.max(0, Math.min(100, score));
  const radius = 90;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (normalized / 100) * circumference;
  const { stroke, glow } = getGaugeStyle(normalized);

  return (
    <div className="gauge">
      <svg viewBox="0 0 220 220">
        <defs>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor={glow} floodOpacity="1" />
          </filter>
        </defs>
        <circle className="gauge__track" cx="110" cy="110" r={radius} />
        <circle
          className="gauge__progress"
          cx="110"
          cy="110"
          r={radius}
          stroke={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          filter="url(#glow)"
        />
      </svg>
      <div className="gauge__label">
        <span>{Math.round(normalized)}%</span>
        <small>confiança</small>
      </div>
    </div>
  );
}