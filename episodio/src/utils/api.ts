// Все запросы идут по относительным путям: в dev их проксирует Vite
// (см. vite.config.ts), в проде фронт и API живут на одном домене.

export interface Movie {
    id: number;
    id_kino: number;
    name: string;
    alternative_name: string | null;
    movie_type: string;
    year: number;
    description: string | null;
    short_description: string | null;
    is_series: boolean;
    rating_kp: number | null;
    rating_imdb: number | null;
    genres: string[] | null;
    countries: string[] | null;
    logo: string | null;
    poster: string | null;
    total_seasons?: number | null;
    total_episodes?: number | null;
}

export interface MovieWithUserRating extends Movie {
    user_rating: number | null;
    is_watched: boolean | null;
    is_tracking: boolean | null;
}

export interface MovieTopResponse extends Movie {
    user_rating: number | null;
    ai_description: string | null;
}

export interface TopMoviesParams {
    page?: number;
    limit?: number;
}

const getHeaders = (): Record<string, string> => {
    const token = localStorage.getItem('jwt');
    const headers: Record<string, string> = {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
};

const authJsonHeaders = (): HeadersInit => ({
    ...getHeaders(),
    'Content-Type': 'application/json',
});

const handleResponse = async (res: Response) => {
    if (res.status === 401) {
        localStorage.removeItem('jwt');
        window.location.reload(); // Перезагрузка вызовет /auth/vk заново!
    }
    if (!res.ok) {
        let detail = 'Ошибка';
        try {
            const data = await res.json();
            if (data?.detail) detail = String(data.detail);
        } catch {
            /* тело ответа может отсутствовать */
        }
        throw new Error(detail);
    }
    if (res.status === 204) return null;
    return res.json();
};

export const searchMovies = async (query: string): Promise<Movie[]> => {
    const res = await fetch(`/movies/search?q=${encodeURIComponent(query)}`);
    return handleResponse(res);
};

export const getUserMovies = async (): Promise<MovieWithUserRating[]> => {
    const res = await fetch('/users/me/movies', {headers: getHeaders()});
    return handleResponse(res);
};

export const addMovieToCollection = async (movieId: number) => {
    const res = await fetch(`/users/me/movies/${movieId}`, {
        method: 'POST',
        headers: getHeaders(),
    });
    return handleResponse(res);
};

export const deleteMovieFromCollection = async (movieId: number) => {
    const res = await fetch(`/users/me/movies/${movieId}`, {
        method: 'DELETE',
        headers: getHeaders(),
    });
    return handleResponse(res);
};

export const getMovieById = async (movieId: number | string): Promise<Movie> => {
    const res = await fetch(`/movies/${movieId}`);
    return handleResponse(res);
};

export const getPopularMovies = async (limit = 20): Promise<Movie[]> => {
    const res = await fetch(`/movies/popular?limit=${limit}`);
    return handleResponse(res);
};

export const getTopMovies = async ({
                                       page = 1,
                                       limit = 20,
                                   }: TopMoviesParams = {}): Promise<MovieTopResponse[]> => {
    const params = new URLSearchParams({page: String(page), limit: String(limit)});
    const res = await fetch(`/movies/top?${params.toString()}`);
    return handleResponse(res);
};

export const rateMovie = async (movieId: number, rating: number) => {
    const res = await fetch(`/users/me/movies/${movieId}/rating`, {
        method: 'PUT',
        headers: authJsonHeaders(),
        body: JSON.stringify({rating}),
    });
    return handleResponse(res);
};

export const toggleTracking = async (movieId: number, isTracking: boolean) => {
    const res = await fetch(`/users/me/movies/${movieId}/track`, {
        method: 'PUT',
        headers: authJsonHeaders(),
        body: JSON.stringify({is_tracking: isTracking}),
    });
    return handleResponse(res);
};

const handleAdminResponse = async (res: Response) => {
    if (res.status === 401) {
        throw new Error('UNAUTHORIZED');
    }
    if (res.status === 403) {
        throw new Error('FORBIDDEN');
    }
    if (!res.ok) {
        let detail = 'Ошибка';
        try {
            const data = await res.json();
            if (data?.detail) detail = String(data.detail);
        } catch {
            /* тело может отсутствовать */
        }
        throw new Error(detail);
    }
    if (res.status === 204) return null;
    return res.json();
};

/** Проверяет, что текущий пользователь — админ. Возвращает true/false. */
export const checkAdmin = async (): Promise<boolean> => {
    try {
        const res = await fetch('/admin/check', {headers: getHeaders()});
        await handleAdminResponse(res);
        return true;
    } catch (e) {
        if (e instanceof Error && (e.message === 'UNAUTHORIZED' || e.message === 'FORBIDDEN')) {
            return false;
        }
        console.error('checkAdmin error:', e);
        return false;
    }
};

/** Вход в админку по паролю. Возвращает true/false. */
export const adminLogin = async (password: string): Promise<boolean> => {
    try {
        const res = await fetch('/admin/login', {
            method: 'POST',
            headers: authJsonHeaders(),
            body: JSON.stringify({password}),
        });
        await handleAdminResponse(res);
        return true;
    } catch (e) {
        if (e instanceof Error && e.message === 'FORBIDDEN') {
            return false;  // неверный пароль
        }
        console.error('adminLogin error:', e);
        return false;
    }
};

/** Получить последние N строк логов. */
export const getLogsLatest = async (lines = 50): Promise<string> => {
    const res = await fetch(`/admin/logs/latest?lines=${lines}`, {
        method: 'POST',
        headers: getHeaders(),
    });
    const data = await handleAdminResponse(res);
    return data?.logs ?? '';
};

/** Баланс GigaChat: список [model, balance]. */
export const getAiBalance = async (): Promise<[string, number][]> => {
    const res = await fetch('/admin/ai-balance', {
        method: 'POST',
        headers: getHeaders(),
    });
    return handleAdminResponse(res);
};

/** Список моделей GigaChat. */
export const getAiModels = async (): Promise<string[]> => {
    const res = await fetch('/admin/ai-models', {
        method: 'POST',
        headers: getHeaders(),
    });
    return handleAdminResponse(res);
};