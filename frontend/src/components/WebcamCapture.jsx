import React, { useEffect, useRef, useState } from 'react';

export default function WebcamCapture({ backendUrl = 'http://localhost:8000' }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    let stream;
    async function init() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
      } catch (e) {
        setError('Webcam permission denied or unavailable');
      }
    }
    init();
    return () => {
      if (stream) stream.getTracks().forEach(t => t.stop());
    };
  }, []);

  useEffect(() => {
    const interval = setInterval(async () => {
      if (isSending) return;
      if (!videoRef.current || !canvasRef.current) return;
      try {
        setIsSending(true);
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const width = 640;
        const height = 480;
        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(videoRef.current, 0, 0, width, height);
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8));
        const form = new FormData();
        form.append('file', blob, 'frame.jpg');
        const resp = await fetch(`${backendUrl}/analyze/`, { method: 'POST', body: form });
        if (!resp.ok) throw new Error(`Backend error: ${resp.status}`);
        const data = await resp.json();
        setResult(data);
      } catch (e) {
        setError(String(e.message || e));
      } finally {
        setIsSending(false);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [backendUrl, isSending]);

  const age = result?.age ?? null;
  const gender = result?.gender ?? null;
  const emotion = result?.emotion ?? null;
  const recommendations = result?.recommendations ?? [];

  return (
    <div style={{ position: 'relative', width: 640, height: 480 }}>
      <video ref={videoRef} style={{ width: 640, height: 480, background: '#000' }} muted playsInline />
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      <div style={{ position: 'absolute', top: 8, left: 8, padding: '8px 12px', background: 'rgba(0,0,0,0.6)', color: '#fff', borderRadius: 8 }}>
        <div>Age: {age ?? '--'}</div>
        <div>Gender: {gender ?? '--'}</div>
        <div>Emotion: {emotion ?? '--'}</div>
        {error && <div style={{ color: '#f66' }}>{error}</div>}
      </div>
      <div style={{ position: 'absolute', right: 8, top: 8, bottom: 8, overflow: 'auto', width: 260, background: 'rgba(255,255,255,0.9)', borderRadius: 8, padding: 8 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>Recommendations</div>
        {!recommendations.length && <div>No recommendations yet.</div>}
        <ul style={{ paddingLeft: 16 }}>
          {recommendations.map((it, idx) => (
            <li key={idx}>
              <a href={it.url} target="_blank" rel="noreferrer">[{it.source}] {it.title}</a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
