<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=180&section=header&text=EPISODIO&fontSize=60&fontColor=fff&animation=twinkling&fontAlignY=35&desc=Трекер%20сериалов%20и%20фильмов&descAlignY=60&descSize=18" width="100%"/>

<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&pause=1000&color=E50914&center=true&vCenter=true&width=600&lines=FastAPI+%7C+React+%7C+PostgreSQL;AI-%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D1%8F+%D1%81+%D1%8E%D0%BC%D0%BE%D1%80%D0%BE%D0%BC+%D0%BE%D1%82+GigaChat;VK+Mini+App+%7C+Celery+%7C+Redis;%D0%A7%D0%B8%D1%81%D1%82%D0%B0%D1%8F+%D0%B0%D1%80%D1%85%D0%B8%D1%82%D0%B5%D0%BA%D1%82%D1%83%D1%80%D0%B0+%D0%B8+%D1%82%D0%B5%D1%81%D1%82%D1%8B" alt="Typing SVG" />
</a>

<br/>

<img src="https://komarev.com/ghpvc/?username=EvgenySkorik&label=Profile%20views&color=E50914&style=flat-square" alt="Profile views" />

</div>

**Episodio** — это VK Mini App для отслеживания любимых фильмов и сериалов на разных платформах (Netflix, YouTube, Кинопоиск и др.). Больше не забудешь, на какой серии остановился!

## Возможности

**Для пользователя**
- Поиск фильмов через API Кинопоиска
- Личная коллекция с рейтингами и статусом просмотра
- Отслеживание сериалов и уведомления о новых сериях (Celery + VK API)
- **AI-описания фильмов с сарказмом** (GigaChat / Sber AI)
- **Топ фильмов** по оценкам пользователей
- **Общий чат** в реальном времени (WebSocket + Redis)

**Технические фичи**
- Авторизация VK Mini App с проверкой подписи (HMAC-SHA256) + JWT
- **Админ-панель** с проверкой по VK ID whitelist + паролю
- Кэширование через Redis с ретраями
- Чистая архитектура: сервисы, репозитории, DI-контейнер
- Celery Beat: ежедневная генерация AI-описаний и проверка новых серий

**Инфраструктура**
- Docker Compose (5+ контейнеров)
- HTTPS через Let's Encrypt
- Nginx с rate limiting и CSP для VK
- Prometheus + Grafana + Hawk

**Качество кода**
- pytest, Mypy, Ruff

## 🛠 Технологии

| **Бэкенд** | **Фронтенд** | **Инфраструктура** | **Качество кода** |
|------------|--------------|-------------------|---------------|
| FastAPI | React + TypeScript | Docker Compose | Mypy |
| PostgreSQL | Tailwind CSS + shadcn/ui | Nginx + Let's Encrypt | Ruff |
| Celery + Redis | Lucide Icons | Ubuntu VPS | pytest |
| SQLAlchemy | Vite | Prometheus + Grafana | |
| Pydantic | VK Bridge | Hawk | |
| Python 3.12 | | Celery Beat | |
| GigaChat SDK | | | |

## Архитектура

Проект построен по принципам **чистой архитектуры** с разделением на слои:

- **DI-контейнер** управляет зависимостями сервисов
- **Кэширование** через Redis (Cache-Aside, TTL, ретраи)
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
│   ├── clients/          # VK API, Kinopoisk API, GigaChat
│   ├── core/             # Конфигурация, исключения
│   ├── db/               # Модели, сессия БД
│   ├── infrastructure/   # Celery, HTTP, Redis, безопасность, WebSocket
│   ├── repositories/     # Работа с БД
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика (Movie, User, AI, Notification)
│   └── tasks/            # Celery задачи
├── episodio/             # Фронтенд
│   └── src/
│       ├── components/   # shadcn/ui компоненты
│       ├── panels/       # Страницы (Home, MovieDetail, TopMovies, Chat, AdminPanel)
│       └── utils/        # API клиент
├── alembic/              # Миграции БД
├── tests/                # Тесты
├── docker-compose.yaml
├── Dockerfile
└── README.md
```

## Безопасность
- Проверка подписи VK (HMAC-SHA256 с защищённым ключом)
- JWT авторизация для всех API запросов
- Админ-доступ по whitelist VK ID + паролю
- HTTPS через Let's Encrypt
- CSP frame-ancestors для VK Mini App
- Секреты в .env

## Мониторинг
- Hawk — отслеживание ошибок в реальном времени
- Prometheus + Grafana — метрики FastAPI (запросы, задержки, память)
- Celery Beat — ежедневные задачи
- 
## Автор
- Evgeny Skorik
- GitHub: @EvgenySkorik
- VK: @id733882553
- tel: +79263653444
