import {useState, useEffect} from 'react';
import {Panel, PanelHeader, Group, Cell, Box, Button, Card} from '@vkontakte/vkui';

interface MovieDetailProps {
    id: string;
    movieId: string | null;
    goBack: () => void;
    vkId: number;
    isInCollection: boolean;
    onDelete?: () => void;
}

const MovieDetail: React.FC<MovieDetailProps> = ({id, movieId, goBack, isInCollection, onDelete}) => {
    const [movie, setMovie] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchMovie = async () => {
            try {
                const res = await fetch(`/movies/${movieId}`);
                const data = await res.json();
                setMovie(data);
            } catch (error) {
                console.error('Ошибка загрузки фильма:', error);
            } finally {
                setLoading(false);
            }
        };
        if (movieId) fetchMovie();
    }, [movieId]);

    const handleDelete = async () => {
        if (!window.confirm('Удалить фильм из коллекции?')) return;
        try {
            const res = await fetch(`/users/me/movies?movie_id=${movieId}&${window.location.search.substring(1)}`, {
                method: 'DELETE',
            });
            if (res.ok) {
                alert('Фильм удалён из коллекции');
                if (onDelete) onDelete();
                goBack();
            } else {
                alert('Ошибка удаления');
            }
        } catch (error) {
            console.error('Ошибка удаления:', error);
        }
    };

    if (loading) return <Box>Загрузка...</Box>;
    if (!movie) return <Box>Фильм не найден</Box>;

    return (
        <Panel id={id}>
            <PanelHeader before={<Button onClick={goBack} mode="tertiary">← Назад</Button>}>
                {movie.name}
            </PanelHeader>

            <Group>
                <Box style={{padding: 12}}>
                    <Card mode="outline" style={{padding: 12, marginBottom: 16}}>
                        <img
                            src={movie.poster}
                            alt={movie.name}
                            style={{width: '100%', maxWidth: 300, borderRadius: 12, display: 'block', margin: '0 auto'}}
                        />
                    </Card>

                    <Cell subtitle="Название">{movie.name}</Cell>
                    <Cell subtitle="Год">{movie.year}</Cell>
                    <Cell subtitle="Тип">{movie.is_series ? 'Сериал' : 'Фильм'}</Cell>
                    <Cell subtitle="Рейтинг">⭐ КП: {movie.rating_kp ?? '—'} • IMDb: {movie.rating_imdb ?? '—'}</Cell>
                    <Cell subtitle="Жанры">{movie.genres?.join(', ') || '—'}</Cell>
                    <Cell subtitle="Страны">{movie.countries?.join(', ') || '—'}</Cell>
                    <Cell subtitle="Описание" multiline>{movie.description || 'Нет описания'}</Cell>

                    {isInCollection && (
                        <Button
                            size="l"
                            stretched
                            mode="primary"
                            onClick={handleDelete}
                            style={{marginTop: 16}}
                        >
                            🗑 Удалить из коллекции
                        </Button>
                    )}
                </Box>
            </Group>
        </Panel>
    );
};

export default MovieDetail;