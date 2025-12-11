# RetailCRM Test Task

REST API-сервис на FastAPI для работы с клиентами, заказами и платежами в RetailCRM (API v5).

Проект реализует прокси-слой между клиентским приложением и RetailCRM:

- получение и фильтрация клиентов;
- создание клиента;
- получение заказов клиента;
- создание заказа;
- создание и привязка платежа к заказу.

---

## Стек

- Python 3.11
- FastAPI
- httpx
- pydantic / pydantic-settings
- Uvicorn
- Docker, docker-compose
- RetailCRM API v5

---

## Структура проекта

```text
retailcrm-test-task/
├── app/
│   ├── __init__.py
│   ├── main.py              # точка входа FastAPI
│   ├── api.py               # маршруты (эндпоинты)
│   ├── config.py            # настройки и чтение .env
│   ├── schemas.py           # Pydantic-схемы запросов/ответов
│   ├── services.py          # доменные сервисы: клиенты, заказы, платежи
│   └── retailcrm_client.py  # OOP-обёртка над httpx для RetailCRM
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Конфигурация

В корне проекта используется файл `.env`.  
В репозитории лежит пример: `.env.example`.

Пример `.env`:

```env
RETAILCRM_API_KEY=your_api_key_here
RETAILCRM_API_URL=https://yourdomain.retailcrm.ru/api/v5
APP_PORT=8000
```

---

## Запуск локально (без Docker)

### 1. Клонировать репозиторий

```bash
git clone <url_репозитория>
cd retailcrm-test-task
```

### 2. Создать и активировать виртуальное окружение

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать файл `.env`

```bash
cp .env.example .env
```

(На Windows — копировать вручную)

### 5. Запустить приложение

```bash
python -m uvicorn app.main:app --reload
```

### 6. Открыть Swagger UI

http://localhost:8000/docs

---

## Запуск через Docker / docker-compose

### 1. Сборка образов

```bash
docker compose build
```

### 2. Запуск контейнеров

```bash
docker compose up
```

Swagger будет доступен по адресу:

http://localhost:8000/docs

Контейнер использует `.env` из корня проекта.

---

## Реализованные эндпоинты

Базовый префикс: `/api`

---

### **1. Получение списка клиентов с фильтрацией**

`GET /api/customers`

Query-параметры:

- `name: str | None` — фильтр по имени  
- `email: str | None` — фильтр по email  
- `registered_from: str | None` — фильтр по дате регистрации (`createdAtFrom`)

Запрос проксируется в RetailCRM `GET /customers`.

---

### **2. Создание клиента**

`POST /api/customers`

Пример тела запроса:

```json
{
  "first_name": "Tom",
  "last_name": "Hallow",
  "email": "tom@example.com",
  "phone": "+79999999999"
}
```

Внутри:

- поля маппятся в формат RetailCRM: `firstName`, `lastName`, `phones`, `email`;
- объект сериализуется в JSON-строку;
- отправляется в RetailCRM `/customers/create` через form-data (`customer=<json>`).

---

### **3. Получение заказов клиента**

`GET /api/customers/{customer_id}/orders`

- `customer_id` — внутренний ID CRM (`id`, не `externalId`)

RetailCRM вызывается через:

`GET /orders?filter[customerId]={id}`

---

### **4. Создание заказа**

`POST /api/orders`

Пример тела:

```json
{
  "number": "ORDER-001",
  "customer_id": "43",
  "customer": null,
  "items": [
    {
      "product_name": "Test product A",
      "quantity": 1,
      "price": 1500
    }
  ]
}
```

Варианты:

- если указан `customer_id` → создается заказ для существующего клиента;
- если указан `customer` → создаётся вложенный объект клиента в заказе.

Список товаров преобразуется в формат:

```json
{
  "offer": { "name": "Test product A" },
  "quantity": 1,
  "initialPrice": 1500
}
```

`order` сериализуется в JSON и отправляется как form-data в:

`/orders/create`

---

### **5. Создание и привязка платежа к заказу**

`POST /api/orders/{order_id}/payments`

Пример запроса:

```json
{
  "amount": 2500,
  "type": "cash",
  "comment": "Test payment"
}
```

Внутри:

- собирается структура `payment`;
- сериализуется в JSON;
- отправляется в RetailCRM `/orders/payments/create` через form-data.

---

---

## Комментарий по реализации

- Проект построен по принципу разделения слоёв:  
  **клиент RetailCRM → сервисы → API-роуты**.

- Для работы с RetailCRM создан отдельный класс `RetailCRMClient`, который инкапсулирует HTTP-запросы и обеспечивает удобную сериализацию данных.

- RetailCRM API требует отправки сущностей (`customer`, `order`, `payment`) как  
  **form-data с JSON-строкой**, что стало ключевым моментом при реализации.

- При создании заказа и платежа использован **внутренний ID CRM**, а не номер заказа — это важно, чтобы API не возвращал ошибку `"Order with {id:X} does not exist"`.

- Все запросы к CRM логируются для удобства отладки.

- Проект полностью контейнеризирован: запускается одной командой `docker compose up` и использует переменные окружения из `.env`.

---

- Create by Hallow_Tommy

---
