import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Redirect to the page they were trying to access, or home
  const from = (location.state as any)?.from?.pathname || "/";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError("Email ou senha inválidos.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: "400px", margin: "100px auto", padding: "30px", border: "1px solid #ddd", borderRadius: "8px", backgroundColor: "#fff" }}>
      <h2 style={{ textAlign: "center", marginBottom: "30px" }}>Entrar</h2>
      
      {error && (
        <div style={{ padding: "12px", backgroundColor: "#fff5f5", color: "#c53030", borderRadius: "4px", marginBottom: "20px", fontSize: "0.9rem", textAlign: "center" }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>E-mail</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="seu@email.com"
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" }}
          />
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}>Senha</label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="********"
            style={{ width: "100%", padding: "10px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{ 
            width: "100%", 
            padding: "12px", 
            backgroundColor: "#007bff", 
            color: "#fff", 
            border: "none", 
            borderRadius: "4px", 
            fontWeight: "bold", 
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? "Carregando..." : "Entrar"}
        </button>
      </form>

      <p style={{ marginTop: "20px", textAlign: "center", fontSize: "0.9rem" }}>
        Não tem uma conta? <Link to="/register" style={{ color: "#007bff", textDecoration: "none" }}>Cadastre-se</Link>
      </p>
    </div>
  );
}
