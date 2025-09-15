import React from 'react';
import WebcamCapture from '../components/WebcamCapture.jsx';

export default function App() {
  return (
    <div style={{ fontFamily: 'Inter, system-ui, Segoe UI, Roboto, Arial, sans-serif', minHeight: '100vh', background: '#0f172a', color: '#e2e8f0' }}>
      <div style={{ maxWidth: 1024, margin: '0 auto', padding: 24 }}>
        <h1 style={{ marginBottom: 16 }}>Live Age, Gender, Emotion with Recommendations</h1>
        <WebcamCapture />
      </div>
    </div>
  );
}


