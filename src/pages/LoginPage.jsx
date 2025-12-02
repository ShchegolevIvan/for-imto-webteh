// src/pages/LoginPage.jsx
import { useState } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function LoginPage() {
  const { isAuthenticated, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // если уже залогинен — не даём попасть на логин, отправляем на главную
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await login(email, password); // login берётся из AuthContext
      navigate("/");               // после успешного входа — на главную
    } catch (err) {
      console.error(err);
      setError("Не удалось войти. Проверьте логин и пароль.");
    }
  };

  return (
    <div>
      <h1>Вход</h1>
      <form onSubmit={handleSubmit} style={{ maxWidth: 320, display: "flex", flexDirection: "column", gap: 12 }}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: "100%" }}
          />
        </label>

        <label>
          Пароль
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%" }}
          />
        </label>

        {error && <p style={{ color: "red" }}>{error}</p>}

        <button type="submit">Войти</button>
      </form>
    </div>
  );
}
