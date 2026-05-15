import { Link } from "react-router-dom";
import type { EventResponse } from "../types/api";

interface EventCardProps {
  event: EventResponse;
}

export default function EventCard({ event }: EventCardProps) {
  // Format date to local string
  const eventDate = new Date(event.date).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="event-card" style={{ border: "1px solid #ddd", borderRadius: "8px", overflow: "hidden", marginBottom: "20px", display: "flex", flexDirection: "column" }}>
      <div style={{ height: "200px", backgroundColor: "#f0f0f0", display: "flex", alignItems: "center", justifyContent: "center" }}>
        {event.image_url ? (
          <img src={event.image_url} alt={event.title} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <span style={{ color: "#999" }}>Sem Imagem</span>
        )}
      </div>
      
      <div style={{ padding: "15px", flex: 1 }}>
        <h3 style={{ margin: "0 0 10px 0" }}>{event.title}</h3>
        <p style={{ margin: "0 0 5px 0", color: "#666", fontSize: "0.9rem" }}>
          <strong>Data:</strong> {eventDate} às {event.start_time.substring(0, 5)}
        </p>
        <p style={{ margin: "0 0 5px 0", color: "#666", fontSize: "0.9rem" }}>
          <strong>Local:</strong> {event.venue_name} ({event.neighborhood})
        </p>
        <p style={{ margin: "10px 0", display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical", overflow: "hidden", textOverflow: "ellipsis" }}>
          {event.description}
        </p>
      </div>

      <div style={{ padding: "15px", borderTop: "1px solid #eee" }}>
        <Link 
          to={`/events/${event.id}`} 
          style={{ textDecoration: "none", color: "#007bff", fontWeight: "bold" }}
        >
          Ver Detalhes →
        </Link>
      </div>
    </div>
  );
}
