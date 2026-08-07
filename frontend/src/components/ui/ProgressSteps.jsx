import React from 'react';
import './ProgressSteps.css';

const ProgressSteps = ({ steps = [], currentStep = 0, isComplete = false }) => {
  return (
    <div className="progress-steps-container">
      {steps.map((step, index) => {
        const isActive = index === currentStep && !isComplete;
        const isPast = index < currentStep || isComplete;

        return (
          <div key={index} className={`progress-step-item ${isActive ? 'active' : ''} ${isPast ? 'completed' : ''}`}>
            <div className="progress-step-indicator-container">
              <div className="progress-step-indicator">
                {isPast ? (
                  <svg viewBox="0 0 24 24" className="checkmark">
                    <path fill="none" stroke="currentColor" strokeWidth="3" d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  step.icon && <span className="step-icon">{step.icon}</span>
                )}
              </div>
              {/* Connector line for all except last */}
              {index < steps.length - 1 && (
                <div className={`progress-step-line ${isPast ? 'filled' : ''}`}></div>
              )}
            </div>
            <div className="progress-step-label">{step.label}</div>
          </div>
        );
      })}
    </div>
  );
};

export default ProgressSteps;
