import React, { useEffect, useState } from "react";
import api from "../api/client";

function NewsListPage() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadNews() {
      try {
        setLoading(true);
        const response = await api.get("/news"); // GET /news из твоего бэка
        setNews(response.data);
      } catch (err) {
        console.error(err);
        setError("Не удалось загрузить новости");
      } finally {
        setLoading(false);
      }
    }

    loadNews();
  }, []);

  if (loading) return <p>Загружаем новости...</p>;
  if (error) return <p>{error}</p>;
  if (!news || news.length === 0) return <p>Новостей нет.</p>;

  return (
    <div>
      <h1>Новости</h1>
      <ul>
        {news.map((item) => (
          <li key={item.id}>
            <strong>{item.title}</strong>
            <div>{item.summary || item.content}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default NewsListPage;
