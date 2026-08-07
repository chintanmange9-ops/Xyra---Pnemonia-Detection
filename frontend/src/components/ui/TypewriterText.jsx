import React, { useState, useEffect } from 'react';

const TypewriterText = ({ text = '', speed = 20, onComplete, trigger = false }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!trigger) return;

    if (!text) {
      setDisplayedText('');
      setIsTyping(false);
      return;
    }

    setIsTyping(true);
    let index = 0;

    // Clear initial state when triggered
    setDisplayedText('');

    const intervalId = setInterval(() => {
      const char = text.charAt(index);
      setDisplayedText((prev) => prev + char);
      index++;

      if (index === text.length) {
        clearInterval(intervalId);
        setIsTyping(false);
        if (onComplete) onComplete();
      }
    }, speed);

    return () => clearInterval(intervalId);
  }, [text, speed, trigger, onComplete]);

  // Handle line breaks
  const renderText = () => {
    return displayedText.split('\n').map((line, i, arr) => (
      <React.Fragment key={i}>
        {line}
        {i !== arr.length - 1 && <br />}
      </React.Fragment>
    ));
  };

  return (
    <div style={{ fontFamily: '"DM Sans", sans-serif', color: 'var(--color-primary, #0A1628)', lineHeight: 1.6 }}>
      {renderText()}
      {isTyping && (
        <span 
          style={{ 
            display: 'inline-block', 
            width: '8px', 
            height: '1.2em', 
            backgroundColor: 'currentColor', 
            verticalAlign: 'bottom',
            marginLeft: '2px',
            animation: 'blink 1s step-end infinite'
          }} 
        />
      )}
      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
      `}</style>
    </div>
  );
};

export default TypewriterText;
