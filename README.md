# 🎬 Episodio — трекер сериалов и фильмов
> **Демо:** [vk.ru/app54667446](https://vk.ru/app54667446)


**Episodio** — это VK Mini App для отслеживания любимых фильмов и сериалов на разных платформах (Netflix, YouTube, Кинопоиск и др.). Больше не забудешь, на какой серии остановился!

## Возможности

**Для пользователя**
- Поиск фильмов через API Кинопоиска
- Личная коллекция с рейтингами
- Уведомления о новых сериях (Celery + VK API)

**Технические фичи**
- Авторизация через VK (HMAC-SHA256) + JWT
- Кэширование через Redis с ретраями
- Чистая архитектура: сервисы, репозитории, DI

**Инфраструктура**
- Docker Compose (5+ контейнеров)
- HTTPS через Let's Encrypt
- Prometheus + Grafana + Hawk

**Качество кода**
- pytest, Mypy, Ruff
- Тесты (pytest), статическая типизация

## 🛠 Технологии

| **Бэкенд** | **Фронтенд** | **Инфраструктура** | **Качество кода** |
|------------|--------------|-------------------|---------------|
| FastAPI | React + TypeScript | Docker Compose | Mypy |
| PostgreSQL | Tailwind CSS + shadcn/ui | Nginx + Let's Encrypt | Ruff |
| Celery + Redis | Lucide Icons | Ubuntu VPS | pytest |
| SQLAlchemy | Vite | Prometheus + Grafana | |
| Pydantic | VK Bridge | Hawk | |
| Python 3.12 | | Celery Beat | |
## Архитектура

Проект построен по принципам **чистой архитектуры** с разделением на слои:


- **DI-контейнер** управляет зависимостями сервисов
- **Фабрики** создают сервисы для Celery-задач
- **Чистые функции** в `infrastructure/security.py` (без привязки к FastAPI)
- Все зависимости тестируемы через mock-объекты

## Быстрый старт

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

## Безопасность
- Проверка подписи VK (HMAC-SHA256 с защищённым ключом)
- JWT авторизация для всех API запросов
- HTTPS через Let's Encrypt
- Секреты в .env

## Мониторинг
- Hawk — отслеживание ошибок в реальном времени
- Prometheus + Grafana — метрики FastAPI (запросы, задержки, память)
- 
## Автор
- Evgeny Skorik
- GitHub: @EvgenySkorik
- VK: @id733882553
- tel: +79263653444
