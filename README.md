# Webtest

Три редизайна сайтов производителей геофизического оборудования. [Открыть список сайтов](https://hinaface1731-blip.github.io/webtest/)

| Сайт | Файлы | GitHub Pages |
| --- | --- | --- |
| АСУ-ЭКСПЕРТ | [`site/`](site/) · [Генератор и инструкция](src/README.md) | [Открыть](https://hinaface1731-blip.github.io/webtest/site/) |
| КРУГЕО | [`krugeo/`](krugeo/) | [Открыть](https://hinaface1731-blip.github.io/webtest/krugeo/) |
| NEMFIS | [`nemfis/`](nemfis/) · [Описание дизайна](nemfis/DESIGN.md) | [Открыть](https://hinaface1731-blip.github.io/webtest/nemfis/) |

## Локальный просмотр

Запустите сервер из корня репозитория.

```sh
python3 -m http.server 8000
```

Откройте [http://localhost:8000/](http://localhost:8000/) и выберите сайт. Все три сайта можно смотреть без сборки.

## Работа с репозиторием

GitHub Pages публикует корень ветки `main`. Каждый сайт хранится в своей папке. Для изменений создавайте рабочую ветку от `main`, а при добавлении сайта внесите его в таблицу выше и в корневой `index.html`.

Исходный архив АСУ-ЭКСПЕРТ в корне и прежние ветки сохраняют историю проекта.
