import { useRef, useState, useCallback } from 'react';
import './ImageSlider.css';

const ImageSlider = ({ beforeSrc, afterSrc, beforeLabel = 'Original', afterLabel = 'Analysis', className = '' }) => {
  const [pos, setPos] = useState(50);
  const containerRef = useRef(null);
  const dragging = useRef(false);

  const updateFromClientX = useCallback((clientX) => {
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect || rect.width === 0) return;
    const pct = ((clientX - rect.left) / rect.width) * 100;
    setPos(Math.max(0, Math.min(100, pct)));
  }, []);

  const onPointerDown = useCallback((e) => {
    dragging.current = true;
    e.currentTarget.setPointerCapture?.(e.pointerId);
    updateFromClientX(e.clientX);
  }, [updateFromClientX]);

  const onPointerMove = useCallback((e) => {
    if (!dragging.current) return;
    updateFromClientX(e.clientX);
  }, [updateFromClientX]);

  const onPointerUp = useCallback(() => {
    dragging.current = false;
  }, []);

  return (
    <div
      ref={containerRef}
      className={`image-slider ${className}`.trim()}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
    >
      <img src={beforeSrc} alt={beforeLabel} className="slider-before" />
      <div className="slider-after" style={{ clipPath: `inset(0 0 0 ${pos}%)` }}>
        <img src={afterSrc} alt={afterLabel} className="slider-before" />
      </div>
      <div className="slider-handle" style={{ left: `${pos}%` }}>
        <span className="slider-handle-grip" />
      </div>
      <span className="slider-label slider-label-left">{beforeLabel}</span>
      <span className="slider-label slider-label-right">{afterLabel}</span>
    </div>
  );
};

export default ImageSlider;
