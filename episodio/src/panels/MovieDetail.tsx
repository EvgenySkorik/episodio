import { useState, useEffect } from 'react';
import { ArrowLeft, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface MovieDetailProps {
  id: string;
  movieId: string | null;
  goBack: () => void;
  vkId: number;
  isInCollection: boolean;
  onDelete?: () => void;
}

const MovieDetail: React.FC<MovieDetailProps> = ({ movieId, goBack, isInCollection, onDelete }) => {
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
    const token = localStorage.getItem('jwt');
    if (!token) {
        alert('Вы не авторизованы');
        return;
    }
    try {
        const res = await fetch(`/users/me/movies/${movieId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
        });
        if (res.ok) {
            alert('Фильм удалён из коллекции');
            if (onDelete) onDelete();
            goBack();
        } else {
            const error = await res.json();
            alert(error.detail || 'Ошибка удаления');
        }
    } catch (error) {
        console.error('Ошибка удаления:', error);
        alert('Ошибка соединения с сервером');
    }
};

  if (loading) return <div className="flex items-center justify-center h-screen bg-gray-950 text-white">Загрузка...</div>;
  if (!movie) return <div className="flex items-center justify-center h-screen bg-gray-950 text-white">Фильм не найден</div>;

  return (
    <div className="min-h-screen bg-gray-950 text-white p-4 space-y-6">
      <Button variant="ghost" onClick={goBack}><ArrowLeft className="w-4 h-4" /> Назад</Button>
      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="p-6 space-y-4">
          <img src={movie.poster} alt={movie.name} className="w-full max-w-xs mx-auto rounded-xl" />
          <h1 className="text-2xl font-bold">{movie.name}</h1>
          <div className="grid grid-cols-2 gap-2 text-sm text-gray-400">
            <div>Год: <span className="text-white">{movie.year}</span></div>
            <div>Тип: <span className="text-white">{movie.is_series ? 'Сериал' : 'Фильм'}</span></div>
            <div>Рейтинг КП: <span className="text-white">⭐ {movie.rating_kp ?? '—'}</span></div>
            <div>IMDb: <span className="text-white">⭐ {movie.rating_imdb ?? '—'}</span></div>
            <div className="col-span-2">Жанры: <span className="text-white">{movie.genres?.join(', ') || '—'}</span></div>
            <div className="col-span-2">Страны: <span className="text-white">{movie.countries?.join(', ') || '—'}</span></div>
          </div>
          <p className="text-sm text-gray-300">{movie.description || 'Нет описания'}</p>
          {isInCollection && (
            <Button className="w-full bg-red-600 hover:bg-red-500" onClick={handleDelete}><Trash2 className="w-4 h-4" /> Удалить из коллекции</Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MovieDetail;
