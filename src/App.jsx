// src/App.jsx
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import NewsListPage from "./pages/NewsListPage";

// эти страницы пока-заглушки, создадим на след. шаге
import NewsDetailsPage from "./pages/NewsDetailsPage";
import LoginPage from "./pages/LoginPage";
import CreateNewsPage from "./pages/CreateNewsPage";

function App() {
  return (
    <div>
      <Navbar />
      <main style={{ padding: "0 20px" }}>
        <Routes>
          <Route path="/" element={<NewsListPage />} />
          <Route path="/news/:id" element={<NewsDetailsPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/create" element={<CreateNewsPage />} />
          <Route path="*" element={<p>Страница не найдена</p>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
