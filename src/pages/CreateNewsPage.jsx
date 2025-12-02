// src/pages/CreateNewsPage.jsx
// src/pages/CreateNewsPage.jsx
import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import api from "../api/client";

export default function CreateNewsPage() {
  const { isVerifiedAuthor, isAdmin, user } = useAuth();
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [contentText, setContentText] = useState("");
  const [error, setError] = useState("");

  // доступ только авторам и админам
  if (!isVerifiedAuthor && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await api.post("/news", {
        title,
        // подгони под то, как у тебя хранится контент
        content: { text: contentText },
        author_id: user.id,
      });

      navigate(`/news/${res.data.id}`);
    } catch (e) {
      console.error(e);
      setError("Не удалось создать новость.");
    }
  };

  return (
    <div>
      <h1>Создать новость</h1>
      <form
        onSubmit={handleSubmit}
        style={{ maxWidth: 480, display: "flex", flexDirection: "column", gap: 12 }}
      >
        <label>
          Заголовок
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            style={{ width: "100%" }}
          />
        </label>

        <label>
          Контент
          <textarea
            value={contentText}
            onChange={(e) => setContentText(e.target.value)}
            required
            style={{ width: "100%", minHeight: 120 }}
          />
        </label>

        {error && <p style={{ color: "red" }}>{error}</p>}

        <button type="submit">Создать</button>
      </form>
    </div>
  );
}
