# Django + Stripe (тестовое задание)

Сервис на **Django 4.2** и **Stripe Checkout Session**: оплата одного `Item` или корзины `Order` (несколько позиций), скидка (Stripe Coupon) и налог (Stripe Tax Rate) передаются в Checkout и отображаются в форме Stripe. У товара есть поле **валюты** (`usd` / `eur`); для каждой валюты задаётся **своя пара** тестовых ключей Stripe (как правило, два тестовых аккаунта или два набора ключей из разных режимов).

## Быстрый старт (локально)

Требования: **Python 3.9+** (для Docker образ использует 3.12).

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Заполните STRIPE_* ключи в .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Откройте в браузере:

- Сводка ссылок: `http://127.0.0.1:8000/`
- Админка: `http://127.0.0.1:8000/admin/`
- Страница товара (пример): `http://127.0.0.1:8000/item/1/`

### Переменные окружения

См. файл [.env.example](.env.example). Основные:

| Переменная | Назначение |
|------------|------------|
| `DJANGO_SECRET_KEY` | Секретный ключ Django |
| `DJANGO_DEBUG` | `true` / `false` |
| `DJANGO_ALLOWED_HOSTS` | Список хостов через запятую |
| `PUBLIC_BASE_URL` | Публичный URL сайта (со схемой), для `success_url` / `cancel_url` в Stripe |
| `STRIPE_SECRET_KEY_USD`, `STRIPE_PUBLISHABLE_KEY_USD` | Ключи для товаров/заказов в **USD** |
| `STRIPE_SECRET_KEY_EUR`, `STRIPE_PUBLISHABLE_KEY_EUR` | Ключи для товаров/заказов в **EUR** |
| `SQLITE_PATH` | Необязательно: путь к файлу SQLite (в Docker задаётся автоматически) |

## API

| Метод | URL | Описание |
|--------|-----|----------|
| GET | `/buy/<id>/` | Создаёт `stripe.checkout.Session` для одного `Item`, в ответе JSON: `{"session_id": "cs_..."}` |
| GET | `/item/<id>/` | HTML: данные товара и кнопка **Buy** → запрос `/buy/<id>/` → `stripe.redirectToCheckout({ sessionId })` |
| GET | `/buy/order/<id>/` | Checkout Session для **Order** (сумма по всем строкам) |
| GET | `/order/<id>/` | HTML для оплаты заказа |

Пример из задания:

```bash
curl -s http://127.0.0.1:8000/item/1
```

## Модели (Django Admin)

В админке доступны: **Item**, **Order** (+ inline **OrderLine**), **Discount**, **Tax**.

- **Order**: несколько товаров через строки заказа; все товары в одном заказе должны быть в **одной валюте** (иначе API вернёт ошибку).
- **Discount**: поле `stripe_coupon_id` — ID купона в Stripe (Products → Coupons), в **том же** Stripe-аккаунте, что и секретный ключ валюты заказа.
- **Tax**: поле `stripe_tax_rate_id` — ID налоговой ставки (Products → Tax rates); передаётся в Checkout как `tax_rates` на каждую позицию — сумма и разбивка видны в форме оплаты Stripe.

## Stripe: две валюты и две пары ключей

Для EUR и USD используются разные пары `sk_test_…` / `pk_test_…`. Ключ выбирается по полю `Item.currency` (для заказа — по валюте позиций). Купоны и налоговые ставки нужно создать в **каждом** используемом тестовом аккаунте Stripe отдельно, если вы реально используете два аккаунта.

## Docker

```bash
cp .env.example .env
# Заполните .env
docker compose up --build
```

Приложение: `http://127.0.0.1:8000/`. База SQLite хранится в volume `sqlite_data` (`/app/data/db.sqlite3` в контейнере).

## Публикация для проверки (бесплатно: Render.com)

Задание просит **живую ссылку** и **доступ в админку**. Это можно сделать **бесплатно** на [Render](https://render.com): тариф **Free** для одного Web Service (есть ограничения: сервис «засыпает» без запросов ~15 мин, первый запрос после сна дольше; файловая система эфемерная — при **новом деплое** SQLite может обнулиться, суперпользователя и товары тогда создают заново в админке).

### 1. Код на GitHub

Репозиторий **без** файла `.env` (он в `.gitignore`). Все секреты задаются только в панели Render.

### 2. Создать Web Service на Render

1. [dashboard.render.com](https://dashboard.render.com) → **New +** → **Web Service**.
2. Подключите репозиторий с этим проектом.
3. Выберите окружение: **Docker** (Render сам найдёт `Dockerfile` в корне). Либо при использовании Blueprint: **New +** → **Blueprint** → указать `render.yaml` из репозитория.
4. Имя сервиса (например `yandex-stripe-demo`) → Render выдаст URL вида `https://yandex-stripe-demo.onrender.com`.

### 3. Переменные окружения (Environment)

В сервисе → **Environment** → добавьте (значения свои):

| Key | Пример значения |
|-----|------------------|
| `DJANGO_SECRET_KEY` | Длинная случайная строка (не как в `.env.example`) |
| `DJANGO_DEBUG` | `false` |
| `DJANGO_ALLOWED_HOSTS` | `yandex-stripe-demo.onrender.com` (подставьте **ваш** хост без `https://`) |
| `PUBLIC_BASE_URL` | `https://yandex-stripe-demo.onrender.com` (со схемой, без слэша в конце) |
| `STRIPE_SECRET_KEY_USD` | `sk_test_...` |
| `STRIPE_PUBLISHABLE_KEY_USD` | `pk_test_...` |
| `STRIPE_SECRET_KEY_EUR` | те же или второй аккаунт Stripe |
| `STRIPE_PUBLISHABLE_KEY_EUR` | `pk_test_...` |
| `SQLITE_PATH` | `/app/data/db.sqlite3` |

**Save** → Render пересоберёт и запустит контейнер. Миграции выполняются при старте (см. `Dockerfile`).

### 4. Суперпользователь для админки

После успешного деплоя: в сервисе откройте **Shell** (или **SSH**, если доступно в вашем плане) и выполните:

```bash
python manage.py createsuperuser
```

Укажите логин и пароль для проверяющих (в письме работодателю лучше написать: пароль передаёте **отдельным каналом**, не в публичном README).

### 5. Что отправить в ответ на тестовое

Пример текста:

- Сайт: `https://<ваш-сервис>.onrender.com/`
- Админка: `https://<ваш-сервис>.onrender.com/admin/`
- Логин: `...` (пароль — в личном сообщении / почте)

### Другие бесплатные варианты

- [Fly.io](https://fly.io) — есть бесплатный лимит, чуть сложнее первый деплой.
- [Railway](https://railway.app) — часто дают пробные кредиты; постоянно «ноль рублей» не гарантируется.

Для продакшена обычно переводят БД с SQLite на **PostgreSQL** (у Render есть бесплатный инстанс с ограничениями); для демонстрации тестового задания SQLite на Render обычно достаточно.

## Что не входит в репозиторий

- **Payment Intent** вместо Checkout Session в задании указан как отдельный бонус; текущая реализация следует базовому сценарию со **Stripe Checkout Session**, как в формулировке ТЗ.

## Структура проекта

- `stripe_demo/` — настройки Django, URL корня.
- `items/` — модели, представления, интеграция со Stripe (`stripe_utils.py`).
- `templates/items/` — HTML для `/item/` и `/order/`.

Лицензия: учебный код для тестового задания.
