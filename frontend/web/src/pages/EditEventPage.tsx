import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import * as api from "../services/api";
import EventForm from "../components/EventForm";
import type { EventResponse, EventCreateRequest } from "../types/api";

export default function EditEventPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [event, setEvent] = useState<EventResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    
    api.getEvent(Number(id))
      .then(setEvent)
      .catch((err) => {
        setError("Não foi possível carregar os dados do evento.");
        console.error(err);
      })
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSubmit(data: EventCreateRequest) {
    if (!id) return;
    await api.updateEvent(Number(id), data);
    navigate("/events/me");
  }

  if (loading) return <div style={{ textAlign: "center", padding: "100px" }}>Carregando dados...</div>;
  
  if (error || !event) {
    return (
      <div style={{ textAlign: "center", padding: "100px", color: "#c53030" }}>
        {error || "Evento não encontrado."}
      </div>
    );
  }

  return (
    <div className="container" style={{ maxWidth: "800px", margin: "0 auto", padding: "40px 20px" }}>
      <h1 style={{ marginBottom: "30px", textAlign: "center" }}>Editar Evento</h1>
      
      {event.status === "aprovado" && (
        <div style={{ 
          padding: "15px", 
          backgroundColor: "#fffaf0", 
          border: "1px solid #feebc8", 
          borderRadius: "8px", 
          color: "#c05621", 
          marginBottom: "30px",
          display: "flex",
          gap: "10px",
          alignItems: "center"
        }}>
          <span style={{ fontSize: "1.5rem" }}>⚠️</span>
          <p style={{ margin: 0, fontWeight: "bold" }}>
            Atenção: como este evento já está aprovado, ao salvar as alterações ele voltará para a fila de aprovação e ficará temporariamente invisível na listagem pública.
          </p>
        </div>
      )}
      
      <div style={{ backgroundColor: "#fff", padding: "30px", borderRadius: "8px", border: "1px solid #ddd" }}>
        <EventForm 
          initialData={event}
          onSubmit={handleSubmit} 
          submitLabel="Salvar Alterações" 
        />
      </div>
    </div>
  );
}
