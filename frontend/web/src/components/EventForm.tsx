import { useState, useEffect } from "react";
import * as api from "../services/api";
import type { CategoryResponse, EventCreateRequest, EventResponse } from "../types/api";

interface EventFormProps {
  initialData?: EventResponse;
  onSubmit: (data: EventCreateRequest) => Promise<void>;
  submitLabel: string;
}

export default function EventForm({ initialData, onSubmit, submitLabel }: EventFormProps) {
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form fields
  const [title, setTitle] = useState(initialData?.title || "");
  const [description, setDescription] = useState(initialData?.description || "");
  const [categoryId, setCategoryId] = useState(initialData?.category_id?.toString() || "");
  const [date, setDate] = useState(initialData?.date || "");
  const [startTime, setStartTime] = useState(initialData?.start_time || "");
  const [endTime, setEndTime] = useState(initialData?.end_time || "");
  const [venueName, setVenueName] = useState(initialData?.venue_name || "");
  const [address, setAddress] = useState(initialData?.address || "");
  const [neighborhood, setNeighborhood] = useState(initialData?.neighborhood || "");
  const [city, setCity] = useState(initialData?.city || "");
  const [imageUrl, setImageUrl] = useState(initialData?.image_url || "");
  const [uploadingImage, setUploadingImage] = useState(false);

  useEffect(() => {
    api.listCategories()
      .then(setCategories)
      .finally(() => setLoadingCategories(false));
  }, []);

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingImage(true);
    setError(null);
    try {
      const res = await api.uploadImage(file);
      setImageUrl(res.url);
    } catch (err: any) {
      setError("Falha ao enviar imagem. Verifique o tamanho (máx 5MB) e formato (jpg, png, webp).");
      console.error(err);
    } finally {
      setUploadingImage(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const data: EventCreateRequest = {
      title,
      description,
      category_id: Number(categoryId),
      date,
      start_time: startTime,
      end_time: endTime || null,
      venue_name: venueName,
      address,
      neighborhood,
      city,
      image_url: imageUrl || null,
    };

    try {
      await onSubmit(data);
    } catch (err: any) {
      setError("Erro ao salvar evento. Verifique se todos os campos estão preenchidos corretamente.");
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {error && (
        <div style={{ padding: "12px", backgroundColor: "#fff5f5", color: "#c53030", borderRadius: "4px", fontSize: "0.9rem" }}>
          {error}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div style={{ gridColumn: "1 / -1" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Título do Evento *</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" }}
          />
        </div>

        <div style={{ gridColumn: "1 / -1" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Descrição *</label>
          <textarea
            required
            rows={5}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box", fontFamily: "inherit" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Categoria *</label>
          <select
            required
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            disabled={loadingCategories}
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" }}
          >
            <option value="">Selecione...</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Data *</label>
          <input
            type="date"
            required
            value={date}
            onChange={(e) => setDate(e.target.value)}
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Hora Início *</label>
          <input
            type="time"
            required
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Hora Fim (Opcional)</label>
          <input
            type="time"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Nome do Local *</label>
          <input
            type="text"
            required
            value={venueName}
            onChange={(e) => setVenueName(e.target.value)}
            placeholder="Ex: Teatro Municipal"
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Endereço Completo *</label>
          <input
            type="text"
            required
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Bairro *</label>
          <input
            type="text"
            required
            value={neighborhood}
            onChange={(e) => setNeighborhood(e.target.value)}
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Cidade *</label>
          <input
            type="text"
            required
            value={city}
            onChange={(e) => setCity(e.target.value)}
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" }}
          />
        </div>

        <div style={{ gridColumn: "1 / -1" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Imagem do Evento</label>
          <div style={{ display: "flex", gap: "20px", alignItems: "flex-start" }}>
            <div style={{ flex: 1 }}>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleImageUpload}
                disabled={uploadingImage}
                style={{ width: "100%", padding: "10px", border: "1px dashed #ccc", borderRadius: "4px" }}
              />
              <p style={{ fontSize: "0.8rem", color: "#666", marginTop: "5px" }}>Formatos: JPG, PNG, WEBP. Tamanho máx: 5MB.</p>
            </div>
            {imageUrl && (
              <div style={{ width: "100px", height: "100px", border: "1px solid #ddd", borderRadius: "4px", overflow: "hidden" }}>
                <img src={imageUrl} alt="Preview" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              </div>
            )}
          </div>
        </div>
      </div>

      <button
        type="submit"
        disabled={submitting || uploadingImage}
        style={{
          width: "100%",
          padding: "15px",
          backgroundColor: "#007bff",
          color: "#fff",
          border: "none",
          borderRadius: "4px",
          fontWeight: "bold",
          fontSize: "1rem",
          cursor: (submitting || uploadingImage) ? "not-allowed" : "pointer",
          marginTop: "20px",
          opacity: (submitting || uploadingImage) ? 0.7 : 1
        }}
      >
        {submitting ? "Salvando..." : submitLabel}
      </button>
    </form>
  );
}
