import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as api from "../services/api";
import type { EventResponse } from "../types/api";

export default function MyEventsPage() {
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadEvents();
  }, [page]);

  async function loadEvents() {
    setLoading(true);
    try {
      const res = await api.getMyEvents(page);
      setEvents(res.items);
      setTotalPages(res.pages);
    } catch (err) {
      setError("Falha ao carregar seus eventos.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm("Tem certeza que deseja cancelar este evento? Esta ação não pode ser desfeita.")) {
      return;
    }

    try {
      await api.deleteEvent(id);
      if (events.length === 1 && page > 1) {
        setPage(page - 1);
      } else {
        loadEvents();
      }
    } catch (err) {
      alert("Falha ao excluir evento.");
      console.error(err);
    }
  }

  const getStatusStyle = (status: string) => {
    switch (status) {
      case "aprovado": return { color: "#2f855a", backgroundColor: "#f0fff4" };
      case "pendente": return { color: "#c05621", backgroundColor: "#fffaf0" };
      case "rejeitado": return { color: "#c53030", backgroundColor: "#fff5f5" };
      case "cancelado": return { color: "#4a5568", backgroundColor: "#edf2f7" };
      default: return {};
    }
  };

  return (
    <div className="container" style={{ maxWidth: "1000px", margin: "0 auto", padding: "40px 20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "40px" }}>
        <h1 style={{ margin: 0 }}>Meus Eventos</h1>
        <Link 
          to="/events/new" 
          style={{ padding: "10px 20px", backgroundColor: "#007bff", color: "#fff", borderRadius: "4px", textDecoration: "none", fontWeight: "bold" }}
        >
          + Novo Evento
        </Link>
      </div>

      {loading && <div style={{ textAlign: "center", padding: "40px" }}>Carregando...</div>}
      
      {error && (
        <div style={{ padding: "15px", backgroundColor: "#fff5f5", color: "#c53030", borderRadius: "8px", textAlign: "center" }}>
          {error}
        </div>
      )}

      {!loading && !error && events.length === 0 && (
        <div style={{ textAlign: "center", padding: "40px", backgroundColor: "#f9f9f9", borderRadius: "8px" }}>
          <p style={{ color: "#666", marginBottom: "20px" }}>Você ainda não cadastrou nenhum evento.</p>
          <Link to="/events/new" style={{ color: "#007bff", fontWeight: "bold" }}>Cadastre seu primeiro evento agora!</Link>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {events.map((event) => (
          <div key={event.id} style={{ display: "flex", padding: "20px", border: "1px solid #ddd", borderRadius: "8px", backgroundColor: "#fff", gap: "20px" }}>
            <div style={{ width: "120px", height: "120px", backgroundColor: "#f0f0f0", borderRadius: "4px", overflow: "hidden", flexShrink: 0 }}>
              {event.image_url ? (
                <img src={event.image_url} alt={event.title} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              ) : (
                <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", color: "#999", fontSize: "0.8rem" }}>Sem foto</div>
              )}
            </div>

            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
                <h3 style={{ margin: 0 }}>{event.title}</h3>
                <span style={{ 
                  padding: "4px 12px", 
                  borderRadius: "20px", 
                  fontSize: "0.8rem", 
                  fontWeight: "bold",
                  textTransform: "uppercase",
                  ...getStatusStyle(event.status)
                }}>
                  {event.status}
                </span>
              </div>
              
              <p style={{ margin: "0 0 5px 0", color: "#666", fontSize: "0.9rem" }}>
                {new Date(event.date).toLocaleDateString("pt-BR")} às {event.start_time.substring(0, 5)}
              </p>
              <p style={{ margin: "0 0 10px 0", color: "#666", fontSize: "0.9rem" }}>
                {event.venue_name} - {event.neighborhood}
              </p>

              {event.status === "rejeitado" && event.rejection_reason && (
                <div style={{ marginTop: "10px", padding: "10px", backgroundColor: "#fff5f5", borderRadius: "4px", borderLeft: "4px solid #c53030" }}>
                  <p style={{ margin: 0, fontSize: "0.85rem", color: "#c53030" }}>
                    <strong>Motivo da rejeição:</strong> {event.rejection_reason}
                  </p>
                </div>
              )}

              <div style={{ marginTop: "15px", display: "flex", gap: "15px" }}>
                {event.status !== "cancelado" && (
                  <Link to={`/events/${event.id}/edit`} style={{ color: "#007bff", textDecoration: "none", fontSize: "0.9rem", fontWeight: "bold" }}>Editar</Link>
                )}
                {event.status !== "cancelado" && (
                  <button
                    onClick={() => handleDelete(event.id)}
                    style={{ background: "none", border: "none", padding: 0, color: "#c53030", cursor: "pointer", fontSize: "0.9rem", fontWeight: "bold" }}
                  >
                    Cancelar
                  </button>
                )}
                {event.status === "aprovado" && (
                  <Link to={`/events/${event.id}`} style={{ color: "#666", textDecoration: "none", fontSize: "0.9rem" }}>Ver público</Link>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div style={{ marginTop: "40px", display: "flex", justifyContent: "center", gap: "10px", alignItems: "center" }}>
          <button 
            disabled={page === 1} 
            onClick={() => setPage(p => p - 1)}
            style={{ padding: "8px 16px", borderRadius: "4px", border: "1px solid #ddd", cursor: page === 1 ? "default" : "pointer" }}
          >
            Anterior
          </button>
          <span style={{ color: "#666" }}>Página {page} de {totalPages}</span>
          <button 
            disabled={page === totalPages} 
            onClick={() => setPage(p => p + 1)}
            style={{ padding: "8px 16px", borderRadius: "4px", border: "1px solid #ddd", cursor: page === totalPages ? "default" : "pointer" }}
          >
            Próxima
          </button>
        </div>
      )}
    </div>
  );
}
