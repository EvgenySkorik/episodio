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

const getHeaders = (): HeadersInit => {
    const token = localStorage.getItem('jwt');
    return token ? {'Authorization': `Bearer ${token}`} : {};
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
