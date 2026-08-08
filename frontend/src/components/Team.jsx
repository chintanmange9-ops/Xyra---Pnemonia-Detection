import React from 'react';
import { teamMembers, projectGuide, techStack } from '../data/teamMembers';
import ScrollReveal from './ui/ScrollReveal';
import './Team.css';

const Team = () => {
  // Helper to render inline SVG icons for tech badges
  const renderTechIcon = (iconType) => {
    switch (iconType) {
      case 'react':
        return (
          <svg className="tech-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="2" fill="currentColor"/>
            <ellipse cx="12" cy="12" rx="9" ry="4"/>
            <ellipse cx="12" cy="12" rx="9" ry="4" transform="rotate(60 12 12)"/>
            <ellipse cx="12" cy="12" rx="9" ry="4" transform="rotate(120 12 12)"/>
          </svg>
        );
      case 'python':
        return (
          <svg className="tech-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2C6.5 2 6 4 6 6v2h6v2H4c-2 0-3 1.5-3 4s1 4 3 4h2v-2c0-1.5 1-3 3-3h6c1.5 0 3-1.5 3-3V6c0-2-.5-4-6-4z"/>
            <path d="M12 22c5.5 0 6-2 6-4v-2h-6v-2h8c2 0 3-1.5 3-4s-1-4-3-4h-2v2c0 1.5-1 3-3 3h-6c-1.5 0-3 1.5-3 3v4c0 2 .5 4 6 4z"/>
            <circle cx="9" cy="5" r="1" fill="currentColor"/>
            <circle cx="15" cy="19" r="1" fill="currentColor"/>
          </svg>
        );
      case 'tensorflow':
        return (
          <svg className="tech-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        );
      case 'faiss':
        return (
          <svg className="tech-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <ellipse cx="12" cy="6" rx="8" ry="3"/>
            <path d="M4 6v6c0 1.66 3.58 3 8 3s8-1.34 8-3V6"/>
            <path d="M4 12v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6"/>
          </svg>
        );
      case 'gemini':
        return (
          <svg className="tech-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2z"/>
          </svg>
        );
      case 'gemini':
        return (
          <svg className="tech-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2z"/>
          </svg>
        );
      case 'vite':
        return (
          <svg className="tech-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
        );
      default:
        return (
          <svg className="tech-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="8"/>
          </svg>
        );
    }
  };

  return (
    <section id="team" className="team-section section-padding">
      <div className="container">
        {/* Section Header */}
        <ScrollReveal direction="up" delay={0}>
          <div className="team-header text-center">
            <span className="team-badge">OUR TEAM</span>
            <h2 className="team-title">Meet the Team</h2>
            <p className="team-subtitle">
              The multi-disciplinary engineering group behind the Explainable AI Chest X-Ray Disease Detection and Retrieval-Augmented Generation framework.
            </p>
          </div>
        </ScrollReveal>

        {/* Team Members Grid */}
        <div className="team-grid">
          {teamMembers.map((member, index) => (
            <ScrollReveal key={member.id} direction="up" delay={150 + index * 150}>
              <div className="team-card">
                {/* Avatar Circle */}
                <div className="team-avatar">
                  <span className="avatar-initials">{member.initials}</span>
                </div>

                {/* Info */}
                <h3 className="member-name">{member.name}</h3>
                <span className="member-role">{member.role}</span>
                <p className="member-bio">{member.bio}</p>

                {/* Social Links */}
                <div className="member-socials">
                  {member.github && (
                    <a 
                      href={member.github} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      aria-label={`${member.name}'s GitHub`}
                      className="social-link"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
                      </svg>
                    </a>
                  )}
                  {member.linkedin && (
                    <a 
                      href={member.linkedin} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      aria-label={`${member.name}'s LinkedIn`}
                      className="social-link"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                        <rect x="2" y="9" width="4" height="12"></rect>
                        <circle cx="4" cy="4" r="2"></circle>
                      </svg>
                    </a>
                  )}
                </div>
              </div>
            </ScrollReveal>
          ))}
        </div>

        {/* Project Guide Card */}
        <ScrollReveal direction="up" delay={600}>
          <div className="guide-card">
            <div className="guide-avatar">
              <span className="avatar-initials">{projectGuide.initials}</span>
            </div>
            <div className="guide-content">
              <div className="guide-header-row">
                <h4 className="guide-name">{projectGuide.name}</h4>
                <span className="guide-role-badge">{projectGuide.role}</span>
              </div>
              <p className="guide-dept">{projectGuide.department}</p>
              <p className="guide-bio">{projectGuide.bio}</p>
            </div>
          </div>
        </ScrollReveal>

        {/* Tech Stack Section */}
        <ScrollReveal direction="up" delay={750}>
          <div className="tech-stack-container text-center">
            <span className="tech-stack-label">BUILT WITH</span>
            <div className="tech-badges-row">
              {techStack.map((tech) => (
                <div key={tech.name} className="tech-badge">
                  {renderTechIcon(tech.icon)}
                  <span className="tech-name">{tech.name}</span>
                </div>
              ))}
            </div>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
};

export default Team;
