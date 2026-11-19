import {useState, useEffect} from 'react';
import vkBridge from '@vkontakte/vk-bridge';
import Home from './panels/Home';
import MovieDetail from './panels/MovieDetail';
import TopMovies from './panels/TopMovies';
import Chat from './panels/Chat';
import AdminPanel from './panels/AdminPanel';
import {checkAdmin, adminLogin} from './utils/api';
import {Input} from '@/components/ui/input';
import {Button} from '@/components/ui/button';

// Dev-режим: твой VK ID для локальной проверки админки
const DEV_VK_ID = 733882553;

export const App = () => {
    const [isInCollection, setIsInCollection] = useState<boolean>(false);
    const [activePanel, setActivePanel] = useState<string>('home');
    const [movieId, setMovieId] = useState<string | null>(null);
    const [vkId, setVkId] = useState<number | null>(null);
    const [userName, setUserName] = useState<string | null>(null);
    const [refreshKey, setRefreshKey] = useState(0);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [isAdmin, setIsAdmin] = useState<boolean>(false);
    const [adminUnlocked, setAdminUnlocked] = useState<boolean>(false);
    const [showPasswordModal, setShowPasswordModal] = useState<boolean>(false);
    const [adminPassword, setAdminPassword] = useState<string>('');
    const [adminError, setAdminError] = useState<string | null>(null);

    useEffect(() => {
        const initApp = async () => {
            // Функция для получения чистых параметров (без '?')
            const getCleanParams = () => {
                const s = window.location.search;
                return s.startsWith('?') ? s.substring(1) : s;
            };

            // DEV-режим: локальная авторизация без VK
            if (import.meta.env.DEV) {
                setVkId(DEV_VK_ID);
                setUserName('Тестовый пользователь');

                const response = await fetch('/auth/vk', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({launch_params: getCleanParams()}),
                });
                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('jwt', data.access_token);
                    const adminStatus = await checkAdmin();
                    setIsAdmin(adminStatus);
                }
                setIsLoading(false);
                return;
            }

            // PROD: настоящий VK Mini App
            try {
                await vkBridge.send('VKWebAppInit');
                const user = await vkBridge.send('VKWebAppGetUserInfo');
                const userId = user.id;
                setVkId(userId);
                setUserName(`${user.first_name ?? ''} ${user.last_name ?? ''}`.trim() || `Пользователь ${userId}`);

                let token = localStorage.getItem('jwt');

                const fetchToken = async () => {
                    const response = await fetch('/auth/vk', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({launch_params: getCleanParams()}),
                    });

                    if (!response.ok) {
                        const errText = await response.text();
                        console.error("Auth failed:", response.status, errText);
                        throw new Error(`Ошибка авторизации: ${response.status}`);
                    }
                    const data = await response.json();
                    localStorage.setItem('jwt', data.access_token);
                };

                if (!token) {
                    await fetchToken();
                } else {
                    // Проверяем валидность старого токена
                    const testResponse = await fetch('/users/me', {
                        headers: {'Authorization': `Bearer ${token}`},
                    });

                    if (!testResponse.ok) {
                        localStorage.removeItem('jwt');
                        await fetchToken();
                    }
                }

                const adminStatus = await checkAdmin();
                setIsAdmin(adminStatus);
                setIsLoading(false);
            } catch (err) {
                console.error('Ошибка инициализации:', err);
                setError('Не удалось подключиться к VK. Попробуйте перезагрузить приложение.');
                setIsLoading(false);
            }
        };

        initApp();
    }, []);

    // Проверяем, админ ли — после того, как vkId установлен
    useEffect(() => {
        if (vkId === null) return;
        checkAdmin().then(setIsAdmin).catch(() => setIsAdmin(false));
    }, [vkId]);

    const openMovie = (id: number, inCollection: boolean) => {
        setMovieId(String(id));
        setIsInCollection(inCollection);
        setActivePanel('movie');
    };

    const goBack = () => setActivePanel('home');
    const goHome = () => setActivePanel('home');
    const openTop = () => setActivePanel('top');
    const openChat = () => setActivePanel('chat');
    const refreshHome = () => setRefreshKey(prev => prev + 1);

    const openAdmin = () => {
        if (adminUnlocked) {
            setActivePanel('admin');
        } else {
            setShowPasswordModal(true);
            setAdminError(null);
        }
    };

    const handleAdminLogin = async () => {
        const ok = await adminLogin(adminPassword);
        if (ok) {
            setAdminUnlocked(true);
            setShowPasswordModal(false);
            setAdminPassword('');
            setActivePanel('admin');
        } else {
            setAdminError('Неверный пароль');
        }
    };

    const closePasswordModal = () => {
        setShowPasswordModal(false);
        setAdminPassword('');
        setAdminError(null);
    };

    const passwordModal = showPasswordModal ? (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-xl p-6 w-full max-w-sm space-y-4">
                <h2 className="text-lg font-bold text-white">Вход в админку</h2>
                <Input
                    type="password"
                    placeholder="Пароль"
                    value={adminPassword}
                    onChange={(e) => setAdminPassword(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAdminLogin()}
                    autoFocus
                />
                {adminError && <p className="text-red-400 text-sm">{adminError}</p>}
                <div className="flex gap-2">
                    <Button onClick={handleAdminLogin} className="flex-1">Войти</Button>
                    <Button variant="ghost" onClick={closePasswordModal}>Отмена</Button>
                </div>
            </div>
        </div>
    ) : null;

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen bg-gray-950 text-white">
                <div className="text-center">
                    <div
                        className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <div>Загрузка...</div>
                </div>
            </div>
        );
    }

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

    if (activePanel === 'home') {
        return (
            <>
                <Home
                    key={refreshKey}
                    id="home"
                    openMovie={openMovie}
                    vkId={vkId!}
                    openTop={openTop}
                    openChat={openChat}
                    openAdmin={openAdmin}
                    isAdmin={isAdmin}
                />
                {passwordModal}
            </>
        );
    }

    if (activePanel === 'admin') {
        return (
            <AdminPanel
                id="admin"
                goHome={goHome}
            />
        );
    }

    if (activePanel === 'top') {
        return (
            <TopMovies
                id="top"
                openMovie={openMovie}
                goHome={goHome}
            />
        );
    }

    if (activePanel === 'chat') {
        return (
            <Chat
                id="chat"
                vkId={vkId!}
                userName={userName ?? undefined}
                goHome={goHome}
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