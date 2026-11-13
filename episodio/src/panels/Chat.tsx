import {useCallback, useEffect, useRef, useState} from 'react';
import {ArrowLeft, MessageCircle, Send} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';

interface ChatProps {
    id: string;
    vkId: number;
    userName?: string;
    goHome: () => void;
}

interface ChatMessage {
    user_id: number;
    user_name: string;
    message: string;
    timestamp: string;
}

type WsIncoming =
    | {type: 'history'; messages: ChatMessage[]}
    | ({type?: 'message'} & ChatMessage);

/** WS-адрес: локалка — ws://localhost:8000, прод/деплой — тот же хост, что и страница. */
const getWsUrl = (): string => {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'ws://localhost:8000/ws/chat';
    }
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//${window.location.host}/ws/chat`;
};

const formatTime = (iso: string): string => {
    const date = new Date(iso);
    if (isNaN(date.getTime())) return '';
    return date.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'});
};

const Chat: React.FC<ChatProps> = ({id, vkId, userName, goHome}) => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [connected, setConnected] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const wsRef = useRef<WebSocket | null>(null);
    const bottomRef = useRef<HTMLDivElement | null>(null);
    const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

    const displayName = userName || `Пользователь ${vkId}`;

    const connect = useCallback(() => {
        let socket: WebSocket;
        try {
            socket = new WebSocket(getWsUrl());
        } catch {
            setError('Не удалось подключиться к чату');
            return;
        }
        wsRef.current = socket;

        socket.onopen = () => {
            setConnected(true);
            setError(null);
        };

        socket.onmessage = (event: MessageEvent) => {
            try {
                const data = JSON.parse(event.data as string) as WsIncoming;
                if (data.type === 'history') {
                    setMessages(data.messages);
                } else if ('message' in data) {
                    setMessages((prev) => [...prev.slice(-99), data]);
                }
            } catch (e) {
                console.error('Ошибка разбора сообщения чата:', e);
            }
        };

        socket.onclose = () => {
            setConnected(false);
            // Переподключение с небольшой задержкой
            reconnectTimer.current = setTimeout(connect, 3000);
        };

        socket.onerror = () => {
            setError('Проблема с соединением. Переподключаемся...');
        };
    }, []);

    useEffect(() => {
        connect();
        return () => {
            if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
            if (wsRef.current) {
                wsRef.current.onclose = null;
                wsRef.current.close();
            }
        };
    }, [connect]);

    // Автоскролл вниз при новых сообщениях
    useEffect(() => {
        bottomRef.current?.scrollIntoView({behavior: 'smooth'});
    }, [messages]);

    const sendMessage = () => {
        const text = input.trim();
        if (!text) return;
        const socket = wsRef.current;
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            setError('Нет соединения с сервером');
            return;
        }
        socket.send(JSON.stringify({user_id: vkId, user_name: displayName, message: text}));
        setInput('');
    };

    return (
        <div id={id} className="flex flex-col h-screen bg-gray-950 text-white">
            {/* Шапка */}
            <div className="p-4 pb-2 flex items-center gap-3">
                <Button variant="ghost" size="sm" onClick={goHome} className="-ml-2 shrink-0">
                    <ArrowLeft className="w-4 h-4 mr-1"/> Назад
                </Button>
                <MessageCircle className="w-6 h-6 text-blue-500"/>
                <h1 className="text-xl font-bold tracking-tight flex-1">Общий чат</h1>
                <span className={`text-xs ${connected ? 'text-green-500' : 'text-gray-500'}`}>
                    {connected ? '● онлайн' : '○ офлайн'}
                </span>
            </div>

            {error && (
                <div className="mx-4 rounded-lg border border-red-800 bg-red-950 px-3 py-2 text-sm text-red-300">
                    {error}
                </div>
            )}

            {/* Сообщения */}
            <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
                {messages.length === 0 && (
                    <p className="text-gray-500 text-sm text-center pt-8">
                        Пока нет сообщений — напишите первым! 👋
                    </p>
                )}
                {messages.map((msg, index) => {
                    const isMine = msg.user_id === vkId;
                    return (
                        <div key={`${msg.timestamp}-${index}`}
                             className={`max-w-[80%] rounded-xl px-3 py-2 ${
                                 isMine
                                     ? 'ml-auto bg-blue-600/80 border border-blue-500'
                                     : 'mr-auto bg-gray-900 border border-gray-800'
                             }`}>
                            <div className="flex items-baseline justify-between gap-2">
                                <span className="text-xs font-semibold text-gray-200 truncate">
                                    {msg.user_name}
                                </span>
                                <span className="text-[10px] text-gray-400 shrink-0">
                                    {formatTime(msg.timestamp)}
                                </span>
                            </div>
                            <p className="text-sm break-words whitespace-pre-wrap">{msg.message}</p>
                        </div>
                    );
                })}
                <div ref={bottomRef}/>
            </div>

            {/* Ввод */}
            <div className="p-4 border-t border-gray-800 flex gap-2">
                <Input
                    type="text"
                    placeholder="Сообщение..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                    maxLength={2000}
                    className="flex-1 bg-gray-900 border-gray-800"
                />
                <Button onClick={sendMessage} disabled={!connected || !input.trim()}>
                    <Send className="w-4 h-4"/>
                </Button>
            </div>
        </div>
    );
};

export default Chat;
