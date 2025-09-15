import React from 'react';

export default function Recommendations({ items = [] }) {
  if (!items.length) {
    return <div>No recommendations yet.</div>;
  }
  return (
    <ul>
      {items.map((it, idx) => (
        <li key={idx}><a href={it.url} target=\"_blank\" rel=\"noreferrer\">{it.title}</a></li>
      ))}
    </ul>
  );
}
