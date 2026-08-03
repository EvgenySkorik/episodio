import {useState, useEffect} from 'react';
import vkBridge from '@vkontakte/vk-bridge';
import Home from './panels/Home';
import MovieDetail from './panels/MovieDetail';

export const App = () => {
    const [isInCollection, setIsInCollection] = useState<boolean>(false);
    const [activePanel, setActivePanel] = useState<string>('home');
    const [movieId, setMovieId] = useState<string | null>(null);
    const [vkId, setVkId] = useState<number | null>(null);
    const [refreshKey, setRefreshKey] = useState(0);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const initApp = async () => {
            try {
                // 1. Инициализируем VK Bridge
                await vkBridge.send('VKWebAppInit');

                // 2. Получаем данные пользователя
                const user = await vkBridge.send('VKWebAppGetUserInfo');
                const userId = user.id;
                setVkId(userId);

                // 3. Получаем или обновляем JWT
                let token = localStorage.getItem('jwt');

                if (!token) {
                    // Нет токена - получаем новый
                    const response = await fetch('/auth/vk', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ vk_user_id: userId })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        localStorage.setItem('jwt', data.access_token);
                    } else {
                        throw new Error('Не удалось получить токен');
                    }
                } else {
                    // Проверяем, работает ли токен
                    const testResponse = await fetch('/users/me', {
                        headers: {'Authorization': `Bearer ${token}`}
                    });

                    if (!testResponse.ok) {
                        // Токен невалидный - получаем новый
                        localStorage.removeItem('jwt');
                        const response = await fetch('/auth/vk', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ vk_user_id: userId })
                        });

                        if (response.ok) {
                            const data = await response.json();
                            localStorage.setItem('jwt', data.access_token);
                        } else {
                            throw new Error('Не удалось обновить токен');
                        }
                    }
                }

                setIsLoading(false);

            } catch (error) {
                console.error('Ошибка инициализации:', error);
                setError('Не удалось подключиться к VK. Попробуйте перезагрузить приложение.');
                setIsLoading(false);
            }
        };

        initApp();
    }, []);

    const openMovie = (id: number, inCollection: boolean) => {
        setMovieId(String(id));
        setIsInCollection(inCollection);
        setActivePanel('movie');
    };

    const goBack = () => setActivePanel('home');
    const refreshHome = () => setRefreshKey(prev => prev + 1);

    // Загрузка
    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen bg-gray-950 text-white">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <div>Загрузка...</div>
                </div>
            </div>
        );
    }

    // Ошибка
    if (error) {
        return (
            <div className="flex items-center justify-center h-screen bg-gray-950 text-white">
                <div className="text-center max-w-md px-4">
                    <div className="text-4xl mb-4">😕</div>
                    <h2 className="text-xl font-semibold mb-2">Ошибка</h2>
                    <p className="text-gray-400 mb-4">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                    >
                        Попробовать снова
                    </button>
                </div>
            </div>
        );
    }

    // Приложение
    if (activePanel === 'home') {
        return (
            <Home
                key={refreshKey}
                id="home"
                openMovie={openMovie}
                vkId={vkId!}
            />
        );
    }

    return (
        <MovieDetail
            id="movie"
            movieId={movieId}
            goBack={goBack}
            vkId={vkId!}
            isInCollection={isInCollection}
            onDelete={refreshHome}
        />
    );
};