import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import * as api from "../services/api";
import type { EventResponse, CategoryResponse } from "../types/api";

export default function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [event, setEvent] = useState<EventResponse | null>(null);
  const [category, setCategory] = useState<CategoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);

  useEffect(() => {
    if (!id) return;

    async function loadData() {
      setLoading(true);
      try {
        const eventData = await api.getEvent(Number(id));
        setEvent(eventData);
        
        // Load category name
        const categories = await api.listCategories();
        const cat = categories.find(c => c.id === eventData.category_id);
        if (cat) setCategory(cat);
      } catch (err) {
        setError("Evento não encontrado ou erro ao carregar detalhes.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [id]);

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  if (loading) return <div style={{ textAlign: "center", padding: "100px" }}>Carregando detalhes do evento...</div>;

  if (error || !event) {
    return (
      <div style={{ textAlign: "center", padding: "100px" }}>
        <p style={{ color: "#c53030", marginBottom: "20px" }}>{error || "Evento não encontrado."}</p>
        <button onClick={() => navigate("/")} style={{ padding: "10px 20px", cursor: "pointer" }}>Voltar para a Home</button>
      </div>
    );
  }

  const eventDate = new Date(event.date).toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="container" style={{ maxWidth: "900px", margin: "0 auto", padding: "40px 20px" }}>
      <button 
        onClick={() => navigate(-1)} 
        style={{ background: "none", border: "none", color: "#007bff", cursor: "pointer", marginBottom: "20px", fontSize: "1rem" }}
      >
        ← Voltar
      </button>

      <div style={{ backgroundColor: "#fff", borderRadius: "12px", border: "1px solid #ddd", overflow: "hidden", boxShadow: "0 4px 6px rgba(0,0,0,0.05)" }}>
        {/* Imagem de Destaque */}
        <div className="feature-image" style={{ height: "400px", backgroundColor: "#f0f0f0", display: "flex", alignItems: "center", justifyContent: "center" }}>
          {event.image_url ? (
            <img src={event.image_url} alt={event.title} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          ) : (
            <span style={{ color: "#999", fontSize: "1.2rem" }}>Sem imagem disponível</span>
          )}
        </div>

        <div style={{ padding: "40px" }}>
          <div className="event-detail-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "20px" }}>
            <div>
              <span style={{ 
                padding: "4px 12px", 
                backgroundColor: "#e2e8f0", 
                borderRadius: "20px", 
                fontSize: "0.8rem", 
                fontWeight: "bold", 
                color: "#4a5568",
                textTransform: "uppercase"
              }}>
                {category?.name || "Categoria"}
              </span>
              <h1 style={{ fontSize: "2.5rem", margin: "10px 0 0 0", color: "#1a202c" }}>{event.title}</h1>
            </div>
            
            <button 
              onClick={handleShare}
              style={{ 
                padding: "10px 20px", 
                backgroundColor: copySuccess ? "#48bb78" : "#edf2f7", 
                color: copySuccess ? "#fff" : "#4a5568",
                border: "none",
                borderRadius: "8px",
                fontWeight: "bold",
                cursor: "pointer",
                transition: "all 0.2s"
              }}
            >
              {copySuccess ? "✓ Link Copiado!" : "🔗 Compartilhar"}
            </button>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "30px", marginBottom: "40px" }}>
            <div>
              <h4 style={{ margin: "0 0 10px 0", color: "#718096", textTransform: "uppercase", fontSize: "0.8rem" }}>Data e Horário</h4>
              <p style={{ margin: 0, fontSize: "1.1rem", fontWeight: "500" }}>{eventDate}</p>
              <p style={{ margin: "5px 0 0 0", color: "#4a5568" }}>
                Das {event.start_time.substring(0, 5)} {event.end_time ? `às ${event.end_time.substring(0, 5)}` : ""}
              </p>
            </div>

            <div>
              <h4 style={{ margin: "0 0 10px 0", color: "#718096", textTransform: "uppercase", fontSize: "0.8rem" }}>Localização</h4>
              <p style={{ margin: 0, fontSize: "1.1rem", fontWeight: "500" }}>{event.venue_name}</p>
              <p style={{ margin: "5px 0 0 0", color: "#4a5568" }}>
                {event.address}<br />
                {event.neighborhood}, {event.city}
              </p>
            </div>
          </div>

          <hr style={{ border: "none", borderTop: "1px solid #eee", marginBottom: "40px" }} />

          <div>
            <h4 style={{ margin: "0 0 20px 0", color: "#718096", textTransform: "uppercase", fontSize: "0.8rem" }}>Sobre o Evento</h4>
            <div style={{ fontSize: "1.1rem", lineHeight: "1.8", color: "#2d3748", whiteSpace: "pre-wrap" }}>
              {event.description}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
