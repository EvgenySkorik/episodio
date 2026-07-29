import {useState, useEffect} from 'react';
import {View} from '@vkontakte/vkui';
import vkBridge from '@vkontakte/vk-bridge';
import Home from './panels/Home';
import MovieDetail from './panels/MovieDetail';
import {DEFAULT_VIEW_PANELS} from './routes';

export const App = () => {
    const [isInCollection, setIsInCollection] = useState<boolean>(false);
    const [activePanel, setActivePanel] = useState<string>(DEFAULT_VIEW_PANELS.HOME);
    const [movieId, setMovieId] = useState<string | null>(null);
    const [vkId, setVkId] = useState<number | null>(null);
    const [refreshKey, setRefreshKey] = useState(0);

    useEffect(() => {
        const initVK = async () => {
            try {
                // Проверяем, что мы внутри VK
                if (window.location.hostname.includes('vk.com') || window.location.hostname.includes('vk')) {
                    await vkBridge.send('VKWebAppInit');
                    const user = await vkBridge.send('VKWebAppGetUserInfo');
                    setVkId(user.id);
                    console.log('Пользователь:', user);
                } else {

                    console.log('Запуск вне VK, используем заглушку');
                    setVkId(10);
                }
            } catch (error) {
                console.error('Ошибка VK Bridge:', error);
                setVkId(10);
            }
        };
        initVK();
    }, []);

    const openMovie = (id: number, inCollection: boolean) => {
        setMovieId(String(id));
        setIsInCollection(inCollection);
        setActivePanel(DEFAULT_VIEW_PANELS.MOVIE_DETAIL);
    };

    const goBack = () => {
        setActivePanel(DEFAULT_VIEW_PANELS.HOME);
    };

    const refreshHome = () => {
        setRefreshKey((prev) => prev + 1);
    };

    if (!vkId) return <div>Загрузка...</div>;

    return (
        <View id="default_view" activePanel={activePanel}>
            <Home
                key={refreshKey}
                id={DEFAULT_VIEW_PANELS.HOME}
                openMovie={openMovie}
                vkId={vkId}
            />
            <MovieDetail
                id={DEFAULT_VIEW_PANELS.MOVIE_DETAIL}
                movieId={movieId}
                goBack={goBack}
                vkId={vkId}
                isInCollection={isInCollection}
                onDelete={refreshHome}
            />
        </View>
    );
};