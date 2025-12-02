// src/pages/NewsDetailsPage.jsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";

export default function NewsDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, isAdmin, user } = useAuth();

  const [news, setNews] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [newsRes, commentsRes] = await Promise.all([
          api.get(`/news/${id}`),
          api.get(`/news/${id}/comments`), // если у тебя другой путь — потом поменяем
        ]);

        setNews(newsRes.data);
        setComments(commentsRes.data);
      } catch (e) {
        console.error("Ошибка загрузки новости", e);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id]);

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;

    try {
      const res = await api.post(`/news/${id}/comments`, {
        text: commentText, // подгони под схему на бэке
      });

      setComments((prev) => [...prev, res.data]);
      setCommentText("");
    } catch (e) {
      console.error("Ошибка добавления комментария", e);
    }
  };

  const handleDeleteNews = async () => {
    if (!window.confirm("Удалить новость?")) return;
    try {
      await api.delete(`/news/${id}`);
      navigate("/");
    } catch (e) {
      console.error("Ошибка удаления новости", e);
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm("Удалить комментарий?")) return;
    try {
      await api.delete(`/comments/${commentId}`);
      setComments((prev) => prev.filter((c) => c.id !== commentId));
    } catch (e) {
      console.error("Ошибка удаления комментария", e);
    }
  };

  if (loading) return <p>Загрузка...</p>;
  if (!news) return <p>Новость не найдена</p>;

  return (
    <div>
      <h1>{news.title}</h1>

      <div style={{ fontSize: 14, color: "#555", marginBottom: 12 }}>
        <span>Автор: {news.author?.email || "неизвестно"}</span>{" "}
        <span>
          • Дата:{" "}
          {news.published_at
            ? new Date(news.published_at).toLocaleString()
            : "—"}
        </span>
      </div>

      <div style={{ marginBottom: 20 }}>
        {/* подгони под структуру контента на бэке */}
        <pre>{JSON.stringify(news.content, null, 2)}</pre>
      </div>

      {isAdmin && (
        <button
          onClick={handleDeleteNews}
          style={{ marginBottom: 20, background: "#f55", color: "#fff" }}
        >
          Удалить новость (админ)
        </button>
      )}

      <section>
        <h2>Комментарии</h2>

        {comments.length === 0 && <p>Комментариев нет.</p>}

        <ul style={{ listStyle: "none", padding: 0 }}>
          {comments.map((c) => (
            <li
              key={c.id}
              style={{ borderBottom: "1px solid #eee", padding: "8px 0" }}
            >
              <div>
                <strong>{c.author?.email || "аноним"}</strong>
              </div>
              <div>{c.text}</div>
              {user &&
                (isAdmin || c.author_id === user.id) && ( // поле author_id подгони под свой бэк
                  <button
                    onClick={() => handleDeleteComment(c.id)}
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "#f55",
                      cursor: "pointer",
                      padding: 0,
                      marginTop: 4,
                    }}
                  >
                    удалить
                  </button>
                )}
            </li>
          ))}
        </ul>

        {isAuthenticated ? (
          <form
            onSubmit={handleAddComment}
            style={{ marginTop: 16, maxWidth: 400 }}
          >
            <textarea
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Ваш комментарий..."
              style={{ width: "100%", minHeight: 60 }}
            />
            <button type="submit" style={{ marginTop: 8 }}>
              Отправить
            </button>
          </form>
        ) : (
          <p>Только авторизованные пользователи могут оставлять комментарии.</p>
        )}
      </section>
    </div>
  );
}
