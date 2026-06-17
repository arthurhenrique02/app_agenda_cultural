import { useEffect, useState } from "react";
import * as api from "../services/api";
import type { EventResponse, CategoryResponse } from "../types/api";

export default function EventsPage() {
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("");

  useEffect(() => {
    api.listCategories().then(setCategories).catch(console.error);
  }, []);

  useEffect(() => {
    loadEvents();
  }, [page, statusFilter]);

  async function loadEvents() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listAllEvents(page, statusFilter || undefined);
      setEvents(res.items);
      setTotalPages(res.pages);
    } catch (err) {
      setError("Falha ao carregar eventos.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm("Tem certeza que deseja excluir permanentemente este evento?")) return;
    
    try {
      await api.deleteAdminEvent(id);
      setEvents(events.filter(e => e.id !== id));
      if (events.length === 1 && page > 1) setPage(page - 1);
    } catch (err) {
      alert("Erro ao excluir evento.");
      console.error(err);
    }
  }

  function handleEdit(id: number) {
    alert(`Funcionalidade de edição para o evento #${id} em desenvolvimento.`);
  }

  const getCategoryName = (id: number) => categories.find(c => c.id === id)?.name || id;

  const getStatusBadgeStyle = (status: string) => {
    const baseStyle = { padding: "4px 8px", borderRadius: "4px", fontSize: "0.8rem", fontWeight: "bold" };
    switch (status) {
      case "aprovado": return { ...baseStyle, backgroundColor: "#d4edda", color: "#155724" };
      case "pendente": return { ...baseStyle, backgroundColor: "#fff3cd", color: "#856404" };
      case "rejeitado": return { ...baseStyle, backgroundColor: "#f8d7da", color: "#721c24" };
      case "cancelado": return { ...baseStyle, backgroundColor: "#e2e3e5", color: "#383d41" };
      default: return baseStyle;
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "30px" }}>
        <h1>Todos os Eventos</h1>
        
        <div>
          <label style={{ marginRight: "10px", fontWeight: "bold" }}>Filtrar por Status:</label>
          <select 
            value={statusFilter} 
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc" }}
          >
            <option value="">Todos</option>
            <option value="pendente">Pendente</option>
            <option value="aprovado">Aprovado</option>
            <option value="rejeitado">Rejeitado</option>
            <option value="cancelado">Cancelado</option>
          </select>
        </div>
      </div>

      {loading && <p>Carregando...</p>}
      {error && <div style={{ color: "red", padding: "20px", border: "1px solid red", borderRadius: "8px" }}>{error}</div>}

      {!loading && !error && events.length === 0 && (
        <div style={{ padding: "40px", textAlign: "center", backgroundColor: "#fff", borderRadius: "8px", border: "1px solid #ddd" }}>
          <p style={{ color: "#666" }}>Nenhum evento encontrado.</p>
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
                <th style={{ padding: "12px 15px" }}>Status</th>
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
                  <td style={{ padding: "12px 15px" }}>
                    <span style={getStatusBadgeStyle(event.status)}>{event.status.toUpperCase()}</span>
                  </td>
                  <td style={{ padding: "12px 15px" }}>
                    <div style={{ display: "flex", gap: "10px" }}>
                      <button 
                        onClick={() => handleEdit(event.id)}
                        style={{ padding: "6px 12px", backgroundColor: "#007bff", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                      >
                        Editar
                      </button>
                      <button 
                        onClick={() => handleDelete(event.id)}
                        style={{ padding: "6px 12px", backgroundColor: "#dc3545", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                      >
                        Excluir
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
    </div>
  );
}
