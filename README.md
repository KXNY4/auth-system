# RBAC Система Аутентификации (Django + Vue.js)

Продакшен-готовое backend приложение на Django Rest Framework с кастомной системой аутентификации и авторизации (RBAC), упакованное в Docker.

## Стек технологий

*   **Backend:** Python 3.11, Django 4.2+, DRF
*   **Database:** PostgreSQL 15 (Alpine)
*   **Auth:** JWT (simplejwt)
*   **Docs:** Swagger/OpenAPI (drf-spectacular)
*   **Frontend Demo:** Vue.js 3 + Bootstrap 5 (Single HTML file)

*   **Testing:** Pytest + Django

## Структура проекта
```
.
├── app/                 # Django приложение
│   ├── core/            # Настройки проекта
│   ├── users/           # Приложение пользователей и RBAC
│   ├── Dockerfile
│   └── manage.py
├── docker-compose.yml   # Оркестрация контейнеров
├── index.html           # Демонстрационный Frontend клиент (Устарело, используется API)
├── .env.example         # Пример переменных окружения
└── README.md
```

### RBAC Логика
Система полностью соответствует требованиям к кастомной авторизации, не полагаясь на стандартные `Groups` и `Permissions` Django. Логика проверки прав реализована в классе `CustomRBACPermission`.

**Схема данных (ER-diagram description):**

1.  **User (Пользователь):** Расширенная модель. Содержит поля ФИО (Имя, Фамилия, Отчество), Email (логин) и связь Many-to-Many с `Role`.
2.  **Role (Роль):** Сущность для группировки прав (например, "Manager", "Admin").
3.  **Resource (Ресурс):** Абстрактное представление бизнес-объекта (например, "orders", "reports"). Это позволяет создавать правила для любых сущностей системы без жесткой привязки к моделям.
4.  **PermissionRule (Правило Доступа):** Связующая таблица между `Role` и `Resource`. Определяет конкретные разрешения в виде булевых флагов:
    *   `can_create` (Create -> POST)
    *   `can_read` (Read -> GET)
    *   `can_update` (Update -> PUT/PATCH)
    *   `can_delete` (Delete -> DELETE)

**Алгоритм проверки доступа:**
1.  При запросе к API определяем **Пользователя** (из JWT токена).
2.  Определяем **Целевой Ресурс** (задается в атрибуте `required_resource` во View классе).
3.  Определяем **Требуемое Действие** на основе HTTP-метода (GET -> read, POST -> create и т.д.).
4.  Ищем среди ролей пользователя такую роль, которая имеет правило (`PermissionRule`) для данного ресурса с установленным флагом требуемого действия (`True`).
5.  Если совпадение найдено -> **Доступ разрешен (200)**. Иначе -> **Запрещен (403)**.

Если пользователь не аутентифицирован -> **401 Unauthorized**.

## Установка и запуск

### Предварительные требования
*   Docker и Docker Compose

### Быстрый старт

1.  **Клонирование репозитория (если применимо)**

2.  **Настройка окружения**
    Создайте файл `.env` на основе примера:
    ```bash
    cp .env.example .env
    ```
    *При необходимости отредактируйте `.env`, задав свои пароли и ключи.*

3.  **Запуск через Docker**
    ```bash
    docker-compose up --build
    ```
    Первый запуск займет некоторое время на сборку образа и инициализацию базы данных.
    Контейнер `web` автоматически:
    *   Применит миграции.
    *   Соберет статику.
    *   **Создаст тестовые данные** (Админ, Менеджер, Заказы, Отчеты) через скрипт `init_data`.

4.  **Доступ к приложению**
    *   **API Root:** [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)
    *   **Swagger UI (Документация):** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
    *   **Админка Django:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

### Учетные данные (создаются автоматически)

*   **Superuser Admin:**
    *   Email: `admin@example.com`
    *   Password: `adminpass`
*   **Менеджер (с правами на Заказы и Отчеты):**
    *   Email: `manager@example.com`
    *   Password: `managerpass`

## Тестирование

Проект использует `pytest` для тестирования.
Для запуска тестов в контейнере выполните:

```bash
docker-compose exec web pytest
```
Мягкое удаление (Soft Delete) переводит пользователя в статус `is_active=False`, запрещая вход, но сохраняя данные.

## Инструкция по запуску

### 1. Переменные окружения
Создайте файл `.env` на основе примера (хотя `docker-compose.yml` уже содержит дефолтные значения для демонстрации):
```bash
cp .env.example .env
```

### 2. Запуск в Docker
Соберите и запустите контейнеры. При первом запуске автоматически выполняются миграции и создание начальных данных (команда `init_data`).

```bash
docker-compose up --build
```

Ожидайте сообщения в логах `web` контейнера: `Инициализация данных завершена успешно!`.

### 3. Использование Frontend клиента
Откройте файл `index.html` в браузере. Так как в `settings.py` включен `CORS_ALLOW_ALL_ORIGINS = True`, вы можете открывать файл прямо с диска (file://) или через Live Server.

**Тестовые данные (создаются автоматически):**

*   **Email:** `manager@example.com`
*   **Пароль:** `managerpass`
*   **Роль:** Manager
*   **Доступ:** Может читать (`GET`) и создавать (`POST`) `orders`.
*   **Нет доступа:** Не может читать `reports`.

**Суперпользователь:**
*   **Email:** `admin@example.com`
*   **Пароль:** `adminpass`

### 4. API Документация (Swagger)
После запуска backend доступен по адресу `http://localhost:8000`.
Документация Swagger UI:
[http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

## API Эндпоинты

*   `POST /api/v1/auth/register/` - Регистрация
*   `POST /api/v1/auth/login/` - Вход (получение JWT)
*   `POST /api/v1/auth/logout/` - Выход (Blacklist refresh token)
*   `GET /api/v1/profile/` - Профиль текущего пользователя
*   `GET /api/v1/resources/orders/` - Пример ресурса (Orders)
*   `GET /api/v1/resources/reports/` - Пример ресурса (Reports)

## Разработка
Для создания новых пользователей с правами админа:
```bash
docker-compose exec web python manage.py createsuperuser
```
Для ручного запуска инициализации:
```bash
docker-compose exec web python manage.py init_data
```
