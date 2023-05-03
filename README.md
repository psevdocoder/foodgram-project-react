# praktikum_new_diplom
[![Docker Image CI](https://github.com/psevdocoder/foodgram-project-react/actions/workflows/foodfram_workflow.yml/badge.svg)](https://github.com/psevdocoder/foodgram-project-react/actions/workflows/foodfram_workflow.yml)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=flat&logo=django&logoColor=white&color=ff1709&labelColor=gray)](https://www.django-rest-framework.org/)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=flat&logo=gunicorn&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)

## Демонстрационный сервер с приложением
http://85.234.110.243/


## Описание
Сайт Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Установка на свой сервер
1. Склонировать репозиторий
```
git clone https://github.com/psevdocoder/foodgram-project-react.git
```
2. Перейти в директорию с docker-compose.yml
```
cd foodgram-project-react/infra/
```
3. Запустить контейнеры
```
docker-compose up -d --build
```
4. Импортировать ингредиенты внутри контейнера
```
docker-compose exec backend python manage.py load_ingredients_csv
```

## Документация к API
http://85.234.110.243/api/docs/
