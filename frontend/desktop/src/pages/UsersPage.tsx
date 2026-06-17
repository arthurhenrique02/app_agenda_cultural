import { useEffect, useState } from "react";
import * as api from "../services/api";
import type { UserResponse } from "../types/api";

export default function UsersPage() {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadUsers();
  }, [page]);

  async function loadUsers() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.listUsers(page);
      setUsers(res.items);
      setTotalPages(res.pages);
    } catch (err) {
      setError("Falha ao carregar usuários.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handlePromote(id: number) {
    if (!window.confirm("Deseja promover este usuário a administrador?")) return;
    
    try {
      const updatedUser = await api.promoteUser(id);
      setUsers(users.map(u => u.id === id ? updatedUser : u));
    } catch (err) {
      alert("Erro ao promover usuário.");
      console.error(err);
    }
  }

  const getRoleBadgeStyle = (role: string) => {
    const baseStyle = { padding: "4px 8px", borderRadius: "4px", fontSize: "0.8rem", fontWeight: "bold" };
    return role === "admin" 
      ? { ...baseStyle, backgroundColor: "#cce5ff", color: "#004085" }
      : { ...baseStyle, backgroundColor: "#e2e3e5", color: "#383d41" };
  };

  return (
    <div>
      <h1 style={{ marginBottom: "30px" }}>Gerenciamento de Usuários</h1>

      {loading && <p>Carregando...</p>}
      {error && <div style={{ color: "red", padding: "20px", border: "1px solid red", borderRadius: "8px" }}>{error}</div>}

      {!loading && !error && users.length === 0 && (
        <div style={{ padding: "40px", textAlign: "center", backgroundColor: "#fff", borderRadius: "8px", border: "1px solid #ddd" }}>
          <p style={{ color: "#666" }}>Nenhum usuário encontrado.</p>
        </div>
      )}

      {users.length > 0 && (
        <div style={{ backgroundColor: "#fff", borderRadius: "8px", border: "1px solid #ddd", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
            <thead style={{ backgroundColor: "#f8f9fa", borderBottom: "2px solid #dee2e6" }}>
              <tr>
                <th style={{ padding: "12px 15px" }}>ID</th>
                <th style={{ padding: "12px 15px" }}>Nome</th>
                <th style={{ padding: "12px 15px" }}>E-mail</th>
                <th style={{ padding: "12px 15px" }}>Papel</th>
                <th style={{ padding: "12px 15px" }}>Data Cadastro</th>
                <th style={{ padding: "12px 15px" }}>Ações</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={{ padding: "12px 15px" }}>{user.id}</td>
                  <td style={{ padding: "12px 15px", fontWeight: "bold" }}>{user.name}</td>
                  <td style={{ padding: "12px 15px" }}>{user.email}</td>
                  <td style={{ padding: "12px 15px" }}>
                    <span style={getRoleBadgeStyle(user.role)}>{user.role.toUpperCase()}</span>
                  </td>
                  <td style={{ padding: "12px 15px" }}>{new Date(user.created_at).toLocaleDateString("pt-BR")}</td>
                  <td style={{ padding: "12px 15px" }}>
                    {user.role !== "admin" && (
                      <button 
                        onClick={() => handlePromote(user.id)}
                        style={{ padding: "6px 12px", backgroundColor: "#17a2b8", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                      >
                        Promover a Admin
                      </button>
                    )}
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
