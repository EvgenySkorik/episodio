import {useCallback, useEffect, useState} from 'react';
import {ArrowLeft, Star, Trophy, Tv, RefreshCw} from 'lucide-react';
import {Card, CardContent} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {getTopMovies, MovieTopResponse} from '../utils/api';

interface TopMoviesProps {
    id: string;
    openMovie: (id: number, inCollection: boolean) => void;
    goHome: () => void;
}

const PAGE_SIZE = 20;
const DESCRIPTION_MAX_LENGTH = 200;

const truncate = (text: string, max = DESCRIPTION_MAX_LENGTH): string =>
    text.length > max ? `${text.slice(0, max).trimEnd()}…` : text;

/** Описание: сначала AI-описание, иначе короткое/полное (обрезанное). */
const getDescription = (movie: MovieTopResponse): string | null => {
    if (movie.ai_description) return truncate(movie.ai_description);
    if (movie.short_description) return truncate(movie.short_description);
    if (movie.description) return truncate(movie.description);
    return null;
};

const TopMovies: React.FC<TopMoviesProps> = ({id, openMovie, goHome}) => {
    const [movies, setMovies] = useState<MovieTopResponse[]>([]);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchTop = useCallback(async (pageNumber: number) => {
        setLoading(true);
        setError(null);
        try {
            const data = await getTopMovies({page: pageNumber, limit: PAGE_SIZE});
            setMovies(data);
        } catch (e) {
            console.error('Ошибка загрузки топа:', e);
            setError('Не удалось загрузить топ фильмов');
            setMovies([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchTop(page).catch(console.error);
    }, [page, fetchTop]);

    const goToPage = (newPage: number) => {
        setPage(newPage);
        window.scrollTo({top: 0});
    };

    const hasPrev = page > 1;
    const hasNext = movies.length === PAGE_SIZE;

    return (
        <div id={id} className="min-h-screen bg-gray-950 text-white p-4 space-y-6">
            {/* Кнопка "Назад" — единый стиль для всех панелей */}
            <Button variant="ghost" size="sm" onClick={goHome} className="-ml-2">
                <ArrowLeft className="w-4 h-4 mr-1"/> Назад
            </Button>

            {/* Заголовок */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Trophy className="w-8 h-8 text-yellow-500"/>
                    <h1 className="text-2xl font-bold tracking-tight">Топ фильмов</h1>
                </div>
                <Button size="sm" variant="ghost" onClick={() => fetchTop(page).catch(console.error)}
                        aria-label="Обновить">
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}/>
                </Button>
            </div>

            {/* Навигация */}
            <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={goHome}>
                    <Tv className="w-4 h-4 mr-1"/> Моя коллекция
                </Button>
            </div>

            {/* Ошибка */}
            {error && !loading && (
                <div className="rounded-lg border border-red-800 bg-red-950 p-4 flex items-center justify-between">
                    <span className="text-red-300 text-sm">{error}</span>
                    <Button size="sm" variant="secondary" onClick={() => fetchTop(page).catch(console.error)}>
                        Повторить
                    </Button>
                </div>
            )}

            {/* Список: одна карточка на строку */}
            {loading ? (
                <div className="space-y-4">
                    {Array.from({length: 6}).map((_, i) => (
                        <div key={i} className="flex gap-4 rounded-xl border border-gray-800 bg-gray-900 p-3">
                            <div className="w-[80px] h-[120px] shrink-0 rounded-lg bg-gray-800 animate-pulse"/>
                            <div className="flex-1 space-y-2 py-1">
                                <div className="h-4 w-2/3 rounded bg-gray-800 animate-pulse"/>
                                <div className="h-3 w-1/3 rounded bg-gray-800 animate-pulse"/>
                                <div className="h-3 w-full rounded bg-gray-800 animate-pulse"/>
                                <div className="h-3 w-5/6 rounded bg-gray-800 animate-pulse"/>
                            </div>
                        </div>
                    ))}
                </div>
            ) : movies.length === 0 && !error ? (
                <p className="text-gray-500">Топ пока пуст — оцените пару фильмов!</p>
            ) : (
                <div className="space-y-4">
                    {movies.map((movie, index) => {
                        const globalRank = (page - 1) * PAGE_SIZE + index + 1;
                        const description = getDescription(movie);
                        return (
                            <Card
                                key={movie.id}
                                className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors cursor-pointer"
                                onClick={() => openMovie(movie.id, false)}
                            >
                                <CardContent className="p-3 flex gap-4">
                                    {/* Постер слева */}
                                    <div className="relative shrink-0">
                                        {movie.poster ? (
                                            <img
                                                src={movie.poster}
                                                alt={movie.name}
                                                loading="lazy"
                                                className="w-[80px] h-[120px] object-cover rounded"
                                            />
                                        ) : (
                                            <div
                                                className="w-[80px] h-[120px] rounded bg-gray-800 flex items-center justify-center text-gray-500 text-[10px] text-center px-1">
                                                Нет постера
                                            </div>
                                        )}
                                        <span
                                            className="absolute top-1 left-1 bg-black/70 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-md">
                                            #{globalRank}
                                        </span>
                                    </div>

                                    {/* Инфо справа */}
                                    <div className="flex-1 min-w-0 space-y-1">
                                        <h3 className="font-medium truncate">{movie.name}</h3>
                                        <p className="text-xs text-gray-400">
                                            {movie.year} • {movie.is_series ? 'сериал' : 'фильм'}
                                        </p>
                                        <p className="text-xs flex items-center gap-1 text-gray-300">
                                            <Star className="w-3 h-3 fill-yellow-500 text-yellow-500"/>
                                            КП: {movie.rating_kp ?? '—'}
                                            <span className="text-gray-600">|</span>
                                            IMDb: {movie.rating_imdb ?? '—'}
                                        </p>
                                        {description && (
                                            <p className="text-xs text-gray-400 line-clamp-4 pt-1">
                                                {description}
                                            </p>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            )}

            {/* Пагинация */}
            {!loading && (hasPrev || hasNext) && (
                <div className="flex items-center justify-center gap-4 pt-2">
                    <Button variant="outline" size="sm" disabled={!hasPrev}
                            onClick={() => goToPage(page - 1)}>
                        Назад
                    </Button>
                    <span className="text-sm text-gray-400">Страница {page}</span>
                    <Button variant="outline" size="sm" disabled={!hasNext}
                            onClick={() => goToPage(page + 1)}>
                        Вперёд
                    </Button>
                </div>
            )}
        </div>
    );
};

export default TopMovies;
