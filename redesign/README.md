# Прототип редизайна asu-expert.ru

Статичный HTML + Tailwind CSS (вариант А: перенос в текущую CMS).

- `index.html` — главная
- `pribor-kp-91eg.html` — страница прибора КП-91ЭГ
- `assets/styles.css` — собранный Tailwind (CDN не нужен)

Открыть: просто открыть `index.html` в браузере.

Пересобрать CSS после правки классов:

```bash
npx tailwindcss@3.4.16 -c tailwind.config.js -i tailwind.input.css -o assets/styles.css --minify
```

Бриф и аудит контента: `../docs/01-brief-i-audit.md`.
Значения в таблице ТХ на странице прибора — заглушки, заменить данными из паспорта.
