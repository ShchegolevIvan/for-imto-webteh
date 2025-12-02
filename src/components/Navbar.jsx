// src/components/Navbar.jsx
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Navbar() {
  const { user, isAuthenticated, isVerifiedAuthor, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <header
      style={{
        borderBottom: "1px solid #ddd",
        marginBottom: 20,
        padding: "10px 20px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <Link
        to="/"
        style={{ textDecoration: "none", fontWeight: "bold", fontSize: 20 }}
      >
        NewsApp
      </Link>

      <nav style={{ display: "flex", gap: 16, alignItems: "center" }}>
        <Link to="/">Новости</Link>

        {(isVerifiedAuthor || isAdmin) && (
          <Link to="/create">Создать новость</Link>
        )}

        {isAuthenticated ? (
          <>
            <span style={{ fontSize: 14, color: "#555" }}>
              {user?.email}{" "}
              {isAdmin
                ? "(админ)"
                : isVerifiedAuthor
                ? "(автор)"
                : "(пользователь)"}
            </span>
            <button onClick={handleLogout}>Выйти</button>
          </>
        ) : (
          <Link to="/login">Войти</Link>
        )}
      </nav>
    </header>
  );
}
