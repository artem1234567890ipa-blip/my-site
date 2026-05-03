# Conference Project

Проект конференции — сайт + Telegram-бот для регистрации участников.

## Стек

- **Telegram Bot** — aiogram (Python)
- **База данных** — Supabase (PostgreSQL облако)
- **Контейнеризация** — Docker + docker-compose
- **Деплой** — Coolify + GitHub автодеплой
- **Прокси** — Traefik

## Структура проекта

```
conference/
├── CLAUDE.md
├── .env.example        — шаблон переменных окружения
├── .gitignore
├── docker-compose.yml  — запуск всех сервисов
├── bot/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py         — точка входа бота
└── landing/
    ├── Dockerfile
    └── index.html      — лендинг конференции
```

## Правила работы

- NEVER read, edit, write .env files
- Коммит после каждого завершённого этапа
- Использовать параллельные сессии для независимых задач
- Для деплоя использовать `expose` вместо `ports` в docker-compose
- Проверять локально: `docker compose up --build`

## Переменные окружения

Все секреты в `.env` (не в git). Шаблон в `.env.example`.

## Этапы реализации

- [ ] Настроить Supabase — создать таблицы
- [ ] Создать Telegram-бота через @BotFather
- [ ] Реализовать регистрацию через бот
- [ ] Создать лендинг конференции
- [ ] Dockerfile + docker-compose
- [ ] Деплой на Coolify
