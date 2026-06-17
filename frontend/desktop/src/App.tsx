import { HashRouter as Router, Routes, Route, Link, Outlet } from "react-router-dom";
import { AdminAuthProvider, useAdminAuth } from "./contexts/AdminAuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import ModerationPage from "./pages/ModerationPage";
import DashboardPage from "./pages/DashboardPage";
import EventsPage from "./pages/EventsPage";
import UsersPage from "./pages/UsersPage";

function AdminLayout() {
  const { user, logout } = useAdminAuth();

  return (
    <div style={{ display: "flex", minHeight: "100vh", backgroundColor: "#f4f7f6" }}>
      {/* Sidebar */}
      <nav style={{ width: "250px", backgroundColor: "#2c3e50", color: "#fff", padding: "20px" }}>
        <h2 style={{ marginBottom: "40px", fontSize: "1.5rem" }}>Admin AC</h2>
        <ul style={{ listStyle: "none", padding: 0 }}>
          <li style={{ marginBottom: "15px" }}>
            <Link to="/" style={{ color: "#bdc3c7", textDecoration: "none", fontWeight: "bold" }}>Dashboard</Link>
          </li>
          <li style={{ marginBottom: "15px" }}>
            <Link to="/moderation" style={{ color: "#bdc3c7", textDecoration: "none", fontWeight: "bold" }}>Moderação</Link>
          </li>
          <li style={{ marginBottom: "15px" }}>
            <Link to="/users" style={{ color: "#bdc3c7", textDecoration: "none", fontWeight: "bold" }}>Usuários</Link>
          </li>
          <li style={{ marginBottom: "15px" }}>
            <Link to="/events" style={{ color: "#bdc3c7", textDecoration: "none", fontWeight: "bold" }}>Todos os Eventos</Link>
          </li>
        </ul>
        
        <div style={{ marginTop: "auto", paddingTop: "40px", borderTop: "1px solid #34495e" }}>
          <p style={{ fontSize: "0.8rem", color: "#95a5a6", marginBottom: "10px" }}>Logado como:</p>
          <p style={{ fontWeight: "bold", marginBottom: "20px" }}>{user?.name}</p>
          <button 
            onClick={logout}
            style={{ width: "100%", padding: "10px", backgroundColor: "#e74c3c", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
          >
            Sair
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ flex: 1, padding: "40px" }}>
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AdminAuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route element={<ProtectedRoute><AdminLayout /></ProtectedRoute>}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/moderation" element={<ModerationPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/events" element={<EventsPage />} />
          </Route>
        </Routes>
      </Router>
    </AdminAuthProvider>
  );
}
