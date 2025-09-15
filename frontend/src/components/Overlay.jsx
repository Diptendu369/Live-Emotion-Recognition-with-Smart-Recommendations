import React from 'react';

export default function Overlay({ age, gender, emotion }) {
  return (
    <div style={{ position: 'absolute', top: 8, left: 8, padding: '8px 12px', background: 'rgba(0,0,0,0.6)', color: '#fff', borderRadius: 8 }}>
      <div>Age: {age ?? '--'}</div>
      <div>Gender: {gender ?? '--'}</div>
      <div>Emotion: {emotion ?? '--'}</div>
    </div>
  );
}
