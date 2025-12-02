const API_URL = "http://localhost:8000"; // если у тебя другой порт — поменяй

// Получение списка новостей
export async function fetchNews() {
  const res = await fetch(`${API_URL}/news`);
  if (!res.ok) throw new Error("Ошибка загрузки новостей");
  return res.json();
}

// Получение одной новости
export async function fetchNewsById(id) {
  const res = await fetch(`${API_URL}/news/${id}`);
  if (!res.ok) throw new Error("Ошибка загрузки новости");
  return res.json();
}

// Авторизация
export async function login(email, password) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  
  if (!res.ok) throw new Error("Ошибка авторизации");
  return res.json(); // должен вернуть токен
}
