import time
import traceback
from datetime import datetime

import vk_api
from vk_api import VkUpload
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType, Event

from config.logger import logger
from config.settings import VK_BOT_TOKEN, VK_TOKEN_ACCESS_TOKEN
from vk_bot.core import keyboards
from vk_bot import models

if not VK_BOT_TOKEN:
    raise ValueError('VK_TOKEN не может быть пустым')


class NextStep:
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs


class VkBot:
    OPERATORS_COUNT = 4

    def __init__(self, token):
        self.vk_bot = vk_api.VkApi(token=token)
        self.long_poll = VkLongPoll(self.vk_bot)
        self.upload = VkUpload(self.vk_bot)
        self.vk_standalone = vk_api.VkApi(token=VK_TOKEN_ACCESS_TOKEN)

        self.next_step_users: {str: NextStep} = {}

    def send_message(self, user_id: str, text, keyboard: VkKeyboard = None):
        """
        Отправка сообщения пользователю.
        """

        values = {
            'user_id': user_id,
            'message': text,
            'random_id': int(datetime.now().strftime('%y%m%d%H%S%f'))
        }

        if keyboard:
            values['keyboard'] = keyboard.get_keyboard(),

        self.vk_bot.method('messages.send', values)

    def polling(self):
        """
        Получение обновлений от Вк.
        :return:
        """
        logger.info('Вк бот запущен...')
        for event in self.long_poll.listen():
            event: Event
            try:
                self.event_handling(event)
            except:
                logger.error(traceback.format_exc())
                self.send_message(user_id=event.user_id, text='Что-то пошло не так 😞\n\n'
                                                              'Попробуйте позже или перезапустите бота командой "Старт"️\n'
                                                              'Мы уже работает над исправлением проблемы ⚙️')

    def infinity_polling(self):
        """
        Получение обновлений от Вк без остановки.
        :return:
        """
        while True:
            try:
                self.polling()
            except KeyboardInterrupt:
                exit(0)
            except Exception as e:
                time.sleep(1)
                continue

    def get_user(self, event) -> models.VkUser:
        """
        Получение или создание пользователя из базы данных.
        """
        vk_user = self.vk_bot.method("users.get", {"user_ids": event.user_id})
        fullname = vk_user[0]['first_name'] + ' ' + vk_user[0]['last_name']
        try:
            user_object = models.VkUser.objects.get(chat_id=event.user_id)
        except models.VkUser.DoesNotExist:
            user_object = models.VkUser.objects.create(chat_id=event.user_id, name=fullname)
        return user_object

    def register_next_step_by_user_id(self, user_id, callback, *args, **kwargs):
        """
        Регистрация функции, которая обработает слдующий ивент по user_id.
        """
        next_step = NextStep(callback, *args, **kwargs)
        self.next_step_users[user_id] = next_step

    def register_next_step(self, event, callback, *args, **kwargs):
        """
        Регистрация функции, которая обработает слдующий ивент.
        """
        user_id = event.user_id
        self.register_next_step_by_user_id(user_id, callback, *args, **kwargs)

    def processing_next_step(self, event, user):
        """
        Обработка запланированных ивентов
        """
        user_id = event.user_id
        if self.next_step_users.get(user_id):
            next_step = self.next_step_users[user_id]
            del self.next_step_users[user_id]
            next_step.callback(event, user, *next_step.args, **next_step.kwargs)
            return True

    def event_handling(self, event):
        """
        Обработка событий бота.
        """
        if event.to_me:
            user = self.get_user(event)
            logger.info(f'New event [user: {user}, type: {event.type}]: "{event.text}"')
            if self.processing_next_step(event, user):
                return
            elif event.type == VkEventType.MESSAGE_NEW:
                self.message_processing(event, user)

    def message_processing(self, event, user: models.VkUser):
        """
        Обработка текстовых сообщений.
        """

        event_text = event.text

        if event_text.lower() in ['начать', 'start']:
            self.send_message(user_id=user.chat_id, text=f'Чат бот для звонков',
                              keyboard=keyboards.get_main_menu_keyboard())

        elif event_text.lower() == 'основное меню':
            self.send_message(user_id=user.chat_id, text=f'Основное меню',
                              keyboard=keyboards.get_main_menu_keyboard())

        elif event_text.lower() == 'звонок':
            call_data = self.start_call()
            self.send_message(user_id=user.chat_id, text=f'Звонок создан ✅\n\n'
                                                         f'Ссылка для подключения:\n'
                                                         f'{call_data["join_link"]}')

        elif event_text.lower() == 'колл-центр':
            self.send_message(user_id=user.chat_id, text=f'Выберите роль',
                              keyboard=keyboards.get_call_center_keyboard())

        elif event_text.lower() == 'оператор':
            operator = models.Operator.objects.filter(user=None).first()
            if not operator:
                self.send_message(user_id=user.chat_id, text=f'4 оператора уже работают',
                                  keyboard=keyboards.get_call_center_keyboard())
                return

            operator.user = user
            operator.save()

            self.send_message(user_id=user.chat_id, text=f'Вы стали оператором ✅\n\n'
                                                         f'Ссылка для подключения к звонку:\n'
                                                         f'{operator.url}',
                              keyboard=keyboards.get_operator_keyboard())

        elif event_text.lower() == 'свободно':
            if not user.operator:
                self.send_not_understand_message(user)
                return

            operator = user.operator
            operator.free = True
            operator.save()

            self.send_message(user_id=user.chat_id, text=f'Ваша линия свободна. '
                                                         f'Ожидайте присоединения пользователя.',
                              keyboard=keyboards.get_operator_keyboard())


        elif event_text.lower() == 'завершить работу':
            if not user.operator:
                self.send_not_understand_message(user)
                return
            operator = user.operator
            operator.user = None
            operator.save()

            self.send_message(user_id=user.chat_id, text=f'Вы завершили свою работу',
                              keyboard=keyboards.get_main_menu_keyboard())

        elif event_text.lower() == 'посетитель':
            operator = models.Operator.objects.filter(free=True, user__isnull=False).first()
            if not operator:
                self.send_message(user_id=user.chat_id, text=f'Все операторы сейчас заняты. Попробуйте позже',
                                  keyboard=keyboards.get_call_center_keyboard())
                return

            self.send_message(user_id=user.chat_id, text=f'Ссылка для подключения:\n'
                                                         f'{operator.url}',
                              keyboard=keyboards.get_main_menu_keyboard())

            operator.free = False
            operator.save()

            self.send_message(user_id=operator.user.chat_id, text=f'К вам подключается пользователь '
                                                                  f'{user.name}. Будьте готовы 😉')

        else:
            self.send_not_understand_message(user)

    def send_in_development_message(self, user):
        self.send_message(user_id=user.chat_id, text=f'Этот раздел находится в разработке 🔧')

    def send_not_understand_message(self, user):
        self.send_message(user_id=user.chat_id, text=f'Я вас не понял 🙈\n'
                                                     f'Воспользуйтесь клавиатурой😉',
                          keyboard=keyboards.get_main_menu_keyboard())

    def start_call(self) -> dict[str, str]:
        response = self.vk_standalone.method('messages.startCall')
        return response

    def init_operators(self):
        for i in range(1, self.OPERATORS_COUNT + 1):
            operator, created = models.Operator.objects.get_or_create(number=i)
            if created:
                call_data = self.start_call()
                operator.url = call_data["join_link"]
                operator.free = True
                operator.save()


bot = VkBot(VK_BOT_TOKEN)

bot.init_operators()
