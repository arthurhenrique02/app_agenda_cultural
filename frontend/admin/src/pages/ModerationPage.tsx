import { useEffect, useState } from "react";
import * as api from "../services/api";
import type { EventResponse, CategoryResponse } from "../types/api";

export default function ModerationPage() {
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Rejection modal state
  const [rejectingId, setRejectingId] = useState<number | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [submittingReject, setSubmittingReject] = useState(false);

  useEffect(() => {
    // Load categories for reference
    api.listCategories().then(setCategories).catch(console.error);
    loadPendingEvents();
  }, [page]);

  async function loadPendingEvents() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listPendingEvents(page);
      setEvents(res.items);
      setTotalPages(res.pages);
    } catch (err) {
      setError("Falha ao carregar eventos pendentes.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(id: number) {
    if (!window.confirm("Deseja aprovar este evento para publicação?")) return;
    
    try {
      await api.approveEvent(id);
      setEvents(events.filter(e => e.id !== id));
      if (events.length === 1 && page > 1) setPage(page - 1);
    } catch (err) {
      alert("Erro ao aprovar evento.");
      console.error(err);
    }
  }

  async function handleRejectSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!rejectingId || !rejectReason.trim()) return;

    setSubmittingReject(true);
    try {
      await api.rejectEvent(rejectingId, rejectReason);
      setEvents(events.filter(e => e.id !== rejectingId));
      setRejectingId(null);
      setRejectReason("");
      if (events.length === 1 && page > 1) setPage(page - 1);
    } catch (err) {
      alert("Erro ao rejeitar evento.");
      console.error(err);
    } finally {
      setSubmittingReject(false);
    }
  }

  const getCategoryName = (id: number) => categories.find(c => c.id === id)?.name || id;

  return (
    <div>
      <h1 style={{ marginBottom: "30px" }}>Moderação de Eventos</h1>

      {loading && <p>Carregando...</p>}
      {error && <div style={{ color: "red", padding: "20px", border: "1px solid red", borderRadius: "8px" }}>{error}</div>}

      {!loading && !error && events.length === 0 && (
        <div style={{ padding: "40px", textAlign: "center", backgroundColor: "#fff", borderRadius: "8px", border: "1px solid #ddd" }}>
          <p style={{ color: "#666" }}>Não há eventos pendentes de moderação no momento.</p>
        </div>
      )}

      {events.length > 0 && (
        <div style={{ backgroundColor: "#fff", borderRadius: "8px", border: "1px solid #ddd", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
            <thead style={{ backgroundColor: "#f8f9fa", borderBottom: "2px solid #dee2e6" }}>
              <tr>
                <th style={{ padding: "12px 15px" }}>ID</th>
                <th style={{ padding: "12px 15px" }}>Título</th>
                <th style={{ padding: "12px 15px" }}>Categoria</th>
                <th style={{ padding: "12px 15px" }}>Data</th>
                <th style={{ padding: "12px 15px" }}>Local</th>
                <th style={{ padding: "12px 15px" }}>Ações</th>
              </tr>
            </thead>
            <tbody>
              {events.map(event => (
                <tr key={event.id} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={{ padding: "12px 15px" }}>{event.id}</td>
                  <td style={{ padding: "12px 15px" }}>
                    <div style={{ fontWeight: "bold" }}>{event.title}</div>
                    <div style={{ fontSize: "0.8rem", color: "#666" }}>Por User #{event.created_by}</div>
                  </td>
                  <td style={{ padding: "12px 15px" }}>{getCategoryName(event.category_id)}</td>
                  <td style={{ padding: "12px 15px" }}>{new Date(event.date).toLocaleDateString("pt-BR")}</td>
                  <td style={{ padding: "12px 15px" }}>{event.venue_name}</td>
                  <td style={{ padding: "12px 15px" }}>
                    <div style={{ display: "flex", gap: "10px" }}>
                      <button 
                        onClick={() => handleApprove(event.id)}
                        style={{ padding: "6px 12px", backgroundColor: "#28a745", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                      >
                        Aprovar
                      </button>
                      <button 
                        onClick={() => setRejectingId(event.id)}
                        style={{ padding: "6px 12px", backgroundColor: "#dc3545", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                      >
                        Rejeitar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ marginTop: "20px", display: "flex", gap: "10px", justifyContent: "center" }}>
          <button disabled={page === 1} onClick={() => setPage(page - 1)}>Anterior</button>
          <span>Página {page} de {totalPages}</span>
          <button disabled={page === totalPages} onClick={() => setPage(page + 1)}>Próxima</button>
        </div>
      )}

      {/* Rejection Modal */}
      {rejectingId && (
        <div style={{ 
          position: "fixed", top: 0, left: 0, width: "100%", height: "100%", 
          backgroundColor: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center",
          zIndex: 1000
        }}>
          <div style={{ backgroundColor: "#fff", padding: "30px", borderRadius: "8px", width: "400px" }}>
            <h3>Rejeitar Evento #{rejectingId}</h3>
            <p style={{ color: "#666", fontSize: "0.9rem" }}>Por favor, informe o motivo da rejeição. O usuário poderá ver este motivo.</p>
            <form onSubmit={handleRejectSubmit}>
              <textarea 
                required
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                style={{ width: "100%", height: "100px", padding: "10px", marginBottom: "20px", borderRadius: "4px", border: "1px solid #ccc" }}
                placeholder="Ex: Descrição insuficiente ou imagem inadequada."
              />
              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
                <button 
                  type="button" 
                  onClick={() => { setRejectingId(null); setRejectReason(""); }}
                  style={{ padding: "8px 16px", background: "none", border: "1px solid #ccc", cursor: "pointer" }}
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  disabled={submittingReject}
                  style={{ padding: "8px 16px", backgroundColor: "#dc3545", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                >
                  {submittingReject ? "Enviando..." : "Confirmar Rejeição"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
