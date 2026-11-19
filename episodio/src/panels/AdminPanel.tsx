import {useState} from 'react';
import {ArrowLeft, FileText, Wallet, Cpu} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {Card, CardContent} from '@/components/ui/card';
import {getLogsLatest, getAiBalance, getAiModels} from '../utils/api';

interface AdminPanelProps {
    id: string;
    goHome: () => void;
}

type Tab = 'logs' | 'balance' | 'models';

const getVariant = (tab: Tab, activeTab: Tab | null): 'default' | 'outline' =>
    activeTab === tab ? 'default' : 'outline';

const AdminPanel: React.FC<AdminPanelProps> = ({id, goHome}) => {
    const [activeTab, setActiveTab] = useState<Tab | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Результаты
    const [logs, setLogs] = useState<string>('');
    const [balance, setBalance] = useState<[string, number][]>([]);
    const [models, setModels] = useState<string[]>([]);

    const run = async (tab: Tab) => {
        setActiveTab(tab);
        setLoading(true);
        setError(null);
        try {
            if (tab === 'logs') {
                const data = await getLogsLatest(100);
                setLogs(data);
            } else if (tab === 'balance') {
                const data = await getAiBalance();
                setBalance(data);
            } else if (tab === 'models') {
                const data = await getAiModels();
                setModels(data);
            }
        } catch (e) {
            console.error('Admin request error:', e);
            setError(e instanceof Error ? e.message : 'Ошибка запроса');
        } finally {
            setLoading(false);
        }
    };

    const renderResult = () => {
        if (loading) {
            return (
                <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"/>
                </div>
            );
        }
        if (error) {
            return (
                <div className="rounded-lg border border-red-800 bg-red-950 px-4 py-3 text-sm text-red-300">
                    {error}
                </div>
            );
        }
        if (!activeTab) {
            return <p className="text-gray-500 text-sm">Выбери действие выше</p>;
        }
        if (activeTab === 'logs') {
            return (
                <pre className="whitespace-pre-wrap break-words text-xs text-gray-300 max-h-[60vh] overflow-y-auto">
                    {logs || 'Логи пусты'}
                </pre>
            );
        }
        if (activeTab === 'balance') {
            if (balance.length === 0) {
                return <p className="text-gray-500 text-sm">Нет данных</p>;
            }
            return (
                <div className="space-y-2">
                    {balance.map(([model, value]) => (
                        <div key={model} className="flex justify-between border-b border-gray-800 pb-2">
                            <span className="text-gray-300">{model}</span>
                            <span className="text-white font-medium">
                                {value.toLocaleString('ru-RU')}
                            </span>
                        </div>
                    ))}
                </div>
            );
        }
        if (activeTab === 'models') {
            if (models.length === 0) {
                return <p className="text-gray-500 text-sm">Нет моделей</p>;
            }
            return (
                <ul className="space-y-2">
                    {models.map((m) => (
                        <li key={m} className="text-gray-300 border-b border-gray-800 pb-2">
                            {m}
                        </li>
                    ))}
                </ul>
            );
        }
        return null;
    };

    return (
        <div id={id} className="min-h-screen bg-gray-950 text-white p-4 space-y-6">
            <Button variant="ghost" size="sm" onClick={goHome} className="-ml-2">
                <ArrowLeft className="w-4 h-4 mr-1"/> Назад
            </Button>

            <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold tracking-tight">Админка</h1>
            </div>

            {/* Кнопки действий */}
            <div className="flex flex-wrap gap-2">
                <Button
                    variant={getVariant('logs', activeTab)}
                    size="sm"
                    onClick={() => run('logs')}
                    disabled={loading}
                >
                    <FileText className="w-4 h-4 mr-1"/> Логи
                </Button>
                <Button
                    variant={getVariant('balance', activeTab)}
                    size="sm"
                    onClick={() => run('balance')}
                    disabled={loading}
                >
                    <Wallet className="w-4 h-4 mr-1"/> Баланс AI
                </Button>
                <Button
                    variant={getVariant('models', activeTab)}
                    size="sm"
                    onClick={() => run('models')}
                    disabled={loading}
                >
                    <Cpu className="w-4 h-4 mr-1"/> Модели AI
                </Button>
            </div>

            {/* Результат */}
            <Card className="bg-gray-900 border-gray-800">
                <CardContent className="p-4">
                    {renderResult()}
                </CardContent>
            </Card>
        </div>
    );
};

export default AdminPanel;