import React, { useRef, useState } from 'react';

const Tilt3D = ({ children, className = '', maxTilt = 10, scale = 1.02, glare = true, perspective = 1000 }) => {
  const cardRef = useRef(null);
  const [transform, setTransform] = useState('');
  const [glareStyle, setGlareStyle] = useState({});

  const handleMouseMove = (e) => {
    const card = cardRef.current;
    if (!card) return;
    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;  // 0 to 1
    const y = (e.clientY - rect.top) / rect.height;   // 0 to 1
    const rotateX = (0.5 - y) * maxTilt;  // -maxTilt/2 to maxTilt/2
    const rotateY = (x - 0.5) * maxTilt;
    setTransform(`perspective(${perspective}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(${scale}, ${scale}, ${scale})`);
    if (glare) {
      setGlareStyle({
        background: `radial-gradient(circle at ${x * 100}% ${y * 100}%, rgba(255,255,255,0.15) 0%, transparent 60%)`,
        opacity: 1
      });
    }
  };

  const handleMouseLeave = () => {
    setTransform('');
    setGlareStyle({ opacity: 0 });
  };

  return (
    <div
      ref={cardRef}
      className={`tilt-3d-wrapper ${className}`}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        transform,
        transition: transform ? 'transform 0.1s ease' : 'transform 0.5s ease-out',
        transformStyle: 'preserve-3d',
        position: 'relative'
      }}
    >
      {children}
      {glare && (
        <div
          className="tilt-glare-overlay"
          style={{
            position: 'absolute',
            top: 0, left: 0, right: 0, bottom: 0,
            borderRadius: 'inherit',
            pointerEvents: 'none',
            transition: 'opacity 0.3s ease',
            ...glareStyle
          }}
        />
      )}
    </div>
  );
};

export default Tilt3D;
