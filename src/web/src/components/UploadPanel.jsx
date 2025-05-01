import React, { useState } from 'react';
import Dropzone from 'react-dropzone';
import './UploadPanel.css';

export default function UploadPanel() {
  const [file, setFile] = useState(null);
  const [tokens, setTokens] = useState(null);
  const PRICE = 0.00013;               // $/1K tokens

  const onDrop = async accepted => {
    const f = accepted[0];
    setFile(f);
    // client-side size heuristic (≈ 4 chars / token)
    const estTok = Math.ceil(f.size / 4);
    setTokens(estTok);
  };

  const upload = async () => {
    const body = new FormData();
    body.append('file', file);
    const res = await fetch('/api/upload-law', {
      method: 'POST',
      body
    });
    alert(await res.text());
  };

  return (
    <div className="upload-box">
      <Dropzone onDrop={onDrop}>
        {({getRootProps, getInputProps}) => (
          <section {...getRootProps()} className="drop">
            <input {...getInputProps()} />
            {file ? (
              <p>📄 {file.name}</p>
            ) : (
              <p>📥 Drag & drop regulation PDF here</p>
            )}
          </section>
        )}
      </Dropzone>

      {tokens && (
        <div className="est">
          <div>⚡ Est. tokens: <strong>{tokens.toLocaleString()}</strong></div>
          <div>💰 Cost: <strong>${(tokens/1000*PRICE).toFixed(2)}</strong></div>
        </div>
      )}

      <button
        disabled={!file}
        onClick={upload}
      >
        {file ? '➕ Process Document' : 'Upload a document to begin'}
      </button>
    </div>
  );
}