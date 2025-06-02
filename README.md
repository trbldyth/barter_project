# Проект: Платформа для обмена вещами

Данный проект - платформа для обмена вещами между пользователями на основе бартерной системы. В проекте реализованы следующие возможности: CRUD операции над объявлениями, создание предложений обмена вещами.

### Стек технологий:

Python, Django, DRF, REST API, PostgreSQL.

### Развернуть проект на удаленном сервере:

- Клонировать репозиторий:
```
git clone git@github.com:trbldyth/barter_project.git
```
Установить виртуальное окружение:
```
python -m venv venv

source venv/bin/activate
```
- Обьявить в директории с файлом .env файл:
```
SECRET_KEY              # секретный ключ Django проекта
ALLOWED_HOSTS           # список разрешенных хостов для подключения
DEBUG                   # default=TRUE
POSTGRES_DATABASE
POSTGRES_USERNAME
POSTGRES_PASSWORD
```

- Установить зависимости:
```
pip install -r requirements.txt
```
- Инициализировать базу данных PostgreSQL

- Выполнить миграции:
```
python manage.py makemigrations
```
```
python manage.py migrate
```

- Создать суперпользователя:
```
python manage.py createsuperuser
```

- Запустить локальный сервер:
```
python manage.py runserver
```

- Для запуска тестов:
```
pytest
```
pytest coverage - 93%
Автоматическая документация доступна в файле [schema.yaml](https://github.com/trbldyth/barter_project/blob/main/schema.yaml)

### Автор:
Михаил Байлаков
