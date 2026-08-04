# 🎬 Episodio — трекер сериалов и фильмов

**Episodio** — это VK Mini App для отслеживания любимых фильмов и сериалов на разных платформах (Netflix, YouTube, Кинопоиск и др.). Больше не забудешь, на какой серии остановился!

## ✨ Возможности

- 🎥 **Поиск фильмов** через API Кинопоиска
- 📚 **Личная коллекция** с рейтингами и статусом просмотра
- 📺 **Отслеживание сериалов** и уведомления о новых сериях (Celery + VK API)
- 🔐 **Авторизация через VK** с проверкой подписи и JWT
- 🎨 **Тёмный Netflix-стиль** на React + Tailwind CSS + shadcn/ui
- 🐳 **Docker Compose** для продакшен-деплоя (5+ контейнеров)
- 📊 **Мониторинг ошибок** через Hawk + **метрики** Prometheus + Grafana
- 🏗️ **Чёткая архитектура**: сервисы, репозитории, DI-контейнер
- ✅ **Unit-тесты** на pytest

## 🛠 Технологии

| Бэкенд | Фронтенд | Инфраструктура |
|--------|----------|----------------|
| FastAPI | React + TypeScript | Docker Compose |
| PostgreSQL | Tailwind CSS + shadcn/ui | Nginx + Let's Encrypt |
| Celery + Redis | Lucide Icons | Ubuntu VPS |
| SQLAlchemy | Vite | Prometheus + Grafana |
| Pydantic | VK Bridge | Hawk |

## 🏗️ Архитектура

Проект построен по принципам **чистой архитектуры** с разделением на слои:


- **DI-контейнер** управляет зависимостями сервисов
- **Фабрики** создают сервисы для Celery-задач
- **Чистые функции** в `infrastructure/security.py` (без привязки к FastAPI)
- Все зависимости тестируемы через mock-объекты

## 🚀 Быстрый старт

### Локальная разработка
```bash
# Бэкенд
cp env.example .env  # заполни .env
docker-compose up -d
uv run uvicorn app.main:app --reload
```


```
# Фронтенд
cd episodio
npm install
npm start
```
```
├── app/                  # Бэкенд
│   ├── api/              # Роутеры, зависимости
│   ├── clients/          # VK API, Kinopoisk API
│   ├── core/             # Конфигурация, исключения
│   ├── db/               # Модели, сессия БД
│   ├── infrastructure/   # Celery, HTTP клиент, безопасность
│   ├── repositories/     # Работа с БД
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика
│   └── tasks/            # Celery задачи
├── episodio/             # Фронтенд
│   └── src/
│       ├── components/   # shadcn/ui компоненты
│       ├── panels/       # Страницы (Home, MovieDetail)
│       └── utils/        # API клиент
├── tests/                # Тесты
├── docker-compose.yaml
├── Dockerfile
└── README.md
```

## 🔐 Безопасность
- Проверка подписи VK (HMAC-SHA256 с защищённым ключом)
- JWT авторизация для всех API запросов
- HTTPS через Let's Encrypt
- Секреты в .env

## 📊 Мониторинг
- Hawk — отслеживание ошибок в реальном времени
- Prometheus + Grafana — метрики FastAPI (запросы, задержки, память)
- 
## 🎯 Автор
- Evgeny Skorik
- GitHub: @EvgenySkorik
- VK: @id733882553
- tel: +79263653444