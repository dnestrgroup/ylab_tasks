# ylab_tasks

Запуск приложения и тестов:
> docker-compose build
> docker-compose up

Что нового сделано
- изменена версия Докер-образа на python:3.10-slim
- изменена версия Докер-образа на postgres:15.1-alpine
- написаны асинхронные тесты для ранее разработанных ендпоинтов
- тесты запускаются в отдельном контейнере вместе с приложением
- создан роутер
- ендопоинты перенесены из файла main.py во view
