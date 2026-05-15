import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import HomePage from "./pages/HomePage";
import EventDetailPage from "./pages/EventDetailPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import CreateEventPage from "./pages/CreateEventPage";
import EditEventPage from "./pages/EditEventPage";
import MyEventsPage from "./pages/MyEventsPage";

function Header() {
  const { user, logout } = useAuth();

  return (
    <nav style={{ padding: "1rem 2rem", borderBottom: "1px solid #eee", display: "flex", justifyContent: "space-between", alignItems: "center", backgroundColor: "#fff" }}>
      <Link to="/" style={{ fontSize: "1.5rem", fontWeight: "bold", textDecoration: "none", color: "#333" }}>
        Agenda Cultural
      </Link>

      <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
        <Link to="/" style={{ textDecoration: "none", color: "#666" }}>Início</Link>

        {user ? (
          <>
            <Link to="/events/me" style={{ textDecoration: "none", color: "#666" }}>Meus Eventos</Link>
            <Link to="/events/new" style={{ textDecoration: "none", color: "#666" }}>Criar Evento</Link>
            <span style={{ fontWeight: "bold", color: "#333" }}>Olá, {user.name}</span>
            <button 
              onClick={logout}
              style={{ padding: "6px 12px", borderRadius: "4px", border: "1px solid #ddd", background: "none", cursor: "pointer" }}
            >
              Sair
            </button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ textDecoration: "none", color: "#666" }}>Entrar</Link>
            <Link 
              to="/register" 
              style={{ padding: "8px 16px", backgroundColor: "#007bff", color: "#fff", borderRadius: "4px", textDecoration: "none" }}
            >
              Cadastrar
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/events/:id" element={<EventDetailPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected Routes */}
            <Route
              path="/events/new"
              element={
                <ProtectedRoute>
                  <CreateEventPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/events/:id/edit"
              element={
                <ProtectedRoute>
                  <EditEventPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/events/me"
              element={
                <ProtectedRoute>
                  <MyEventsPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
      </Router>
    </AuthProvider>
  );
}

export default App;

