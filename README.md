https://github.com/akumanowski/foodgram-project-react

# Продуктовый помощник Foodgram

На нашем сервисе вы можете публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. 
Пока это учебный проект к дипломному проекту курса «Python-разработчик» Яндекс.Практикум, но ... всё может быть 🙂 

## Техническое описание

Проект реализован на языке `Python`, с применением фреймворка `Django`. Обмен данными между бекендом и фронтендом организован по технологии REST Api c применением фреймворка `DjangoRestFramework`.
Для хранения данных используется `PostgreSQL`. 

## Особенности реализации

- Проект скомпонован в четыре Docker-контейнера;
- Образы foodgram_frontend и foodgram_backend запушены на DockerHub;
- Реализован workflow c автодеплоем на удаленный сервер и отправкой сообщения в Telegram;

## Тестирование 
- Проект доступен для тестирования по адресу <https://top-kittygram.site/>
- Тестовые данные введены от лица пользователя Василия Васильева:
  - логин: vasya@yandex.ru
  - пароль: BigBoss%17
- Добавлять такие системные данные как теги и ингредиенты может только администратор. 
  Пример загрузки ингредиентов из файла ingredients.csv реализован в разделе Ингредиенты 
  в модуле Администрирование Django как дополнительное действие. После выполнения действия,
  система показывает количество записей с некорректно заполненными данными и количество дублирующихся записей.

## Автор

 Андрей Кумановский (akuman@yandex.ru)
