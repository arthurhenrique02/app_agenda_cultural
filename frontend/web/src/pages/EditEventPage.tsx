import { useParams } from "react-router-dom";

export default function EditEventPage() {
  const { id } = useParams<{ id: string }>();
  return (
    <div>
      <h1>Editar Evento #{id}</h1>
    </div>
  );
}
