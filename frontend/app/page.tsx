"use client";

import { useEffect, useState } from "react";

interface HealthStatus {
  status: string;
  service: string;
}

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkApi = async () => {
      try {
        const res = await fetch("http://localhost:8000/health");
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        setHealth(data);
      } catch (err: any) {
        setError(err.message || "Failed to connect to API");
      } finally {
        setLoading(false);
      }
    };
    checkApi();
  }, []);

  return (
    <main style={{ padding: "40px", maxWidth: "800px", margin: "0 auto" }}>
      <header style={{ marginBottom: "32px", borderBottom: "1px solid #334155", paddingBottom: "16px" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold", color: "#3b82f6" }}>SENTINEL-RAG</h1>
        <p style={{ color: "#94a3b8" }}>
          Self-Evaluating Evidence-Navigating, Trust-Calibrated RAG System
        </p>
      </header>

      <section style={{ backgroundColor: "#1e293b", padding: "24px", borderRadius: "8px" }}>
        <h2 style={{ fontSize: "1.25rem", marginBottom: "16px" }}>API Status</h2>
        {loading && <p style={{ color: "#e2e8f0" }}>Checking API connection...</p>}
        {error && (
          <div style={{ color: "#ef4444", border: "1px solid #ef4444", padding: "12px", borderRadius: "6px" }}>
            <strong>Offline / Error:</strong> {error}
          </div>
        )}
        {health && (
          <div style={{ color: "#22c55e", border: "1px solid #22c55e", padding: "12px", borderRadius: "6px" }}>
            <p style={{ margin: "0 0 8px 0" }}><strong>Status:</strong> Connected / Available</p>
            <p style={{ margin: 0 }}><strong>Service:</strong> {health.service}</p>
          </div>
        )}
      </section>

      <footer style={{ marginTop: "40px", color: "#64748b", fontSize: "0.875rem" }}>
        <p>Phase 1 Skeleton — Production Foundation</p>
      </footer>
    </main>
  );
}
