# devops_project_itmo2023

<b>Работу выполнил:</b> студент 1 курса магистратуры ИПКН ИТМО (группа M4130) Меньщиков Михаил.


<b>Базовый уровень.</b> Необходимо написать свой небольшой сервис на любом языке, он должен использовать базу данных. Добавить для него Dockerfile и docker-compose конфигурацию. Код необходимо залить на GitHub. Плюсом будет написание fullstack приложения с использованием nginx для фронтенда.

<b>Требования:</b>
* на машине, где будет запущен сервис должен быть установлен ```docker``` и должна быть доступна утилита ```docker-compose```.

<b>Запуск проекта:</b>

* выполнить команду в корневой директории ```docker-compose up -d --build app_devops```;
* выполнить команду в корневой директории ```docker-compose up -d --build nginx_devops```;
* после усшеного развёртывания сервис будет доступен по следующей ссылке ```http:\\localhost:8008```.
