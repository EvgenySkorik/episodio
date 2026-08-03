import { useState, useEffect } from 'react';
import { Search, Bookmark, Star, Tv, Plus } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { getUserMovies, searchMovies, addMovieToCollection } from '../utils/api';

interface HomeProps {
  id: string;
  openMovie: (id: number, inCollection: boolean) => void;
  vkId: number;
}

const Home: React.FC<HomeProps> = ({ id, openMovie, vkId }) => {
  const [movies, setMovies] = useState<any[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [searchResults, setSearchResults] = useState<any[]>([]);
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
    setMovies((prev) => prev.map((m) => m.id === movieId ? { ...m, is_tracking: newStatus } : m));
    try {
      await fetch(`/users/me/movies/track?movie_id=${movieId}&is_tracking=${newStatus}&${window.location.search.substring(1)}`, {
        method: 'PUT',
      });
      const updated = await getUserMovies();
      setMovies(updated);
    } catch (error) {
      setMovies((prev) => prev.map((m) => m.id === movieId ? { ...m, is_tracking: currentStatus } : m));
      console.error('Ошибка обновления статуса:', error);
    }
  };

  if (loading) return <div className="flex items-center justify-center h-screen text-gray-400">Загрузка...</div>;

  return (
    <div className="min-h-screen bg-gray-950 text-white p-4 space-y-6">
      <div className="flex items-center gap-3">
        <Tv className="w-8 h-8 text-red-600" />
        <h1 className="text-2xl font-bold tracking-tight">Episodio</h1>
      </div>
      <div className="flex gap-2">
        <Input type="text" placeholder="Найти фильм..." value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSearch()} className="flex-1" />
        <Button onClick={handleSearch} variant="secondary"><Search className="w-4 h-4" /></Button>
      </div>
      {showSearch && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2"><Search className="w-5 h-5" /> Результаты</h2>
          {searchResults.length === 0 ? <p className="text-gray-500">Ничего не найдено</p> : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {searchResults.map((movie: any) => (
                <Card key={movie.id} className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors cursor-pointer" onClick={() => openMovie(movie.id, false)}>
                  <CardContent className="p-3 space-y-2">
                    <img src={movie.poster} alt={movie.name} className="w-full aspect-[2/3] object-cover rounded-lg" />
                    <h3 className="font-medium truncate">{movie.name}</h3>
                    <p className="text-xs text-gray-400">{movie.year} • ⭐ {movie.rating_kp ?? '—'}</p>
                    <Button size="sm" variant="outline" className="w-full" onClick={(e) => { e.stopPropagation(); handleAddToCollection(movie.id); }}><Plus className="w-4 h-4" /> Сохранить</Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
          <Button variant="ghost" onClick={() => { setShowSearch(false); setQuery(''); }}>← Назад</Button>
        </div>
      )}
      {!showSearch && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2"><Bookmark className="w-5 h-5" /> Моя коллекция</h2>
          {movies.length === 0 ? <p className="text-gray-500">Нет фильмов в коллекции</p> : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {movies.map((movie: any) => (
                <Card key={movie.id} className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-colors">
                  <CardContent className="p-3 space-y-3">
                    <img src={movie.poster} alt={movie.name} className="w-full aspect-[2/3] object-cover rounded-lg cursor-pointer" onClick={() => openMovie(movie.id, true)} />
                    <h3 className="font-medium truncate cursor-pointer" onClick={() => openMovie(movie.id, true)}>{movie.name}</h3>
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs text-gray-400">
                        <span>Рейтинг</span>
                        <span className="flex items-center gap-1"><Star className="w-3 h-3 fill-yellow-500 text-yellow-500" /> {movie.user_rating || 0}</span>
                      </div>
                      <Slider value={[movie.user_rating || 0]} max={10} step={0.5} onValueChange={([value]) => rateMovie(movie.id, value)} className="w-full" />
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant={movie.user_rating > 0 ? "secondary" : "outline"} className="flex-1"><Star className="w-3 h-3" /> {movie.user_rating || 0}</Button>
                      {movie.is_series && (
                        <Button size="sm" variant={movie.is_tracking ? "secondary" : "outline"} className="flex-1" onClick={() => toggleTracking(movie.id, movie.is_tracking)}><Tv className="w-3 h-3" /> {movie.is_tracking ? 'Отслеживаю' : 'Отслеживать'}</Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Home;
