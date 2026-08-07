import React, { useEffect, useState } from 'react';
import './ConfidenceGauge.css';

const ConfidenceGauge = ({ value = 0, size = 180, strokeWidth = 12, label }) => {
  const [progress, setProgress] = useState(0);
  
  useEffect(() => {
    // Animate slightly after mount
    const timer = setTimeout(() => setProgress(value), 100);
    return () => clearTimeout(timer);
  }, [value]);

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - progress * circumference;

  let color = 'var(--color-danger, #DC2626)'; // < 0.5
  if (value > 0.8) {
    color = 'var(--color-success, #059669)';
  } else if (value >= 0.5) {
    color = 'var(--color-warning, #D97706)';
  }

  return (
    <div className="confidence-gauge" style={{ width: size, height: size + (label ? 30 : 0) }}>
      <svg width={size} height={size} className="gauge-svg">
        <circle
          className="gauge-track"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
        />
        <circle
          className="gauge-progress"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          stroke={color}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
        />
      </svg>
      <div className="gauge-text-container">
        <span className="gauge-percentage">{Math.round(progress * 100)}%</span>
      </div>
      {label && <div className="gauge-label">{label}</div>}
    </div>
  );
};

export default ConfidenceGauge;
