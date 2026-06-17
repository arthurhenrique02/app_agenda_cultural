import { useEffect, useState } from "react";
import * as api from "../services/api";
import type { CategoryResponse, EventResponse, PaginatedResponse } from "../types/api";
import EventCard from "../components/EventCard";
import FilterBar from "../components/FilterBar";

export default function HomePage() {
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // States for filters
  const [q, setQ] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [neighborhood, setNeighborhood] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Load categories once
  useEffect(() => {
    api.listCategories()
      .then(setCategories)
      .catch((err) => console.error("Falha ao carregar categorias:", err));
  }, []);

  // Load events when filters or page change
  useEffect(() => {
    async function loadEvents() {
      setLoading(true);
      setError(null);
      try {
        let res: PaginatedResponse<EventResponse>;
        
        if (q.length >= 2) {
          res = await api.searchEvents(q, page);
        } else {
          res = await api.listEvents({
            page,
            category_id: categoryId ? Number(categoryId) : undefined,
            date_from: dateFrom || undefined,
            date_to: dateTo || undefined,
            neighborhood: neighborhood || undefined,
          });
        }
        
        setEvents(res.items);
        setTotalPages(res.pages);
      } catch (err) {
        setError("Não foi possível carregar os eventos. Tente novamente mais tarde.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    // Debounce search if q is being typed
    const timer = setTimeout(loadEvents, q.length > 0 ? 500 : 0);
    return () => clearTimeout(timer);
  }, [q, categoryId, neighborhood, dateFrom, dateTo, page]);

  // Reset page to 1 when filters change (except page itself)
  useEffect(() => {
    setPage(1);
  }, [q, categoryId, neighborhood, dateFrom, dateTo]);

  return (
    <div className="container" style={{ maxWidth: "1200px", margin: "0 auto", padding: "20px" }}>
      <header style={{ marginBottom: "40px", textAlign: "center" }}>
        <h1 style={{ fontSize: "2.5rem", color: "#333" }}>Agenda Cultural</h1>
        <p style={{ fontSize: "1.2rem", color: "#666" }}>Descubra o melhor da cultura na sua cidade</p>
      </header>

      <FilterBar
        categories={categories}
        q={q}
        setQ={setQ}
        categoryId={categoryId}
        setCategoryId={setCategoryId}
        neighborhood={neighborhood}
        setNeighborhood={setNeighborhood}
        dateFrom={dateFrom}
        setDateFrom={setDateFrom}
        dateTo={dateTo}
        setDateTo={setDateTo}
      />

      {loading && <div style={{ textAlign: "center", padding: "40px" }}>Carregando eventos...</div>}
      
      {error && (
        <div style={{ padding: "20px", backgroundColor: "#fff5f5", color: "#c53030", borderRadius: "8px", marginBottom: "20px", textAlign: "center" }}>
          {error}
        </div>
      )}

      {!loading && !error && events.length === 0 && (
        <div style={{ textAlign: "center", padding: "40px", color: "#666" }}>
          Nenhum evento encontrado para os filtros selecionados.
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "30px" }}>
        {events.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>

      {totalPages > 1 && (
        <div style={{ marginTop: "40px", display: "flex", justifyContent: "center", gap: "10px" }}>
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            style={{ padding: "8px 16px", cursor: page === 1 ? "not-allowed" : "pointer" }}
          >
            Anterior
          </button>
          <span style={{ padding: "8px 16px" }}>
            Página {page} de {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            style={{ padding: "8px 16px", cursor: page === totalPages ? "not-allowed" : "pointer" }}
          >
            Próxima
          </button>
        </div>
      )}
    </div>
  );
}
