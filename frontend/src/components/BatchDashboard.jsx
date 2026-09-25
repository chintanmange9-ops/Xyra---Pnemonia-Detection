import React from 'react';
import './Dashboard.css';

const BatchDashboard = ({ batch, onReset }) => {
  if (!batch || batch.length === 0) return null;

  const okEntries = batch.filter(b => b.result);
  const failed = batch.filter(b => b.error);
  const counts = { Normal: 0, 'Bacterial Pneumonia': 0, 'Viral Pneumonia': 0, Unknown: 0 };
  okEntries.forEach(e => {
    const p = e.result.prediction || 'Unknown';
    counts[p] = (counts[p] || 0) + 1;
  });

  const downloadCSV = () => {
    const rows = [['filename','prediction','confidence','overallStatus','case_id','status','shapUrl']];
    batch.forEach(e => {
      if (e.result) {
        rows.push([`"${e.filename}"`, e.result.prediction, e.result.confidence, e.result.overallStatus, e.result.case_id, e.result.status, e.result.shapUrl || '']);
      } else {
        rows.push([`"${e.filename}"`, 'ERROR', '', '', '', e.error, '']);
      }
    });
    const csv = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `LungAI_Batch_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section id="dashboard" className="dashboard-section fade-in">
      <div className="section-header">
        <span className="section-label">BATCH RESULTS</span>
        <h2 className="section-heading">Folder Analysis — {batch.length} images</h2>
        <p className="section-subtitle">
          {okEntries.length} succeeded, {failed.length} failed — {new Date().toLocaleString()}
        </p>
      </div>

      <div className="dashboard-grid">
        <div className="card" style={{gridColumn:'1/-1'}}>
          <h3 className="card-title">Summary</h3>
          <div style={{display:'flex', gap:'12px', flexWrap:'wrap', marginTop:'8px'}}>
            {Object.entries(counts).filter(([,v])=>v>0).map(([k,v]) => (
              <span key={k} style={{padding:'6px 12px', background:'#f1f5f9', borderRadius:'20px', fontWeight:600, fontSize:'13px'}}>
                {k}: {v}
              </span>
            ))}
            <span style={{padding:'6px 12px', background: failed.length? '#fef2f2':'#f0fdf4', color: failed.length? '#dc2626':'#059669', borderRadius:'20px', fontWeight:600}}>
              Failed: {failed.length}
            </span>
          </div>
          <div style={{marginTop:'14px', display:'flex', gap:'10px'}}>
            <button className="btn-primary" onClick={downloadCSV}>Download CSV</button>
            <button className="btn-outline" onClick={onReset}>Analyze Another Folder</button>
          </div>
        </div>

        <div className="card" style={{gridColumn:'1/-1', overflow:'auto'}}>
          <h3 className="card-title">Per-Image Results</h3>
          <div style={{overflow:'auto'}}>
            <table style={{width:'100%', borderCollapse:'collapse', fontSize:'13px'}}>
              <thead>
                <tr style={{background:'#f8fafc', textAlign:'left'}}>
                  <th style={{padding:'8px', borderBottom:'1px solid #e2e8f0'}}>#</th>
                  <th style={{padding:'8px', borderBottom:'1px solid #e2e8f0'}}>Preview</th>
                  <th style={{padding:'8px', borderBottom:'1px solid #e2e8f0'}}>File</th>
                  <th style={{padding:'8px', borderBottom:'1px solid #e2e8f0'}}>Prediction</th>
                  <th style={{padding:'8px', borderBottom:'1px solid #e2e8f0'}}>Confidence</th>
                  <th style={{padding:'8px', borderBottom:'1px solid #e2e8f0'}}>Status</th>
                  <th style={{padding:'8px', borderBottom:'1px solid #e2e8f0'}}>SHAP</th>
                </tr>
              </thead>
              <tbody>
                {batch.map((entry, idx) => {
                  const r = entry.result;
                  const color = r ? (r.prediction==='Normal'? '#059669' : r.prediction==='Bacterial Pneumonia'? '#DC2626' : '#D97706') : '#64748b';
                  return (
                    <tr key={idx} style={{borderBottom:'1px solid #f1f5f9'}}>
                      <td style={{padding:'8px'}}>{idx+1}</td>
                      <td style={{padding:'8px'}}>
                        {entry.previewUrl ? <img src={entry.previewUrl} alt={entry.filename} style={{width:'56px', height:'56px', objectFit:'cover', borderRadius:'6px', border:'1px solid #e2e8f0'}} /> : <span style={{color:'#94a3b8'}}>—</span>}
                      </td>
                      <td style={{padding:'8px', maxWidth:'180px', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}} title={entry.filename}>{entry.filename}</td>
                      <td style={{padding:'8px', color, fontWeight:700}}>{r ? r.prediction : 'ERROR'}</td>
                      <td style={{padding:'8px'}}>{r ? `${r.confidence}%` : '—'}</td>
                      <td style={{padding:'8px'}}>{r ? r.status : <span style={{color:'#dc2626'}}>{entry.error?.slice(0,80)}</span>}</td>
                      <td style={{padding:'8px'}}>
                        {r?.shapUrl ? <a href={r.shapUrl} target="_blank" rel="noreferrer" style={{color:'#0891B2', fontWeight:600}}>View</a> : <span style={{color:'#cbd5e1'}}>—</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
};

export default BatchDashboard;
