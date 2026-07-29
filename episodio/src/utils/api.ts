export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Убираем vk_id из URL — VK сам передаст параметры!
export const getUserMovies = async () => {
  const res = await fetch(`${API_URL}/users/me/movies`);
  if (!res.ok) throw new Error('Ошибка загрузки коллекции');
  return res.json();
};

export const addMovieToCollection = async (movieId: number) => {
  const res = await fetch(`${API_URL}/users/me/movies?movie_id=${movieId}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Ошибка добавления');
  return res.json();
};

export const searchMovies = async (query: string) => {
  const res = await fetch(`${API_URL}/movies/search?q=${query}`);
  if (!res.ok) throw new Error('Ошибка поиска');
  return res.json();
};