import React from 'react';
import ParticleBackground from './ui/ParticleBackground';
import './Hero.css';

const Hero = () => {

  const scrollToSection = (id) => {
    const el = document.querySelector(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section id="home" className="hero-section">
      <ParticleBackground />
      
      {/* Glowing Background Orbs */}
      <div className="hero-orb orb-1"></div>
      <div className="hero-orb orb-2"></div>
      <div className="hero-orb orb-3"></div>

      <div className="hero-container">
        <div className="hero-content">
          <div className="hero-text-block">
            <h2 className="hero-label">Next-Generation Medical AI</h2>
            <h1 className="hero-title">
              <span className="text-gradient">Precision Diagnostics</span><br />
              Powered by Intelligence
            </h1>
            <p className="hero-description">
              Analyze medical images with unprecedented accuracy. Our advanced AI command center assists healthcare professionals in detecting anomalies faster and more reliably.
            </p>
            
            <div className="hero-actions">
              <button className="hero-btn primary-btn" onClick={() => scrollToSection('#upload')}>
                Start Diagnosis &rarr;
              </button>
              <button className="hero-btn secondary-btn" onClick={() => scrollToSection('#about')}>
                Learn More
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
