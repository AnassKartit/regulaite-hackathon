import React, { useState } from 'react';
import UploadPanel from './components/UploadPanel';
import Heatmap from './components/Heatmap';
import './App.css';

export default function App() {
  const [reports, setReports] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [pdfName, setPdfName] = useState('');
  const [error, setError] = useState(null);

  const runScan = async () => {
    setIsScanning(true);
    setError(null);
    
    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        body: '{}'
      });
      
      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      const data = await res.json();
      setReports(data.reports);
      setPdfName(data.pdf);
    } catch (err) {
      setError(err.message);
      console.error('Scan failed:', err);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>
          <span style={{ marginRight: '8px' }}>🛡️</span>
          RegulAIte Compliance Scanner
        </h1>
        <div className="actions">
          <button 
            onClick={runScan}
            disabled={isScanning}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <span>{isScanning ? '⚡' : '🔍'}</span>
            {isScanning ? 'Scanning...' : 'Run Compliance Scan'}
          </button>
        </div>
      </header>
      
      <main style={{ position: 'relative' }}>
        {isScanning && (
          <div className="scanning-overlay">
            <div className="scanning-beam" />
            <span className="scanning-icon">⚡</span>
            <div>Scanning system for compliance risks...</div>
          </div>
        )}

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}
        
        <div style={{ 
          display: 'grid',
          gridTemplateColumns: '320px 1fr',
          gap: '2rem',
          alignItems: 'start'
        }}>
          <div>
            <h2 style={{ margin: '0 0 1rem', fontSize: '1.25rem', fontWeight: 600 }}>
              Upload Regulations
            </h2>
            <UploadPanel />
          </div>

          <div>
            <Heatmap reports={reports} />
            {pdfName && (
              <div style={{ marginTop: '1rem' }}>
                <a 
                  href={`/api/pdf/${pdfName}`}
                  className="download-link"
                >
                  📄 Download Compliance Report
                </a>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}