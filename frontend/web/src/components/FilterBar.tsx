import type { CategoryResponse } from "../types/api";

interface FilterBarProps {
  categories: CategoryResponse[];
  q: string;
  setQ: (val: string) => void;
  categoryId: string;
  setCategoryId: (val: string) => void;
  neighborhood: string;
  setNeighborhood: (val: string) => void;
  dateFrom: string;
  setDateFrom: (val: string) => void;
  dateTo: string;
  setDateTo: (val: string) => void;
}

export default function FilterBar({
  categories,
  q,
  setQ,
  categoryId,
  setCategoryId,
  neighborhood,
  setNeighborhood,
  dateFrom,
  setDateFrom,
  dateTo,
  setDateTo,
}: FilterBarProps) {
  return (
    <div style={{ marginBottom: "30px", padding: "20px", backgroundColor: "#f9f9f9", borderRadius: "8px" }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px" }}>
        {/* Busca Textual */}
        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Buscar</label>
          <input
            type="text"
            placeholder="Título ou descrição..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
            style={{ width: "100%", padding: "8px", borderRadius: "4px", border: "1px solid #ccc" }}
          />
        </div>

        {/* Categorias */}
        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Categoria</label>
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            style={{ width: "100%", padding: "8px", borderRadius: "4px", border: "1px solid #ccc" }}
          >
            <option value="">Todas as Categorias</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>

        {/* Bairro */}
        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Bairro</label>
          <input
            type="text"
            placeholder="Filtrar por bairro..."
            value={neighborhood}
            onChange={(e) => setNeighborhood(e.target.value)}
            style={{ width: "100%", padding: "8px", borderRadius: "4px", border: "1px solid #ccc" }}
          />
        </div>

        {/* Data De */}
        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>A partir de</label>
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            style={{ width: "100%", padding: "8px", borderRadius: "4px", border: "1px solid #ccc" }}
          />
        </div>

        {/* Data Até */}
        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>Até</label>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            style={{ width: "100%", padding: "8px", borderRadius: "4px", border: "1px solid #ccc" }}
          />
        </div>
      </div>
    </div>
  );
}
