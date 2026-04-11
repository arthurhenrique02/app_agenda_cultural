import { useParams } from "react-router-dom";

export default function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  return (
    <div>
      <h1>Detalhes do Evento #{id}</h1>
    </div>
  );
}
