import React from 'react';
import './Footer.css';

const Footer = () => {
  const quickLinks = [
    { name: 'Home', href: '#home' },
    { name: 'About', href: '#about' },
    { name: 'How It Works', href: '#how-it-works' },
    { name: 'Diagnose', href: '#upload' },
    { name: 'Our Team', href: '#team' },
  ];

  return (
    <footer className="footer-section">
      <div className="footer-gradient-line"></div>

      <div className="container footer-container">
        <div className="footer-grid">
          {/* Column 1: Brand */}
          <div className="footer-col footer-brand-col">
            <a href="#home" className="footer-logo">
              <svg className="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3v18M3 12h18" />
                <path d="M8 8c-2 0-4 1.5-4 4s2 4 4 4" />
                <path d="M16 8c2 0 4 1.5 4 4s-2 4-4 4" />
              </svg>
              <span className="logo-text">Group<span className="logo-accent">2</span></span>
            </a>

            <p className="footer-desc">
              Explainable AI dashboard for chest X-ray disease detection. Powered by EfficientNet-B2, SHAP, and RAG-augmented clinical report generation.
            </p>

            <div className="footer-disclaimer">
              <span className="disclaimer-title">DISCLAIMER</span>
              <p className="disclaimer-text">
                This is an academic research prototype developed for IPD. Not intended for clinical use without professional oversight.
              </p>
            </div>
          </div>

          {/* Column 2: Quick Links */}
          <div className="footer-col footer-links-col">
            <h4 className="footer-col-title">Quick Links</h4>
            <ul className="footer-links-list">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <a href={link.href} className="footer-link">
                    <svg className="link-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Column 3: Project Info */}
          <div className="footer-col footer-info-col">
            <h4 className="footer-col-title">Project Info</h4>
            <div className="project-info-card">
              <h5 className="project-title">Explainable AI for X-Ray Disease Detection using RAG</h5>
              
              <ul className="project-details-list">
                <li>
                  <span className="detail-label">Project</span>
                  <span className="detail-val">Inter-Project Design (IPD 2026)</span>
                </li>
                <li>
                  <span className="detail-label">Group</span>
                  <span className="detail-val">IPD Group 2</span>
                </li>
                <li>
                  <span className="detail-label">Stack</span>
                  <span className="detail-val">EfficientNet-B2 + XAI + FAISS + OpenRouter LLM</span>
                </li>
              </ul>

              <div className="system-status">
                <span className="status-dot"></span>
                <span className="status-text">System Operational</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="footer-bottom">
          <div className="copyright-container">
            <p className="copyright-text">
              &copy; 2026 Xyra &mdash; IPD Group 2. All rights reserved.
            </p>
            <div className="heartbeat-badge">
              <svg className="heartbeat-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
            </div>
          </div>

          <div className="footer-legal-links">
            <a href="#home" className="legal-link">Privacy Policy</a>
            <span className="legal-separator">&bull;</span>
            <a href="#home" className="legal-link">Terms of Service</a>
            <span className="legal-separator">&bull;</span>
            <a href="#team" className="legal-link">Contact Team</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
