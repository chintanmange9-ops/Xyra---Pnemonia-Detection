import React, { useEffect, useState } from 'react';
import './BarChart.css';
import { useInView } from '../../hooks/useInView';

const BarChart = ({ data = [], animated = true, height = 36 }) => {
  const [ref, inView] = useInView({ threshold: 0.1 });
  const [shouldAnimate, setShouldAnimate] = useState(!animated);

  useEffect(() => {
    if (animated && inView) {
      // Small delay to ensure render is ready before animating
      const timer = setTimeout(() => setShouldAnimate(true), 100);
      return () => clearTimeout(timer);
    }
  }, [animated, inView]);

  return (
    <div className="barchart-container" ref={ref}>
      {data.map((item, index) => {
        const valueNum = parseFloat(item.value) || 0;
        
        return (
          <div key={index} className="barchart-row" style={{ minHeight: height }}>
            <div className="barchart-label">{item.label}</div>
            <div className="barchart-bar-wrapper">
              <div 
                className="barchart-bar"
                style={{ 
                  width: shouldAnimate ? `${valueNum}%` : '0%',
                  backgroundColor: item.color || 'var(--color-primary, #0A1628)',
                  transitionDelay: `${index * 150}ms`
                }}
              />
            </div>
            <div className="barchart-value">{valueNum.toFixed(1)}%</div>
          </div>
        );
      })}
    </div>
  );
};

export default BarChart;
