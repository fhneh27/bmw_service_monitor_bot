# BMW Service Monitor Bot

Минимальный бот с PostgreSQL для хранения услуг, цен и избранного.

## Быстрый запуск (Docker)

1. Создайте `.env` по примеру `.env.example` и вставьте свой `TG_BOT_TOKEN`.
2. Запустите:

```bash
docker compose up --build -d
```

## Параметры БД для pgAdmin

- Host: `localhost`
- Port: `55432`
- Database: `bmw_service`
- User: `postgres`
- Password: `postgres`

## Как открыть таблицы в pgAdmin

1. `Add New Server`
2. В `Connection` укажите параметры выше
3. Откройте:
`Databases -> bmw_service -> Schemas -> public -> Tables`
4. Для данных: ПКМ по таблице -> `View/Edit Data -> All Rows`

## Ручная инициализация таблиц (если нужно)

```bash
docker compose exec web python -m app.database.init_db
```
