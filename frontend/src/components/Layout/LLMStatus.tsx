import React, { useEffect, useState } from 'react';
import { fetchHealth } from '../../api/healthApi';

export default function LLMStatus() {
  const [health, setHealth] = useState<{ status: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch((e) => {
        setError('Unable to fetch backend health');
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Checking LLM status…</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!health) return <div>Backend status unknown</div>;

  return (
    <div style={{ fontSize: 14, padding: 4 }}>
      <b>Backend:</b>{' '}
      <span style={{ color: health.status === 'ok' ? 'green' : 'red', fontWeight: 500 }}>
        {health.status === 'ok' ? 'Connected' : health.status}
      </span>
    </div>
  );
}
