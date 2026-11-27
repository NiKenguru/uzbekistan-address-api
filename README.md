# Uzbekistan Address API

O‘zbekiston hududlari, tumanlari va SOATO kodlarini tanlash uchun ma’lumotnoma. Веб-форма и API для выбора региона и района с названиями на узбекской латинице, узбекской кириллице и русском.

## Ishga tushirish / Запуск

```bash
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Интерфейс доступен по адресу http://127.0.0.1:8000, документация OpenAPI — на /docs.

- `GET /api/regions` — список регионов.
- `GET /api/regions/{region_id}/districts` — районы и города региона. Для неизвестного региона возвращается 404.

В ответах есть `id`, `soato` и локализованные названия. Требуется доступ к raw.githubusercontent.com. Данные кешируются до перезапуска процесса.

## Manba / Источник

[MIMAXUZ/uzbekistan-regions-data](https://github.com/MIMAXUZ/uzbekistan-regions-data) — сторонний набор данных под GPL-3.0. Приложение загружает JSON из репозитория источника при запуске запросов.
