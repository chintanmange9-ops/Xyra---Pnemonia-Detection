import React, { useState } from 'react';
import './Dashboard.css';
import ConfidenceGauge from './ui/ConfidenceGauge';
import BarChart from './ui/BarChart';
import TypewriterText from './ui/TypewriterText';
import ScrollReveal from './ui/ScrollReveal';
import Tilt3D from './ui/Tilt3D';

const Dashboard = ({ results, imageUrl, onReset }) => {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const [openSource, setOpenSource] = useState(null);

  if (!results) return null;

  const { probabilities, prediction, isValidated, status, shapAnalysis, report, regions, recommendations } = results;

  const getPredictionColor = (pred) => {
    switch (pred) {
      case 'Normal': return 'var(--color-success, #059669)';
      case 'Bacterial Pneumonia': return 'var(--color-danger, #DC2626)';
      case 'Viral Pneumonia': return 'var(--color-warning, #D97706)';
      default: return 'var(--color-primary, #0A1628)';
    }
  };

  const predictionColor = getPredictionColor(prediction);
  
  const chartData = [
    { label: 'Normal', value: (probabilities?.normal || 0) * 100, color: '#059669' },
    { label: 'Bacterial Pneumonia', value: (probabilities?.bacterial || 0) * 100, color: '#DC2626' },
    { label: 'Viral Pneumonia', value: (probabilities?.viral || 0) * 100, color: '#D97706' }
  ];

  return (
    <section id="dashboard" className="dashboard-section fade-in">
      <ScrollReveal>
        <div className="section-header">
          <span className="section-label">RESULTS</span>
          <h2 className="section-heading">Diagnostic Report</h2>
          <p className="section-subtitle">
            Analysis completed on {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
          </p>
        </div>
      </ScrollReveal>

      <div className="dashboard-grid">
        <div className="dashboard-scan-line"></div>
        {/* Top Row: Original X-Ray (Grad-CAM removed) */}
        <div className="top-row">
          <ScrollReveal delay={100}>
            <Tilt3D maxTilt={4} scale={1.01}>
              <div className="card image-card">
                <h3 className="card-title">Chest X-Ray</h3>
                <div className="image-wrapper">
                  <img src={imageUrl} alt="Chest X-Ray" className="display-image" style={{width:'100%', borderRadius:'8px'}} />
                </div>
              </div>
            </Tilt3D>
          </ScrollReveal>
        </div>

        {/* Middle Row: Diagnosis Summary */}
        <div className="middle-row">
          <ScrollReveal delay={400}>
            <Tilt3D maxTilt={4} scale={1.01}>
              <div className="card prediction-card">
                <span className="subtitle">AI Classification Result</span>
                <div className="prediction-badge" style={{ backgroundColor: `${predictionColor}20`, color: predictionColor }}>
                  <h2 className="prediction-text" style={{ color: predictionColor }}>{prediction}</h2>
                </div>
                
                <div className={`validation-status ${isValidated ? 'valid' : 'warning'}`}>
                  {isValidated ? (
                    <>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                      <span>Validated by RAG System</span>
                    </>
                  ) : (
                    <>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                      <span>{status === 'FALLBACK' ? 'Degraded Result — Clinical Review Required' : 'Requires Clinical Validation'}</span>
                    </>
                  )}
                </div>
              </div>
            </Tilt3D>
          </ScrollReveal>

          <ScrollReveal delay={500}>
            <Tilt3D maxTilt={4} scale={1.01}>
              <div className="card gauge-card">
                <h3 className="card-title">Confidence Score</h3>
                <div className="gauge-container">
                  <ConfidenceGauge 
                    value={Math.max(probabilities?.normal || 0, probabilities?.bacterial || 0, probabilities?.viral || 0)} 
                    color={predictionColor} 
                  />
                </div>
              </div>
            </Tilt3D>
          </ScrollReveal>

          <ScrollReveal delay={600}>
            <Tilt3D maxTilt={4} scale={1.01}>
              <div className="card chart-card">
                <h3 className="card-title">Classification Breakdown</h3>
                <div className="chart-container">
                  <BarChart data={chartData} />
                </div>
              </div>
            </Tilt3D>
          </ScrollReveal>
        </div>

        {/* Bottom Row: Explainability */}
        <div className="bottom-row">
          <ScrollReveal delay={700}>
            <Tilt3D maxTilt={4} scale={1.01}>
              <div className="card shap-card">
                <h3 className="card-title">Feature Importance (SHAP)</h3>
                <p className="card-desc">Contribution of lung regions to the prediction</p>
                {results.shapUrl && (
                  <div className="image-wrapper shap-image-wrapper">
                    <img src={results.shapUrl} alt="SHAP Attribution Map" className="display-image" />
                  </div>
                )}
                <div className="shap-bars">
                  {shapAnalysis?.sort((a, b) => b.importance - a.importance).map((item, idx) => (
                    <div key={idx} className="shap-bar-container">
                      <div className="shap-bar-header">
                        <span className="shap-feature">{item.feature}</span>
                        <span className="shap-value">{item.importance}%</span>
                      </div>
                      <div className="shap-track">
                        <div 
                          className="shap-fill" 
                          style={{ 
                            width: `${item.importance}%`,
                            background: `linear-gradient(90deg, var(--color-accent, #0891B2) 0%, var(--color-primary, #0A1628) 100%)`,
                            animationDelay: `${idx * 0.1 + 0.8}s`
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Tilt3D>
          </ScrollReveal>

          <ScrollReveal delay={800}>
            <Tilt3D maxTilt={4} scale={1.01}>
              <div className="card report-card">
                <div className="report-header">
                  <h3 className="card-title">Clinical Analysis Report</h3>
                  <span className="badge">{status === 'APPROVED' ? 'Powered by RAG + OpenRouter' : 'Fallback Report'}</span>
                </div>
                
                <div className="report-content">
                  <TypewriterText text={report?.text || 'Generating report...'} trigger />
                </div>

                {recommendations?.length > 0 && (
                  <div className="recommendations">
                    <h4 className="recommendations-title">Recommendations</h4>
                    <ul className="recommendations-list">
                      {recommendations.map((rec, idx) => (
                        <li key={idx} className="recommendation-item">
                          <span className="recommendation-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                          </span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="evidence-section">
                  <button 
                    className="evidence-toggle" 
                    onClick={() => setSourcesOpen(!sourcesOpen)}
                  >
                    <span>Evidence Sources</span>
                    <svg className={`chevron ${sourcesOpen ? 'open' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                  </button>
                  
                  <div className={`evidence-content ${sourcesOpen ? 'open' : ''}`}>
                    {report?.sources?.map((source, idx) => (
                      <div key={idx} className="source-card">
                        <div
                          className="source-header"
                          role="button"
                          onClick={() => setOpenSource(openSource === idx ? null : idx)}
                        >
                          <h4 className="source-title">{source.title}</h4>
                          {source.text && source.text.length > 110 && (
                            <span className="source-toggle">
                              {openSource === idx ? 'Show less' : 'Show more'}
                            </span>
                          )}
                        </div>
                        <p className="source-meta">{source.journal}, {source.year}</p>
                        {openSource === idx && source.text && (
                          <p className="source-text">{source.text}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Tilt3D>
          </ScrollReveal>
        </div>

        {/* Detected Regions */}
        <ScrollReveal delay={900}>
          <Tilt3D maxTilt={4} scale={1.01}>
            <div className="card regions-card">
              <h3 className="card-title">Detected Regions</h3>
              <div className="regions-grid">
                {regions?.map((region, idx) => (
                  <div key={idx} className="region-item">
                    <div className="region-header">
                      <h4 className="region-name">{region.name}</h4>
                      <span className={`severity-badge ${region.severity.toLowerCase()}`}>
                        {region.severity}
                      </span>
                    </div>
                    <p className="region-desc">{region.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </Tilt3D>
        </ScrollReveal>

        {/* Actions */}
        <ScrollReveal delay={1000} className="actions-row">
          <button className="btn-primary" onClick={onReset}>
            Analyze Another X-Ray
          </button>
          <button className="btn-outline" onClick={async () => {
            try {
              const resp = await fetch('http://localhost:5000/api/download-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ result: results }),
              });
              if (!resp.ok) throw new Error('Failed to generate report');
              const blob = await resp.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `LungAI_Report_${results.case_id || 'report'}.pdf`;
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(url);
            } catch (err) {
              alert('Download failed: ' + err.message);
            }
          }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            Download Report
          </button>
          <button className="btn-outline" onClick={() => {
            navigator.clipboard.writeText(window.location.href);
            alert('Link copied to clipboard!');
          }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
            Share Results
          </button>
        </ScrollReveal>
      </div>
    </section>
  );
};

export default Dashboard;
