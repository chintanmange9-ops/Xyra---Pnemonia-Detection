import React, { useMemo } from 'react';
import './ParticleBackground.css';

const ParticleBackground = () => {
  // Generate random particles once
  const particles = useMemo(() => {
    return Array.from({ length: 25 }).map((_, i) => {
      const size = Math.random() * 5 + 3; // 3px to 8px
      const left = Math.random() * 100; // 0% to 100%
      const duration = Math.random() * 15 + 15; // 15s to 30s
      const delay = Math.random() * 10; // 0s to 10s
      const opacity = Math.random() * 0.2 + 0.1; // 0.1 to 0.3
      const isBlue = Math.random() > 0.5;

      return {
        id: i,
        size,
        left,
        duration,
        delay,
        opacity,
        isBlue
      };
    });
  }, []);

  return (
    <div className="particle-container">
      {particles.map((p) => (
        <div
          key={p.id}
          className={`particle ${p.isBlue ? 'particle-blue' : 'particle-white'}`}
          style={{
            width: p.size,
            height: p.size,
            left: `${p.left}%`,
            opacity: p.opacity,
            animationDuration: `${p.duration}s`,
            animationDelay: `${p.delay}s`
          }}
        />
      ))}
    </div>
  );
};

export default ParticleBackground;
