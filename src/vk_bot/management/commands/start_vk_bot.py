from django.core.management.base import BaseCommand

from vk_bot.core.bot import bot


class Command(BaseCommand):
    help = 'Запуск Вк бота'

    def handle(self, *args, **options):
        bot.infinity_polling()

