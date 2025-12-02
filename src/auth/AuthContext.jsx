// src/auth/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  // подтягиваем юзера из localStorage при загрузке
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const login = async (email, password) => {
    // ⚠️ тут формат подгони под свой бэкенд, но пока оставим так
    const res = await api.post("/auth/login", { email, password });
    const token = res.data.access_token;

    localStorage.setItem("access_token", token);

    // если бэк возвращает user вместе с токеном — используем его
    if (res.data.user) {
      localStorage.setItem("user", JSON.stringify(res.data.user));
      setUser(res.data.user);
    } else {
      // если нет — дергаем эндпоинт "кто я"
      const me = await api.get("/auth/me");
      localStorage.setItem("user", JSON.stringify(me.data));
      setUser(me.data);
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setUser(null);
  };

  const isAuthenticated = !!user;
  const isVerifiedAuthor = !!user?.is_verified_author; // флаг из ЛР3
  const isAdmin = user?.role === "admin"; // роль админа, если есть

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated, isVerifiedAuthor, isAdmin, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
