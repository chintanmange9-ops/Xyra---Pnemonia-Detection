import React from 'react';
import { useInView } from '../../hooks/useInView';

const ScrollReveal = ({ children, direction = 'up', delay = 0, className = '' }) => {
  const [ref, inView] = useInView({ threshold: 0.1 });

  const getTransform = () => {
    switch (direction) {
      case 'up': return 'translateY(40px)';
      case 'down': return 'translateY(-40px)';
      case 'left': return 'translateX(40px)';
      case 'right': return 'translateX(-40px)';
      case 'scale': return 'scale(0.9)';
      default: return 'translateY(40px)';
    }
  };

  const style = {
    opacity: inView ? 1 : 0,
    transform: inView ? 'translate(0) scale(1)' : getTransform(),
    transition: `opacity 0.6s ease-out ${delay}ms, transform 0.6s ease-out ${delay}ms`,
    willChange: 'opacity, transform'
  };

  return (
    <div ref={ref} style={style} className={className}>
      {children}
    </div>
  );
};

export default ScrollReveal;
