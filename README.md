# VkVideoAndCallsFinal

## Расположение заданий

- `src` - задания 10 и 20
- `scripts` - задания 30, 40, 50

Инструкици по запуску скриптов (30, 40, 50) находятся в соответствующих папках

## Чат бот (10, 20)

[Группа](https://vk.com/public214425111)

[Диалог с чат ботом](https://vk.com/im?sel=-214425111)

- Для проекта использовался python 3.9

### Запуск проекта

Рабочая папка `src`

1. Установить зависимости

```
pip install -r requirements.txt
```

2. Задать переменные окружения в фале `.env` (пример `.env.example`)
```
DEBUG=True # режим запуска (True, False)
SECRET_KEY=test # секретный ключ (необходим для работы Django)
VK_BOT_TOKEN= # токен бота
VK_TOKEN_ACCESS_TOKEN= # токен пользователя для работы VK звонков
```

3. Применить миграции

```
python manage.py migrate
```

4. Запустить бота

```
python manage.py start_vk_bot
```