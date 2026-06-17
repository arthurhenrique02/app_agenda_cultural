import { useNavigate } from "react-router-dom";
import * as api from "../services/api";
import EventForm from "../components/EventForm";
import type { EventCreateRequest } from "../types/api";

export default function CreateEventPage() {
  const navigate = useNavigate();

  async function handleSubmit(data: EventCreateRequest) {
    await api.createEvent(data);
    navigate("/events/me");
  }

  return (
    <div className="container" style={{ maxWidth: "800px", margin: "0 auto", padding: "40px 20px" }}>
      <h1 style={{ marginBottom: "30px", textAlign: "center" }}>Criar Novo Evento</h1>
      <p style={{ marginBottom: "40px", textAlign: "center", color: "#666" }}>
        Preencha os dados abaixo para submeter seu evento para aprovação.
      </p>
      
      <div style={{ backgroundColor: "#fff", padding: "30px", borderRadius: "8px", border: "1px solid #ddd" }}>
        <EventForm 
          onSubmit={handleSubmit} 
          submitLabel="Enviar para Aprovação" 
        />
      </div>
    </div>
  );
}
