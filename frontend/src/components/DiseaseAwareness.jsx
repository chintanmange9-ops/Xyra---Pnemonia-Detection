import React, { useState } from 'react';
import './DiseaseAwareness.css';
// import { diseaseInfo } from '../data/diseaseInfo';
import ScrollReveal from './ui/ScrollReveal';

const DiseaseAwareness = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'types', label: 'Types' },
    { id: 'symptoms', label: 'Symptoms & Signs' },
    { id: 'prevention', label: 'Prevention' }
  ];

  return (
    <section id="awareness" className="awareness-section">
      <div className="container">
        <ScrollReveal>
          <div className="section-header">
            <span className="section-label">KNOWLEDGE CENTER</span>
            <h2 className="section-title">Understanding Pneumonia</h2>
            <p className="section-subtitle">
              Empowering patients and professionals with critical awareness and insights.
            </p>
          </div>
        </ScrollReveal>

        <ScrollReveal delay={200}>
          <div className="tabs-navigation">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </ScrollReveal>

        <div className="tab-content-container">
          {/* OVERVIEW TAB */}
          {activeTab === 'overview' && (
            <div className="tab-pane active fade-in">
              <ScrollReveal delay={300}>
                <div className="overview-card">
                  <h3>What is Pneumonia?</h3>
                  <p>
                    Pneumonia is an infection that inflames the air sacs in one or both lungs. The air sacs may fill with fluid or pus (purulent material), causing cough with phlegm or pus, fever, chills, and difficulty breathing. A variety of organisms, including bacteria, viruses and fungi, can cause pneumonia.
                  </p>
                </div>
              </ScrollReveal>
              
              <div className="stats-container">
                <ScrollReveal delay={400} className="stat-card">
                  <div className="stat-icon">🌍</div>
                  <h4 className="stat-number">~2.5M</h4>
                  <p className="stat-label">lower-respiratory deaths/yr (WHO 2021) — pneumonia major contributor</p>
                </ScrollReveal>
                <ScrollReveal delay={500} className="stat-card">
                  <div className="stat-icon">👶</div>
                  <h4 className="stat-number">Leading</h4>
                  <p className="stat-label">infectious cause of death in children &lt;5y (WHO)</p>
                </ScrollReveal>
                <ScrollReveal delay={600} className="stat-card">
                  <div className="stat-icon">🏥</div>
                  <h4 className="stat-number">#1</h4>
                  <p className="stat-label">US childhood hospitalization reason (HCUP) — pneumonia</p>
                </ScrollReveal>
              </div>
            </div>
          )}

          {/* TYPES TAB */}
          {activeTab === 'types' && (
            <div className="tab-pane active fade-in types-grid">
              <ScrollReveal delay={300} className="type-card bacterial">
                <h3>Bacterial Pneumonia</h3>
                <p className="type-desc">The most common form, often caused by Streptococcus pneumoniae. It can occur on its own or develop after a viral cold or the flu.</p>
                <div className="type-details">
                  <h4>Common Causes:</h4>
                  <p>Streptococcus pneumoniae, Haemophilus influenzae</p>
                  <h4>X-ray Characteristics:</h4>
                  <p>Lobar consolidation, focal opacities, pleural effusions are common.</p>
                </div>
              </ScrollReveal>
              
              <ScrollReveal delay={400} className="type-card viral">
                <h3>Viral Pneumonia</h3>
                <p className="type-desc">Caused by various viruses, including influenza and SARS-CoV-2. It is typically milder but can become serious.</p>
                <div className="type-details">
                  <h4>Common Causes:</h4>
                  <p>Influenza viruses, RSV, SARS-CoV-2</p>
                  <h4>X-ray Characteristics:</h4>
                  <p>Diffuse, bilateral interstitial infiltrates, "ground-glass" opacities.</p>
                </div>
              </ScrollReveal>
            </div>
          )}

          {/* SYMPTOMS TAB — unified with data/diseaseInfo.js (ATS/IDSA) */}
          {activeTab === 'symptoms' && (
            <div className="tab-pane active fade-in symptoms-grid">
              {[
                { icon: '🤒', name: 'Fever', desc: 'Fever, sweating and shaking chills — often the first sign.' },
                { icon: '🗣️', name: 'Cough', desc: 'Persistent cough which may produce greenish, yellow or blood-tinged phlegm.' },
                { icon: '😮‍💨', name: 'Shortness of Breath', desc: 'Difficult or labored breathing, breathlessness even at rest or on light exertion.' },
                { icon: '⚡', name: 'Chest Pain', desc: 'Sharp or stabbing chest pain that worsens when you breathe deeply or cough.' },
                { icon: '🥱', name: 'Fatigue', desc: 'Extreme tiredness and weakness, general feeling of being unwell.' },
                { icon: '🧠', name: 'Confusion', desc: 'Changes in mental awareness — notably in adults age 65+ (ATS/IDSA).' }
              ].map((symptom, index) => (
                <ScrollReveal key={index} delay={300 + (index * 100)} className="symptom-card">
                  <div className="symptom-icon">{symptom.icon}</div>
                  <h4 className="symptom-name">{symptom.name}</h4>
                  <p className="symptom-desc">{symptom.desc}</p>
                </ScrollReveal>
              ))}
            </div>
          )}

          {/* PREVENTION TAB */}
          {activeTab === 'prevention' && (
            <div className="tab-pane active fade-in prevention-list">
              {[
                { title: 'Get Vaccinated', desc: 'Vaccines are available to prevent some types of pneumonia and the flu. Talk to your doctor about these shots.' },
                { title: 'Practice Good Hygiene', desc: 'Wash your hands regularly or use an alcohol-based hand sanitizer to protect yourself against respiratory infections.' },
                { title: 'Don\'t Smoke', desc: 'Smoking damages your lungs\' natural defenses against respiratory infections.' },
                { title: 'Keep Your Immune System Strong', desc: 'Get enough sleep, exercise regularly, and eat a healthy diet.' },
                { title: 'Avoid Sick People', desc: 'Limit your contact with people who have colds, the flu, or other respiratory illnesses.' }
              ].map((item, index) => (
                <ScrollReveal key={index} delay={300 + (index * 100)} className="prevention-card">
                  <div className="prevention-number">{index + 1}</div>
                  <div className="prevention-content">
                    <h4 className="prevention-title">{item.title}</h4>
                    <p className="prevention-desc">{item.desc}</p>
                  </div>
                </ScrollReveal>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default DiseaseAwareness;
