import React from 'react';
import ScrollReveal from './ui/ScrollReveal';
import Tilt3D from './ui/Tilt3D';
import './About.css';

const About = () => {
  const features = [
    {
      title: 'Image Preprocessing',
      description: 'Resizing to 384×384 and ImageNet normalization (mean 0.485/0.456/0.406, std 0.229/0.224/0.225) to match EfficientNet-B2 training; CLAHE available for visualization only.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="feature-icon">
          <rect x="2" y="2" width="20" height="20" rx="2" ry="2"></rect>
          <circle cx="8.5" cy="8.5" r="1.5"></circle>
          <polyline points="21 15 16 10 5 21"></polyline>
        </svg>
      )
    },
    {
      title: 'EfficientNet-B2',
      description: 'EfficientNet-B2 (7.7M params, 384px) fine-tuned for 3-class Normal/Bacterial/Viral pneumonia — high accuracy on in-distribution raw X-rays (93–96% top-1 on fresh external 30) and 86–99% on segmented hold-outs.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="feature-icon">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
          <path d="M2 12h20"></path>
        </svg>
      )
    },
    {
      title: 'SHAP Explainability',
      description: 'Provides SHAP attribution maps and feature importance scores to explain AI decisions, ensuring transparency and building trust with clinical practitioners.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="feature-icon">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
          <circle cx="12" cy="12" r="3"></circle>
        </svg>
      )
    },
    {
      title: 'RAG + LLM',
      description: 'Retrieval-Augmented Generation coupled with Large Language Models produces comprehensive, evidence-based radiological reports based on findings.',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="feature-icon">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10 9 9 8 9"></polyline>
        </svg>
      )
    }
  ];

  return (
    <section id="about" className="about-section">
      <div className="about-container">
        <ScrollReveal>
          <div className="about-header">
            <span className="about-label">About The Project</span>
            <h2 className="about-heading">Understanding Our Approach</h2>
            <p className="about-subtitle">
              Our explainable AI pipeline combines advanced computer vision models with natural language generation to provide a complete diagnostic aid for medical professionals.
            </p>
          </div>
        </ScrollReveal>

        <div className="features-grid">
          {features.map((feature, index) => (
            <ScrollReveal key={index} delay={index * 100}>
              <Tilt3D maxTilt={8} scale={1.03}>
                <div className="feature-card">
                  <div className="feature-icon-wrapper">
                    {feature.icon}
                  </div>
                  <h3 className="feature-title">{feature.title}</h3>
                  <p className="feature-desc">{feature.description}</p>
                </div>
              </Tilt3D>
            </ScrollReveal>
          ))}
        </div>

        <ScrollReveal delay={400}>
          <div className="about-highlight">
            <p>
              Built with cutting-edge AI techniques to assist radiologists with transparent, evidence-based diagnostic support.
            </p>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
};

export default About;
