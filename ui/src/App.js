import React, { useEffect, useState } from 'react';
import ForceGraph3D from 'react-force-graph';

export default function App() {
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [feed, setFeed] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');
    ws.onmessage = e => {
      const msg = JSON.parse(e.data);
      setFeed(f => [...f, msg]);
      if (msg.type === 'subdomain') {
        setGraph(g => ({ ...g, nodes: [...g.nodes, { id: msg.host }] }));
      }
      if (msg.type === 'httpx') {
        setGraph(g => ({
          nodes: g.nodes,
          links: [...g.links, { source: msg.host, target: msg.url }]
        }));
      }
    };
    return () => ws.close();
  }, []);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <div style={{ width: '30%', overflow: 'auto', background: '#111', color: '#0f0', padding: '0.5rem' }}>
        {feed.map((f, i) => <div key={i}>{JSON.stringify(f)}</div>)}
      </div>
      <div style={{ flex: 1 }}>
        <ForceGraph3D graphData={graph} />
      </div>
    </div>
  );
}
