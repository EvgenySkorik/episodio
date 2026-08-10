import {useState, useEffect, useRef} from 'react';
import {Search, Bookmark, Star, Tv, Plus} from 'lucide-react';
import {Card, CardContent} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Slider} from '@/components/ui/slider';
import {getUserMovies, searchMovies, addMovieToCollection} from '../utils/api';

interface HomeProps {
    id: string;
    openMovie: (id: number, inCollection: boolean) => void;
    vkId: number;
}

const Home: React.FC<HomeProps> = ({id, openMovie, vkId}) => {
    const [movies, setMovies] = useState<any[]>([]);
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(true);
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [showSearch, setShowSearch] = useState(false);
    const token = localStorage.getItem('jwt');
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
    const [mode, setMode] = useState<'collection' | 'popular'>('collection');
    const [popularMovies, setPopularMovies] = useState<any[]>([]);
    const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const collectionVariant: 'default' | 'outline' = mode === 'collection' ? 'default' : 'outline';
    const popularVariant: 'default' | 'outline' = mode === 'popular' ? 'default' : 'outline';

    useEffect(() => {
        if (toast) {
            const timer = setTimeout(() => setToast(null), 2000);
            return () => clearTimeout(timer);
        }
    }, [toast]);

    useEffect(() => {
        const fetchMovies = async () => {
            try {
                const data = await getUserMovies();
                setMovies(data);
            } catch (error) {
                console.error('Ошибка загрузки коллекции:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchMovies();
    }, [vkId]);

    const fetchPopularMovies = async () => {
        setLoading(true);
        try {
            const response = await fetch('/movies/popular?limit=20');
            const data = await response.json();
            setPopularMovies(data);
        } catch (error) {
            console.error('Ошибка загрузки популярных:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        if (!query.trim()) return;
        setLoading(true);
        try {
            const data = await searchMovies(query);
            setSearchResults(data);
            setShowSearch(true);
        } catch (error) {
            console.error('Ошибка поиска:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAddToCollection = async (movieId: number) => {
        try {
            await addMovieToCollection(movieId);
            const updated = await getUserMovies();
            setMovies(updated);
            setShowSearch(false);
            setQuery('');
        } catch (error) {
            console.error('Ошибка добавления:', error);
        }
    };

    const rateMovie = async (movieId: number, rating: number) => {
        try {
            const token = localStorage.getItem('jwt');
            if (!token) {
                console.error('Нет токена авторизации');
                return;
            }

            const response = await fetch(`/users/me/movies/${movieId}/rating`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({rating})  // ✅ Правильно!
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка сохранения рейтинга');
            }

            const updated = await getUserMovies();
            setMovies(updated);

        } catch (error) {
            console.error('Ошибка сохранения рейтинга:', error);
            alert('Не удалось сохранить рейтинг');
        }
    };

    const toggleTracking = async (movieId: number, currentStatus: boolean) => {
        const newStatus = !currentStatus;
        const token = localStorage.getItem('jwt');

        if (!token) {
            console.error('Нет токена авторизации');
            return;
        }

        setMovies((prev) =>
            prev.map((m) => m.id === movieId ? {...m, is_tracking: newStatus} : m)
        );

        try {
            const response = await fetch(`/users/me/movies/${movieId}/track`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({is_tracking: newStatus})
            });

            if (!response.ok) {
                throw new Error('Ошибка обновления статуса');
            }

            setToast({
                message: newStatus ? '✅ Сериал отслеживается' : '❌ Сериал не отслеживается',
                type: newStatus ? 'success' : 'error'
            });

        } catch (error) {
            setMovies((prev) =>
                prev.map((m) => m.id === movieId ? {...m, is_tracking: currentStatus} : m)
            );
            console.error('Ошибка обновления статуса:', error);
            setToast({
                message: '❌ Не удалось обновить статус',
                type: 'error'
            });
        }
    };

    if (loading) return <div className="flex items-center justify-center h-screen text-gray-400">Загрузка...</div>;

    return (
        <div className="min-h-screen bg-gray-950 text-white p-4 space-y-6">
            {/* Toast уведомления */}
            {toast && (
                <div
                    className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-lg text-white text-sm font-medium transition-all duration-300 ${
                        toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
                    }`}>
                    {toast.message}
                </div>
            )}

            {/* Заголовок */}
            <div className="flex items-center gap-3">
                <Tv className="w-8 h-8 text-red-600"/>
                <h1 className="text-2xl font-bold tracking-tight">Episodio</h1>
            </div>

            {/* Навигация: Моя коллекция / Популярное */}
            <div className="flex gap-2">
                <Button
                    variant={collectionVariant}
                    size="sm"
                    onClick={() => setMode('collection')}
                >
                    <Bookmark className="w-4 h-4 mr-1"/> Моя коллекция
                </Button>
                <Button
                    variant={popularVariant}
                    size="sm"
                    onClick={() => {
                        setMode('popular');
                        fetchPopularMovies().catch(console.error);
                    }}
                >
                    <Star className="w-4 h-4 mr-1 fill-yellow-500 text-yellow-500"/> Популярное
                </Button>
            </div>

            {/* Поиск */}
            <div className="flex gap-2">
                <Input
                    type="text"
                    placeholder="Найти фильм..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    className="flex-1"
                />
                <Button onClick={handleSearch} variant="secondary">
                    <Search className="w-4 h-4"/>
                </Button>
            </div>

            {/* Результаты поиска */}
            {showSearch && (
                <div className="space-y-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Search className="w-5 h-5"/> Результаты
                    </h2>
                    {searchResults.length === 0 ? (
                        <p className="text-gray-500">Ничего не найдено</p>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            {searchResults.map((movie: any) => (
                                <Card key={movie.id}
                                      className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors cursor-pointer"
                                      onClick={() => openMovie(movie.id, false)}>
                                    <CardContent className="p-3 space-y-2">
                                        <img src={movie.poster} alt={movie.name}
                                             className="w-full aspect-[2/3] object-cover rounded-lg"/>
                                        <h3 className="font-medium truncate">{movie.name}</h3>
                                        <p className="text-xs text-gray-400">{movie.year} •
                                            ⭐ {movie.rating_kp ?? '—'}</p>
                                        <Button size="sm" variant="outline" className="w-full" onClick={(e) => {
                                            e.stopPropagation();
                                            handleAddToCollection(movie.id).catch(console.error);
                                        }}>
                                            <Plus className="w-4 h-4"/> Сохранить
                                        </Button>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                    <Button variant="ghost" onClick={() => {
                        setShowSearch(false);
                        setQuery('');
                    }}>← Назад</Button>
                </div>
            )}

            {/* Моя коллекция */}
            {!showSearch && mode === 'collection' && (
                <div className="space-y-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Bookmark className="w-5 h-5"/> Моя коллекция
                    </h2>
                    {movies.length === 0 ? (
                        <p className="text-gray-500">Нет фильмов в коллекции</p>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            {movies.map((movie: any) => (
                                <Card key={movie.id}
                                      className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors">
                                    <CardContent className="p-3 space-y-3">
                                        <img
                                            src={movie.poster}
                                            alt={movie.name}
                                            className="w-full aspect-[2/3] object-cover rounded-lg cursor-pointer"
                                            onClick={() => openMovie(movie.id, true)}
                                        />
                                        <h3
                                            className="font-medium truncate cursor-pointer"
                                            onClick={() => openMovie(movie.id, true)}
                                        >
                                            {movie.name}
                                        </h3>

                                        <div className="space-y-1">
                                            <div className="flex items-center justify-between text-xs text-gray-400">
                                                <span>Рейтинг</span>
                                                <span className="flex items-center gap-1">
                                                <Star className="w-3 h-3 fill-yellow-500 text-yellow-500"/>
                                                    {movie.user_rating || 0}
                                            </span>
                                            </div>
                                            <Slider
                                                value={[movie.user_rating || 0]}
                                                max={10}
                                                step={0.5}
                                                onValueChange={([value]) => {
                                                    if (debounceTimer.current) {
                                                        clearTimeout(debounceTimer.current);
                                                    }
                                                    debounceTimer.current = setTimeout(() => {
                                                        rateMovie(movie.id, value).catch(console.error);
                                                    }, 500);
                                                }}
                                                className="w-full relative z-10"
                                            />
                                        </div>

                                        {movie.is_series && (
                                            <div className="flex justify-end">
                                                <Button
                                                    size="sm"
                                                    variant="ghost"
                                                    className="h-8 w-8 p-0"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        toggleTracking(movie.id, movie.is_tracking).catch(console.error);
                                                    }}
                                                >
                                                    <Tv className={`w-4 h-4 transition-colors ${
                                                        movie.is_tracking ? 'text-red-500 fill-red-500' : 'text-gray-400'
                                                    }`}/>
                                                </Button>
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Популярное */}
            {!showSearch && mode === 'popular' && (
                <div className="space-y-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Star className="w-5 h-5 fill-yellow-500 text-yellow-500"/> Популярное
                    </h2>
                    {popularMovies.length === 0 ? (
                        <p className="text-gray-500">Нет популярных фильмов</p>
                    ) : (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            {popularMovies.map((movie: any) => (
                                <Card key={movie.id}
                                      className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors">
                                    <CardContent className="p-3 space-y-2">
                                        <img
                                            src={movie.poster}
                                            alt={movie.name}
                                            className="w-full aspect-[2/3] object-cover rounded-lg cursor-pointer"
                                            onClick={() => openMovie(movie.id, false)}
                                        />
                                        <h3 className="font-medium truncate">{movie.name}</h3>
                                        <p className="text-xs text-gray-400">
                                            {movie.year} • ⭐ {movie.rating_kp ?? '—'}
                                        </p>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="w-full"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleAddToCollection(movie.id).catch(console.error);
                                            }}
                                        >
                                            <Plus className="w-4 h-4"/> Сохранить
                                        </Button>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
export default Home;
