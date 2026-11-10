// const API_URL = '';

// ДЛЯ ЛОКАЛКИ!!!
const API_URL = 'http://localhost:8000';
// ДЛЯ ЛОКАЛКИ!!!

const getHeaders = () => {
    const token = localStorage.getItem('jwt');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
};

const handleResponse = async (res: Response) => {
    if (res.status === 401) {
        localStorage.removeItem('jwt');
        window.location.reload(); // Перезагрузка вызовет /auth/vk заново!
    }
    if (!res.ok) throw new Error('Ошибка');
    return res.json();
};

export const searchMovies = async (query: string) => {
    const res = await fetch(`${API_URL}/movies/search?q=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Ошибка поиска');
    return res.json();
};

export const getUserMovies = async () => {
    const res = await fetch(`${API_URL}/users/me/movies`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Ошибка загрузки коллекции');
    return handleResponse(res);
};

export const addMovieToCollection = async (movieId: number) => {
    const res = await fetch(`${API_URL}/users/me/movies/${movieId}`, {
        method: 'POST',
        headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Ошибка добавления');
    return handleResponse(res);
};

export interface TopMoviesParams {
    page?: number;
    limit?: number;
}

export const getTopMovies = async ({page = 1, limit = 20}: TopMoviesParams = {}) => {
    const params = new URLSearchParams({page: String(page), limit: String(limit)});
    const res = await fetch(`${API_URL}/movies/top?${params.toString()}`);
    if (!res.ok) throw new Error('Ошибка загрузки топа');
    return res.json();
};
