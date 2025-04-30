import React from 'react';

export default function Heatmap({ reports }) {
  const riskColors = {
    unacceptable: "#a4262c",  // Microsoft red
    high: "#ca5010",          // Microsoft orange
    medium: "#8f7034",        // Microsoft gold/brown
    low: "#107c10"           // Microsoft green
  };

  const getRiskIcon = (level) => {
    switch(level) {
      case 'unacceptable': return '⛔';
      case 'high': return '⚠️';
      case 'medium': return '⚡';
      case 'low': return '✅';
      default: return '❓';
    }
  };

  return (
    <div>
      <h2 style={{ margin: "0 0 1rem", fontSize: "1.25rem", fontWeight: 600 }}>
        Compliance Risk Assessment
      </h2>
      
      <div className="risk-legend">
        {Object.entries(riskColors).map(([level, color]) => (
          <div key={level} className="risk-level" style={{ background: color }}>
            <span className="risk-icon">{getRiskIcon(level)}</span>
            {level.charAt(0).toUpperCase() + level.slice(1)}
          </div>
        ))}
      </div>

      <div className="risk-grid">
        {reports.map(r => (
          <div
            key={r.asset_id}
            className="risk-card"
            style={{
              borderColor: riskColors[r.risk_level]
            }}
          >
            <div className="risk-header" style={{ background: riskColors[r.risk_level] }}>
              <span className="risk-icon">{getRiskIcon(r.risk_level)}</span>
              <span>{r.risk_level.toUpperCase()}</span>
              <span className="confidence">{(r.confidence * 100).toFixed(0)}% confidence</span>
            </div>
            
            <div className="risk-content">
              <h3>{r.asset_id}</h3>
              <div className="risk-details">
                <div>
                  <strong>Articles:</strong> {r.articles.join(", ")}
                </div>
                <div>
                  <strong>Suggestions:</strong>
                  <ul>
                    {r.suggestions.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {reports.length === 0 && (
        <div className="no-data">
          No compliance reports yet. Run a scan to begin assessment.
        </div>
      )}

      <style jsx>{`
        .risk-legend {
          display: flex;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .risk-level {
          padding: 0.25rem 0.75rem;
          border-radius: 2px;
          color: white;
          font-size: 0.875rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .risk-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1rem;
        }

        .risk-card {
          background: white;
          border-radius: 4px;
          border: 1px solid;
          overflow: hidden;
        }

        .risk-header {
          padding: 0.5rem 1rem;
          color: white;
          font-weight: 500;
          font-size: 0.875rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .confidence {
          margin-left: auto;
          opacity: 0.9;
        }

        .risk-content {
          padding: 1rem;
        }

        .risk-content h3 {
          margin: 0 0 0.75rem;
          font-size: 1rem;
          font-weight: 600;
        }

        .risk-details {
          font-size: 0.875rem;
          color: #605e5c;
        }

        .risk-details ul {
          margin: 0.25rem 0 0;
          padding-left: 1.5rem;
        }

        .risk-details li {
          margin: 0.25rem 0;
        }

        .no-data {
          padding: 2rem;
          text-align: center;
          color: #605e5c;
          background: var(--background);
          border-radius: 4px;
          border: 1px solid var(--border);
        }
      `}</style>
    </div>
  );
}