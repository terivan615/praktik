
### 1. Запустите NocoDB через Docker

```bash
cd /workspace/nocodb
docker-compose up -d
```

### 2. Откройте NocoDB Dashboard

Перейдите в браузере: **http://localhost:8080**

### 3. Создайте проект

1. Нажмите **"Create Project"**
2. Название: `SupportDesk`
3. Database: SQLite (по умолчанию)
4. Нажмите **"Create"**

### 4. Импортируйте структуру БД

В NocoDB Dashboard:
1. Нажмите **"SQL"** в левом меню
2. Скопируйте содержимое файла `sample_data.sql`
3. Вставьте и выполните

ИЛИ создайте таблицы вручную согласно инструкции в `SETUP_GUIDE.md`

### 5. Получите API токен

1. Кликните на аватар (справа сверху)
2. **"API & Webhooks"** → **"Create Token"**
3. Скопируйте токен


## Структура файлов

```
nocodb/
├── docker-compose.yml      # Конфигурация Docker
├── README.md               # Общая документация
├── SETUP_GUIDE.md          # Пошаговая инструкция
├── QUICKSTART.md           # Этот файл
├── api_integration.js      # JS клиент для API
├── sample_data.sql         # Тестовые данные
└── .env.example            # Пример конфига
```

## API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/tables/Tickets/records` | Получить все заявки |
| POST | `/api/v1/tables/Tickets/records` | Создать заявку |
| PATCH | `/api/v1/tables/Tickets/records/{id}` | Обновить заявку |
| GET | `/api/v1/tables/Categories/records` | Получить категории |
| GET | `/api/v1/tables/Statuses/records` | Получить статусы |
| GET | `/api/v1/tables/Employees/records` | Получить сотрудников |


## Остановка сервера

```bash
docker-compose down
```

## Сброс данных

```bash
docker-compose down -v  # Удалит все данные!
```
