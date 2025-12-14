# Инструкция по импорту коллекции Postman

Файл коллекции (todo-app-backend.postman_collection.json) и файл переменных среды (Task API Environment.postman_environment.json) находятся в директории /docs/postman/.

## Импорт коллекции и переменных среды

1. Установите и запустите Postman.

2. В главном меню выберите "File" -> "Import...".

3. В окне импорта необходимо выбрать локально файл коллекции (todo-app-backend.postman_collection.json) и файл переменных среды (Task API Environment.postman_environment.json).

4. Коллекцию можно будет найти во вкладке "Collections" под названием "todo-app-backend".Переменные среды можно найти во вкладке "Environments", под названием "Task API Environment".

5. Переменная "base_url" будет заполнена по умолчанию. 

6. Чтобы выполнять запросы, нужно пройти авторизацию с помощью запроса "Login User". Для этого в переменных среды, в поле "email" и "password" необходимо ввести данные уже зарегистрированного пользователя.

7. Переменные "token" и "refresh_token" запишутся после успешного использования запроса "Login User". 

8. Всё готово! Можно тестировать запросы.