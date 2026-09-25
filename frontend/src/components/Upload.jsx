import React, { useState, useRef, useEffect } from 'react';
import './Upload.css';
import ScrollReveal from './ui/ScrollReveal';
import ProgressSteps from './ui/ProgressSteps';
import { analyzeXray, analyzeBatch } from '../services/api';

const steps = [
  'Preprocessing',
  'Classifying',
  'Generating SHAP Attribution',
  'Retrieving Knowledge',
  'Generating Report'
];

const analysisMessages = [
  'Analyzing pixel density...',
  'Detecting lung boundaries...',
  'Computing SHAP attribution...',
  'Mapping affected regions...',
  'Calculating opacities...',
  'Cross-referencing database...'
];

const Upload = ({ onAnalysisComplete, onBatchComplete }) => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [batchFiles, setBatchFiles] = useState([]);
  const [batchProgress, setBatchProgress] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const fileInputRef = useRef(null);
  const folderInputRef = useRef(null);

  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  // Cleanup batch object URLs if any (stored as _preview on file)
  useEffect(() => {
    return () => {
      batchFiles.forEach(f => f._preview && URL.revokeObjectURL(f._preview));
    };
  }, [batchFiles]);

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
    setBatchFiles([]);
    const url = URL.createObjectURL(selectedFile);
    setPreviewUrl(url);
    setAnalysisComplete(false);
    setIsAnalyzing(false);
    setCurrentStep(0);
  };

  const handleFolderChange = (e) => {
    const all = Array.from(e.target.files || []);
    const images = all.filter(f => {
      const extOk = /\.(jpe?g|png|webp|bmp|tiff)$/i.test(f.name);
      const typeOk = !f.type || f.type.startsWith('image/');
      return extOk && typeOk;
    });
    if (images.length === 0) {
      alert('No image files found in selected folder (need JPG/PNG/WEBP/BMP/TIFF)');
      return;
    }
    if (images.length > 50) {
      alert(`Folder contains ${images.length} images, limiting to first 50.`);
    }
    const limited = images.slice(0, 50);
    // attach preview for first 4 for UI (optional)
    limited.forEach(f => { try { f._preview = URL.createObjectURL(f); } catch {} });
    setBatchFiles(limited);
    setFile(null);
    if (previewUrl) { URL.revokeObjectURL(previewUrl); setPreviewUrl(null); }
    setAnalysisComplete(false);
    setIsAnalyzing(false);
    setCurrentStep(0);
    setBatchProgress(null);
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
    batchFiles.forEach(f => f._preview && URL.revokeObjectURL(f._preview));
    setBatchFiles([]);
    setPreviewUrl(null);
    setBatchProgress(null);
    setAnalysisComplete(false);
    setIsAnalyzing(false);
    setCurrentStep(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    if (folderInputRef.current) {
      folderInputRef.current.value = '';
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
      alert('Analysis failed: ' + (error.message || error));
      setIsAnalyzing(false);
    }
  };

  const handleAnalyzeBatch = async () => {
    if (batchFiles.length === 0) return;
    setIsAnalyzing(true);
    setAnalysisComplete(false);
    setBatchProgress({ done: 0, total: batchFiles.length, label: `Starting batch...` });
    try {
      // Sequential with per-image progress (better UX than single batch POST which appears stuck at 0/10 for 2 min)
      // We keep analyzeBatch as optional fast path only for small batches if backend is warm; but sequential gives live 1/10, 2/10 feedback
      const useSequential = true; // force sequential for live progress
      let data;
      if (useSequential) {
        const results = [];
        for (let i = 0; i < batchFiles.length; i++) {
          const f = batchFiles[i];
          setBatchProgress({ done: i, total: batchFiles.length, label: `Analyzing ${i+1}/${batchFiles.length}: ${f.name}` });
          setCurrentStep(Math.floor((i / batchFiles.length) * 5));
          try {
            const r = await analyzeXray(f, (p) => setCurrentStep(p.step));
            results.push({ filename: f.name, result: r });
          } catch (e) {
            console.error('Failed', f.name, e);
            results.push({ filename: f.name, error: e.message || String(e) });
          }
        }
        data = { success: true, count: batchFiles.length, ok: results.filter(r=>r.result).length, failed: results.filter(r=>r.error).length, results };
      } else {
        data = await analyzeBatch(batchFiles, (p) => {
          if (p && p.label) setBatchProgress({ done: 0, total: batchFiles.length, label: p.label });
        });
      }
      setAnalysisComplete(true);
      setTimeout(() => {
        setIsAnalyzing(false);
        // Build preview URLs map for dashboard
        const withPreview = data.results.map(entry => {
          const orig = batchFiles.find(b => b.name === entry.filename);
          return { ...entry, previewUrl: orig?._preview || null };
        });
        if (onBatchComplete) {
          onBatchComplete(withPreview);
        } else {
          // fallback to single dashboard with first result
          const first = withPreview.find(x => x.result);
          if (first) onAnalysisComplete(first.result, first.previewUrl);
        }
        setTimeout(() => {
          document.getElementById('dashboard')?.scrollIntoView({ behavior: 'smooth' });
        }, 500);
      }, 800);
    } catch (error) {
      console.error('Batch analysis failed:', error);
      alert('Batch analysis failed: ' + (error.message || error));
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
          {!file && batchFiles.length === 0 && (
            <>
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
                  accept="image/jpeg, image/png, image/webp, image/bmp, image/tiff" 
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
                <p className="file-types">Supports: JPEG, PNG, WEBP, BMP, TIFF (Single)</p>
              </div>
              <div className="upload-options" style={{marginTop:'18px', textAlign:'center'}}>
                <span className="or-divider" style={{display:'block', margin:'12px 0', color:'#64748b', fontWeight:600}}>— OR —</span>
                <input
                  type="file"
                  ref={folderInputRef}
                  onChange={handleFolderChange}
                  webkitdirectory="true"
                  directory=""
                  multiple
                  hidden
                  id="folder-input"
                />
                <button
                  type="button"
                  className="btn-folder"
                  onClick={() => folderInputRef.current && folderInputRef.current.click()}
                  style={{padding:'10px 18px', border:'1px solid #0891B2', background:'white', color:'#0891B2', borderRadius:'8px', cursor:'pointer', fontWeight:600, display:'inline-flex', alignItems:'center', gap:'8px'}}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                  Upload Folder (Batch — up to 50)
                </button>
                <p className="file-types" style={{marginTop:'8px'}}>Select a folder containing X-rays for batch analysis</p>
              </div>
            </>
          )}

          {batchFiles.length > 0 && !isAnalyzing && (
            <div className="preview-state">
              <div className="preview-card" style={{maxWidth:'640px'}}>
                <h4 style={{margin:'0 0 10px', color:'#0A1628'}}>Batch: {batchFiles.length} images selected</h4>
                <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(80px, 1fr))', gap:'8px', maxHeight:'160px', overflow:'auto', padding:'4px'}}>
                  {batchFiles.slice(0,12).map((f, i) => (
                    <div key={i} style={{textAlign:'center'}}>
                      <img src={f._preview} alt={f.name} style={{width:'80px', height:'80px', objectFit:'cover', borderRadius:'6px', border:'1px solid #e2e8f0'}} />
                      <div style={{fontSize:'10px', color:'#475569', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', maxWidth:'80px'}}>{f.name}</div>
                    </div>
                  ))}
                </div>
                {batchFiles.length > 12 && <div style={{fontSize:'12px', color:'#64748b', marginTop:'6px'}}>+ {batchFiles.length - 12} more</div>}
                <div style={{marginTop:'10px', fontSize:'12px', color:'#334155'}}>
                  Total size: {formatFileSize(batchFiles.reduce((a,b)=>a+b.size,0))} — will be processed via <code>/api/analyze-batch</code>
                </div>
              </div>
              <div className="preview-actions">
                <button className="btn-analyze" onClick={handleAnalyzeBatch}>
                  <svg className="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                  </svg>
                  Analyze Folder ({batchFiles.length})
                </button>
                <button className="btn-remove" onClick={handleRemove}>
                  Remove
                </button>
              </div>
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
              <div className="progress-ring-container" style={{width:'380px', height:'380px'}}>
                <svg className="progress-ring" width="380" height="380" style={{transform:'rotate(-90deg)'}}>
                  {/* Inner per-image progress (existing) */}
                  <circle 
                    className="progress-ring-circle-bg" 
                    stroke="rgba(8,145,178,0.08)" 
                    strokeWidth="6" 
                    fill="transparent" 
                    r="160" 
                    cx="190" 
                    cy="190" 
                    style={{strokeDasharray: 1005, strokeDashoffset: 0}}
                  />
                  <circle 
                    className="progress-ring-circle" 
                    stroke="var(--color-accent, #0891B2)" 
                    strokeWidth="6" 
                    fill="transparent" 
                    r="160" 
                    cx="190" 
                    cy="190" 
                    style={{strokeDasharray: 1005, strokeDashoffset: `${1005 - (currentStep / 5) * 1005}`, transition:'stroke-dashoffset 0.5s ease'}}
                  />
                  {/* Outer overall batch progress — only visible for folder upload */}
                  {batchFiles.length > 0 && (
                    <>
                      <circle 
                        stroke="rgba(10,22,40,0.08)" 
                        strokeWidth="8" 
                        fill="transparent" 
                        r="180" 
                        cx="190" 
                        cy="190" 
                        style={{strokeDasharray: 1131, strokeDashoffset: 0}}
                      />
                      <circle 
                        stroke="var(--color-primary, #0A1628)" 
                        strokeWidth="8" 
                        fill="transparent" 
                        r="180" 
                        cx="190" 
                        cy="190" 
                        strokeLinecap="round"
                        style={{
                          strokeDasharray: 1131, 
                          strokeDashoffset: `${1131 - ((batchProgress?.done || 0) / (batchProgress?.total || 1)) * 1131}`,
                          transition:'stroke-dashoffset 0.6s ease',
                          filter:'drop-shadow(0 0 6px rgba(10,22,40,0.2))'
                        }}
                      />
                    </>
                  )}
                </svg>
                {/* Center overall counter for batch */}
                {batchFiles.length > 0 && batchProgress && (
                  <div style={{position:'absolute', top:'50%', left:'50%', transform:'translate(-50%, -50%)', textAlign:'center', pointerEvents:'none', marginTop:'-10px'}}>
                    <div style={{fontSize:'11px', fontWeight:700, letterSpacing:'0.12em', color:'#64748b'}}>OVERALL</div>
                    <div style={{fontSize:'22px', fontWeight:800, color:'#0A1628', lineHeight:1}}>{batchProgress.done || 0}/{batchProgress.total}</div>
                    <div style={{fontSize:'11px', color:'#0891B2', fontWeight:600}}>{Math.round(((batchProgress.done||0)/batchProgress.total)*100)}%</div>
                  </div>
                )}
              </div>

              <div className={`scene-3d ${analysisComplete ? 'analysis-done' : ''}`}>
                <div className="pulse-rings">
                  <div className="pulse-ring ring-1"></div>
                  <div className="pulse-ring ring-2"></div>
                  <div className="pulse-ring ring-3"></div>
                </div>

                <div className="card-3d">
                  <img src={batchFiles.length > 0 ? batchFiles[0]._preview : previewUrl} alt="Analyzing" className="analysis-image" />
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
                {batchFiles.length > 0 && batchProgress ? batchProgress.label : (steps[currentStep] || 'Finalizing...')}
              </div>
            </div>
          )}
        </div>
      </ScrollReveal>
    </section>
  );
};

export default Upload;
