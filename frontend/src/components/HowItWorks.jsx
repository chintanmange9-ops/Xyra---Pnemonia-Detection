import React, { useState, useEffect } from 'react';
import './HowItWorks.css';
// import { pipelineSteps } from '../data/pipelineSteps';
import ScrollReveal from './ui/ScrollReveal';

// Fallback data in case pipelineSteps is not available yet
const defaultSteps = [
  { title: 'Image Upload', description: 'Upload a standard chest X-ray image in DICOM, PNG, or JPEG format.', details: ['Secure upload', 'Format validation', 'Preprocessing'] },
  { title: 'Image Preprocessing', description: 'The image is resized, normalized, and enhanced for the AI model.', details: ['Noise reduction', 'Contrast enhancement', 'Auto-cropping'] },
  { title: 'Feature Extraction', description: 'EfficientNet-B2 extracts complex visual features from the X-ray.', details: ['Deep learning backbone', 'High-level feature maps', 'Spatial hierarchies'] },
  { title: 'Classification', description: 'The model classifies the image as Normal, Bacterial, or Viral Pneumonia.', details: ['Softmax probabilities', 'Confidence scores', 'Multi-class detection'] },
  { title: 'Explainability (XAI)', description: 'Grad-CAM and SHAP generate heatmaps showing which areas influenced the decision.', details: ['Visual heatmaps', 'Feature importance', 'Clinical validation'] },
  { title: 'Report Generation', description: 'RAG and an LLM generate a comprehensive, human-readable medical report.', details: ['Contextual insights', 'Actionable recommendations', 'PDF export'] }
];

const HowItWorks = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [isMobile, setIsMobile] = useState(false);

  // You would normally use the imported pipelineSteps here
  const steps = defaultSteps; // pipelineSteps || defaultSteps;

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 992);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <section id="how-it-works" className="how-it-works-section">
      <div className="container">
        <ScrollReveal>
          <div className="section-header">
            <span className="section-label">OUR PIPELINE</span>
            <h2 className="section-title">How It Works</h2>
            <p className="section-subtitle">
              A seamless 6-step process from image upload to explainable AI diagnosis.
            </p>
          </div>
        </ScrollReveal>

        <div className={`timeline-container ${isMobile ? 'mobile' : 'desktop'}`}>
          {!isMobile && (
            <div 
              className="timeline-progress-bar" 
              style={{ width: `${(activeStep / (steps.length - 1)) * 100}%` }}
            ></div>
          )}
          
          {isMobile && (
            <div 
              className="timeline-progress-bar-vertical" 
              style={{ height: `${(activeStep / (steps.length - 1)) * 100}%` }}
            ></div>
          )}

          <div className="timeline-steps">
            {steps.map((step, index) => (
              <ScrollReveal key={index} delay={index * 100} className="timeline-step-wrapper">
                <div 
                  className={`timeline-step ${activeStep === index ? 'active' : ''} ${index <= activeStep ? 'completed' : ''}`}
                  onClick={() => setActiveStep(index)}
                >
                  <div className="step-circle">
                    <span className="step-number">{index + 1}</span>
                  </div>
                  <h4 className="step-title">{step.title}</h4>
                </div>
                
                {isMobile && activeStep === index && (
                  <div className="mobile-step-detail">
                    <h3 className="detail-title">{step.title}</h3>
                    <p className="detail-description">{step.description}</p>
                    <ul className="detail-bullets">
                      {step.details && step.details.map((detail, i) => (
                        <li key={i}>{detail}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </ScrollReveal>
            ))}
          </div>
        </div>

        {!isMobile && (
          <div className="step-details-container">
            {steps.map((step, index) => (
              <div 
                key={index} 
                className={`step-detail-panel ${activeStep === index ? 'active' : ''}`}
              >
                <h3 className="detail-title">{step.title}</h3>
                <p className="detail-description">{step.description}</p>
                <ul className="detail-bullets">
                  {step.details && step.details.map((detail, i) => (
                    <li key={i}>{detail}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default HowItWorks;
