
# **Test task**

## **Описание**
Данный скрипт производит авторизацию по логину и паролю + CRUD на таблицу пользователей.

[comment]: <> (## **Подготовка к запуску**)

[comment]: <> (Необходимо создать бд с название 'test_db', а также пользователя `admin, admin, admin, admin, 01-01-1970, True`)

## Prepare development environment

Create virtualenv and install dependencies:

```bash
python3 -m venv `PWD`/venv
source venv/bin/activate
pip install -U pip && pip install -r requirements.txt
```
## 1. Build DB

```bash
alembic upgrade head
```

## 2. Run
```bash
python3 views.py
```

## Create migration:
```bash
alembic revision -m "revision message"
```
