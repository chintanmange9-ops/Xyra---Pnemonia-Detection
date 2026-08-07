import React, { useState, useRef, useEffect } from 'react';
import './Upload.css';
import ScrollReveal from './ui/ScrollReveal';
import ProgressSteps from './ui/ProgressSteps';
import { analyzeXray } from '../services/api';

const steps = [
  'Preprocessing',
  'Classifying',
  'Generating Heatmap',
  'Retrieving Knowledge',
  'Generating Report'
];

const analysisMessages = [
  'Analyzing pixel density...',
  'Detecting lung boundaries...',
  'Computing Grad-CAM...',
  'Mapping affected regions...',
  'Calculating opacities...',
  'Cross-referencing database...'
];

const Upload = ({ onAnalysisComplete }) => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const fileInputRef = useRef(null);

  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  useEffect(() => {
    let interval;
    if (isAnalyzing) {
      interval = setInterval(() => {
        setMessageIndex((prev) => (prev + 1) % analysisMessages.length);
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isAnalyzing]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && (selectedFile.type === 'image/jpeg' || selectedFile.type === 'image/png')) {
      handleFile(selectedFile);
    }
  };

  const handleFile = (selectedFile) => {
    setFile(selectedFile);
    const url = URL.createObjectURL(selectedFile);
    setPreviewUrl(url);
    setAnalysisComplete(false);
    setIsAnalyzing(false);
    setCurrentStep(0);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type === 'image/jpeg' || droppedFile.type === 'image/png')) {
      handleFile(droppedFile);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleRemove = () => {
    setFile(null);
    setPreviewUrl(null);
    setAnalysisComplete(false);
    setIsAnalyzing(false);
    setCurrentStep(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    setAnalysisComplete(false);
    try {
      const results = await analyzeXray(file, (p) => {
        setCurrentStep(p.step);
      });
      setAnalysisComplete(true);
      
      // Delay to show completion animation
      setTimeout(() => {
        setIsAnalyzing(false);
        onAnalysisComplete(results, previewUrl);
        
        // Auto-scroll to dashboard
        setTimeout(() => {
          document.getElementById('dashboard')?.scrollIntoView({ behavior: 'smooth' });
        }, 500);
      }, 1000);
    } catch (error) {
      console.error('Analysis failed:', error);
      setIsAnalyzing(false);
    }
  };

  return (
    <section id="upload" className="upload-section">
      <ScrollReveal>
        <div className="section-header">
          <span className="section-label">DIAGNOSIS</span>
          <h2 className="section-heading">Analyze Your X-Ray</h2>
          <p className="section-subtitle">Upload a chest X-ray image for AI-powered analysis</p>
        </div>

        <div className="upload-container">
          {!file && (
            <div 
              className={`drop-zone ${isDragOver ? 'drag-over' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current.click()}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                accept="image/jpeg, image/png" 
                hidden 
              />
              <div className="upload-icon-wrapper">
                <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
              </div>
              <h3 className="drop-text-primary">Drag & drop your chest X-ray here</h3>
              <p className="drop-text-secondary">or click to browse</p>
              <p className="file-types">Supports: JPEG, PNG</p>
            </div>
          )}

          {file && !isAnalyzing && (
            <div className="preview-state">
              <div className="preview-card">
                <img src={previewUrl} alt="X-Ray Preview" className="preview-image" />
                <div className="file-info">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">{formatFileSize(file.size)}</span>
                </div>
              </div>
              <div className="preview-actions">
                <button className="btn-analyze" onClick={handleAnalyze}>
                  <svg className="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                  </svg>
                  Analyze X-Ray
                </button>
                <button className="btn-remove" onClick={handleRemove}>
                  Remove
                </button>
              </div>
            </div>
          )}

          {isAnalyzing && (
            <div className="analysis-state-3d">
              <div className="progress-ring-container">
                <svg className="progress-ring" width="340" height="340">
                  <circle 
                    className="progress-ring-circle-bg" 
                    stroke="rgba(8,145,178,0.1)" 
                    strokeWidth="6" 
                    fill="transparent" 
                    r="160" 
                    cx="170" 
                    cy="170" 
                  />
                  <circle 
                    className="progress-ring-circle" 
                    stroke="var(--color-accent, #0891B2)" 
                    strokeWidth="6" 
                    fill="transparent" 
                    r="160" 
                    cx="170" 
                    cy="170" 
                    style={{ strokeDashoffset: `${1005 - (currentStep / 5) * 1005}` }}
                  />
                </svg>
              </div>

              <div className={`scene-3d ${analysisComplete ? 'analysis-done' : ''}`}>
                <div className="pulse-rings">
                  <div className="pulse-ring ring-1"></div>
                  <div className="pulse-ring ring-2"></div>
                  <div className="pulse-ring ring-3"></div>
                </div>

                <div className="card-3d">
                  <img src={previewUrl} alt="Analyzing" className="analysis-image" />
                  <div className="grid-overlay"></div>
                  
                  {!analysisComplete && (
                    <div className="scanning-line">
                        <div className="scanning-trail"></div>
                    </div>
                  )}

                  <div className="corner-bracket top-left"></div>
                  <div className="corner-bracket top-right"></div>
                  <div className="corner-bracket bottom-left"></div>
                  <div className="corner-bracket bottom-right"></div>
                </div>

                <div className="data-stream top-left">
                  <span className="data-message" key={`tl-${messageIndex}`}>{analysisMessages[messageIndex]}</span>
                </div>
                <div className="data-stream top-right">
                  <span className="data-message" key={`tr-${messageIndex}`}>{analysisMessages[(messageIndex + 1) % analysisMessages.length]}</span>
                </div>
                <div className="data-stream bottom-left">
                  <span className="data-message" key={`bl-${messageIndex}`}>{analysisMessages[(messageIndex + 2) % analysisMessages.length]}</span>
                </div>
                <div className="data-stream bottom-right">
                  <span className="data-message" key={`br-${messageIndex}`}>{analysisMessages[(messageIndex + 3) % analysisMessages.length]}</span>
                </div>
              </div>

              <div className="status-text-flicker">
                {steps[currentStep] || 'Finalizing...'}
              </div>
            </div>
          )}
        </div>
      </ScrollReveal>
    </section>
  );
};

export default Upload;
