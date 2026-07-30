export const API_URL = '';

export const getUserMovies = async () => {
  const res = await fetch(`/users/me/movies?${window.location.search.substring(1)}`);
  if (!res.ok) throw new Error('Ошибка загрузки коллекции');
  return res.json();
};

export const addMovieToCollection = async (movieId: number) => {
  const res = await fetch(`/users/me/movies?movie_id=${movieId}&${window.location.search.substring(1)}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Ошибка добавления');
  return res.json();
};

export const searchMovies = async (query: string) => {
  const res = await fetch(`/movies/search?q=${query}`);
  if (!res.ok) throw new Error('Ошибка поиска');
  return res.json();
};