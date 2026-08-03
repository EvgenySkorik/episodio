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

    useEffect(() => {
        const initVK = async () => {
            // Фолбэк для браузера
            const setFallbackVkId = () => {
                const urlParams = new URLSearchParams(window.location.search);
                const vkUserId = urlParams.get('vk_user_id');
                setVkId(vkUserId ? Number(vkUserId) : 10);
            };

            try {
                // Таймаут 2 секунды для VK Bridge (локально)
                const timeout = new Promise((_, reject) =>
                    setTimeout(() => reject(new Error('VK Bridge timeout')), 2000)
                );
                await Promise.race([vkBridge.send('VKWebAppInit'), timeout]);
                const user = await vkBridge.send('VKWebAppGetUserInfo');
                setVkId(user.id);
            } catch (error) {
                console.log('VK Bridge not available, using fallback');
                setFallbackVkId();
            }
        };
        initVK();
    }, []);

    const openMovie = (id: number, inCollection: boolean) => {
        setMovieId(String(id));
        setIsInCollection(inCollection);
        setActivePanel('movie');
    };

    const goBack = () => setActivePanel('home');
    const refreshHome = () => setRefreshKey(prev => prev + 1);

    if (!vkId) return <div className="flex items-center justify-center h-screen bg-gray-950 text-white">Загрузка...</div>;

    if (activePanel === 'home') {
        return (
            <Home
                key={refreshKey}
                id="home"
                openMovie={openMovie}
                vkId={vkId}
            />
        );
    }

    return (
        <MovieDetail
            id="movie"
            movieId={movieId}
            goBack={goBack}
            vkId={vkId}
            isInCollection={isInCollection}
            onDelete={refreshHome}
        />
    );
};