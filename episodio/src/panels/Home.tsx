import {useState, useEffect} from 'react';
import {Panel, PanelHeader, Group, Cell, Button, Input, Box, Title, Card, Slider} from '@vkontakte/vkui';
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
    const [searchResults, setSearchResults] = useState([]);
    const [showSearch, setShowSearch] = useState(false);


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

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') handleSearch();
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
            await fetch(`/users/me/movies/rating?movie_id=${movieId}&rating=${rating}&${window.location.search.substring(1)}`, {
                method: 'PUT',
            });
            const updated = await getUserMovies();
            setMovies(updated);
        } catch (error) {
            console.error('Ошибка сохранения рейтинга:', error);
        }
    };

    const toggleTracking = async (movieId: number, currentStatus: boolean) => {
        const newStatus = !currentStatus;

        setMovies((prev: any[]) =>
            prev.map((m) =>
                m.id === movieId ? {...m, is_tracking: newStatus} : m
            )
        );

        try {
            await fetch(`/users/me/movies/track?movie_id=${movieId}&is_tracking=${newStatus}&${window.location.search.substring(1)}`, {
                method: 'PUT',
            });
            const updated = await getUserMovies();
            setMovies(updated);
        } catch (error) {
            setMovies((prev: any[]) =>
                prev.map((m) =>
                    m.id === movieId ? {...m, is_tracking: currentStatus} : m
                )
            );
            console.error('Ошибка обновления статуса:', error);
        }
    };

    if (loading) return <Box>Загрузка...</Box>;

    return (
        <Panel id={id}>
            <PanelHeader>🎬 Episodio</PanelHeader>

            <Group>
                <Box style={{padding: 12}}>
                    <Input
                        type="text"
                        placeholder="Найти фильм..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={handleKeyDown}
                    />
                    <Button size="l" stretched onClick={handleSearch} style={{marginTop: 8}}>
                        Найти
                    </Button>
                </Box>
            </Group>

            {showSearch ? (
                <Group>
                    <Box style={{padding: 12}}>
                        <Title level="3">🔍 Результаты</Title>
                        {searchResults.length === 0 ? (
                            <Box>Ничего не найдено</Box>
                        ) : (
                            searchResults.map((movie: any) => (
                                <Card key={movie.id} mode="outline" style={{marginBottom: 12}}>
                                    <Cell
                                        before={
                                            <img
                                                src={movie.poster}
                                                alt={movie.name}
                                                width={60}
                                                height={90}
                                                style={{objectFit: 'cover', borderRadius: 4}}
                                            />
                                        }
                                        subtitle={`${movie.year} • ${movie.is_series ? 'Сериал' : 'Фильм'} • ⭐ ${movie.rating_kp ?? '—'}`}
                                        after={
                                            <Button
                                                size="s"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleAddToCollection(movie.id);
                                                }}
                                            >
                                                Сохранить
                                            </Button>
                                        }
                                        onClick={() => openMovie(movie.id, false)}
                                    >
                                        {movie.name}
                                    </Cell>
                                </Card>
                            ))
                        )}
                        <Button
                            size="m"
                            onClick={() => {
                                setShowSearch(false);
                                setQuery('');
                            }}
                        >
                            Назад
                        </Button>
                    </Box>
                </Group>
            ) : (
                <Group>
                    <Box style={{padding: 12}}>
                        <Title level="3">📚 Моя коллекция</Title>
                        {movies.length === 0 ? (
                            <Box>Нет фильмов в коллекции</Box>
                        ) : (
                            movies.map((movie: any) => (
                                <Card key={movie.id} mode="outline" style={{marginBottom: 12}}>
                                    <Cell
                                        before={
                                            <img
                                                src={movie.poster}
                                                alt={movie.name}
                                                width={60}
                                                height={90}
                                                style={{objectFit: 'cover', borderRadius: 4}}
                                            />
                                        }
                                        subtitle={`${movie.year} • ${movie.is_series ? 'Сериал' : 'Фильм'} • ⭐ ${movie.rating_kp ?? '—'}`}
                                        onClick={() => openMovie(movie.id, true)}
                                    >
                                        {movie.name}
                                    </Cell>

                                    <Box style={{padding: '0 12px 12px 12px'}}>
                                        <Slider
                                            min={0}
                                            max={10}
                                            step={0.5}
                                            value={movie.user_rating || 0}
                                            onChange={(value: number) => {
                                                const updated = movies.map((m: any) =>
                                                    m.id === movie.id ? {...m, user_rating: value} : m
                                                );
                                                setMovies(updated);
                                                rateMovie(movie.id, value);
                                            }}
                                        />

                                        <Box style={{display: 'flex', gap: 8, marginTop: 8}}>
                                            <Button
                                                size="s"
                                                mode={movie.user_rating > 0 ? 'primary' : 'secondary'}
                                                onClick={() => rateMovie(movie.id, movie.user_rating || 0)}
                                            >
                                                ⭐ {movie.user_rating || 0} / 10
                                            </Button>

                                            {movie.is_series && (
                                                <Button
                                                    size="s"
                                                    mode={movie.is_tracking ? 'primary' : 'outline'}
                                                    onClick={() => toggleTracking(movie.id, movie.is_tracking)}
                                                >
                                                    {movie.is_tracking ? '📺 Отслеживаю' : '📺 Отслеживать'}
                                                </Button>
                                            )}
                                        </Box>
                                    </Box>
                                </Card>
                            ))
                        )}
                    </Box>
                </Group>
            )}
        </Panel>
    );
};

export default Home;