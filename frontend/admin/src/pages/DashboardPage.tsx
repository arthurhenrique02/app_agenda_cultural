import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as api from "../services/api";
import type { DashboardResponse } from "../types/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await api.getDashboardStats();
        setStats(data);
      } catch (err) {
        setError("Erro ao carregar estatísticas do dashboard.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  if (loading) return <p>Carregando métricas...</p>;
  if (error || !stats) return <div style={{ color: "red" }}>{error}</div>;

  const pendingCount = stats.pendente || 0;

  return (
    <div>
      <h1 style={{ marginBottom: "40px" }}>Dashboard</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "25px", marginBottom: "40px" }}>
        {/* Total Usuários */}
        <div style={{ backgroundColor: "#fff", padding: "25px", borderRadius: "10px", boxShadow: "0 2px 4px rgba(0,0,0,0.05)", borderLeft: "5px solid #3498db" }}>
          <h4 style={{ margin: "0 0 10px 0", color: "#7f8c8d", fontSize: "0.9rem", textTransform: "uppercase" }}>Total de Usuários</h4>
          <span style={{ fontSize: "2.5rem", fontWeight: "bold", color: "#2c3e50" }}>{stats.total_users}</span>
        </div>

        {/* Total Eventos */}
        <div style={{ backgroundColor: "#fff", padding: "25px", borderRadius: "10px", boxShadow: "0 2px 4px rgba(0,0,0,0.05)", borderLeft: "5px solid #9b59b6" }}>
          <h4 style={{ margin: "0 0 10px 0", color: "#7f8c8d", fontSize: "0.9rem", textTransform: "uppercase" }}>Total de Eventos</h4>
          <span style={{ fontSize: "2.5rem", fontWeight: "bold", color: "#2c3e50" }}>{stats.total_events}</span>
        </div>

        {/* Fila de Moderação */}
        <div style={{ 
          backgroundColor: pendingCount > 0 ? "#fffcf0" : "#fff", 
          padding: "25px", 
          borderRadius: "10px", 
          boxShadow: "0 2px 4px rgba(0,0,0,0.05)", 
          borderLeft: `5px solid ${pendingCount > 0 ? "#f1c40f" : "#27ae60"}` 
        }}>
          <h4 style={{ margin: "0 0 10px 0", color: "#7f8c8d", fontSize: "0.9rem", textTransform: "uppercase" }}>Aguardando Moderação</h4>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "2.5rem", fontWeight: "bold", color: pendingCount > 0 ? "#d4ac0d" : "#27ae60" }}>{pendingCount}</span>
            {pendingCount > 0 && (
              <Link to="/moderation" style={{ padding: "8px 16px", backgroundColor: "#f1c40f", color: "#fff", textDecoration: "none", borderRadius: "5px", fontWeight: "bold", fontSize: "0.8rem" }}>
                MODERAR AGORA
              </Link>
            )}
          </div>
        </div>
      </div>

      <h2 style={{ marginBottom: "20px", fontSize: "1.2rem", color: "#7f8c8d" }}>Distribuição por Status</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "20px" }}>
        <div style={{ backgroundColor: "#fff", padding: "20px", borderRadius: "8px", border: "1px solid #eee" }}>
          <span style={{ color: "#27ae60", fontWeight: "bold" }}>Aprovados:</span> {stats.aprovado || 0}
        </div>
        <div style={{ backgroundColor: "#fff", padding: "20px", borderRadius: "8px", border: "1px solid #eee" }}>
          <span style={{ color: "#e74c3c", fontWeight: "bold" }}>Rejeitados:</span> {stats.rejeitado || 0}
        </div>
        <div style={{ backgroundColor: "#fff", padding: "20px", borderRadius: "8px", border: "1px solid #eee" }}>
          <span style={{ color: "#95a5a6", fontWeight: "bold" }}>Cancelados:</span> {stats.cancelado || 0}
        </div>
      </div>
    </div>
  );
}
