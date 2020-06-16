from vk.exceptions import VkAPIError
from random import randint
from requests import *
import json
import vk

# Указываем ключи доступа, id группы и версию API
VK_API_ACCESS_TOKEN = 'abbd9e53577540e899a6f21a16ae3f1750dd256a69094895db2e9f5723b72d01ac03f5534338266a46e17'
VK_API_VERSION = '5.95'
GROUP_ID = 196362480
INT_MIN = -2147483648
INT_MAX = 2147483647


# Проверяем на целое число
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# Выводим персональную информацию
def person_info(_user_id, _request_id):
    if _request_id != 'vad7er' and _request_id != '81432373':
        if 'deactivated' not in api.users.get(user_ids=_request_id)[0]:
            # Запрашиваем имя пользователя
            first_name = api.users.get(user_ids=_request_id)[0]['first_name']

            # Запрашиваем фамилию пользователя
            last_name = api.users.get(user_ids=_request_id)[0]['last_name']

            # Запрашиваем фото пользователя
            photo_id = api.users.get(user_ids=_request_id, fields='photo_id')[0]['photo_id']

            # Запрашиваем количество сообщений с пользователем
            # count = api.messages.getHistory(user_id=user_id)

            # Отправляем сообщение о пользователе
            message_template = '[id%s|%s %s]' if is_number(_request_id) else '[%s|%s %s]'
            api.messages.send(user_id=_user_id, random_id=randint(INT_MIN, INT_MAX),
                              message=message_template % (_request_id, first_name, last_name),
                              attachment='photo%s' % photo_id,
                              keyboard=json.loads(json.dumps(
                                  open('keyboards/keyboard.json', 'r', encoding='utf-8').read())))
        else:
            api.messages.send(user_id=_user_id, random_id=randint(INT_MIN, INT_MAX),
                              message='Аккаунт удалён с ID: %s' % _user_id,
                              keyboard=json.loads(json.dumps(
                                  open('keyboards/keyboard.json', 'r', encoding='utf-8').read())))

    else:
        # Загружаем картинку на сервера ВК
        pfile = post(api.photos.getMessagesUploadServer(peer_id=_user_id)['upload_url'],
                     files={'photo': open('images/kaneki.jpg', 'rb')}).json()

        photo = api.photos.saveMessagesPhoto(server=pfile['server'],
                                             photo=pfile['photo'],
                                             hash=pfile['hash'])[0]

        # Отправляем сообщение о Вадиме
        message_template = '[id%s|%s %s]' if is_number(request_id) else '[%s|%s %s]'
        api.messages.send(user_id=user_id, random_id=randint(-2147483648, 2147483647),
                          message=message_template % (_request_id, 'Dead', 'Inside'),
                          attachment='photo%s_%s' % (photo['owner_id'], photo['id']),
                          keyboard=json.loads(json.dumps(
                              open('keyboards/keyboard.json', 'r', encoding='utf-8').read())))


def start_info(_user_id):
    # Запрашиваем имя пользователя
    name = api.users.get(user_ids=_user_id)[0]['first_name']

    # Загружаем картинку на сервера ВК
    pfile = post(api.photos.getMessagesUploadServer(peer_id=_user_id)['upload_url'],
                 files={'photo': open('images/opa.jpg', 'rb')}).json()

    photo = api.photos.saveMessagesPhoto(server=pfile['server'],
                                         photo=pfile['photo'],
                                         hash=pfile['hash'])[0]

    # Отправляем сообщение "Привет, %name%" с картинкой
    api.messages.send(user_id=_user_id, random_id=randint(INT_MIN, INT_MAX),
                      message='Привет, %s &#128169;' % name,
                      attachment='photo%s_%s' % (photo['owner_id'], photo['id']),
                      keyboard=json.loads(json.dumps(
                          open('keyboards/keyboard.json', 'r', encoding='utf-8').read())))


session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
api = vk.API(session, v=VK_API_VERSION)

# Первый запрос к LongPoll: получаем server и key
longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']

started = False
find_id = False

while True:
    # Последующие запросы: меняется только ts
    longPoll = post('%s' % server, data={'act': 'a_check',
                                         'key': key,
                                         'ts': ts,
                                         'wait': 25}).json()

    if longPoll['updates'] and len(longPoll['updates']) != 0:
        for update in longPoll['updates']:
            if update['type'] == 'message_new':
                # Помечаем сообщение от этого пользователя как прочитанное
                api.messages.markAsRead(peer_id=update['object']['from_id'])
                user_id = update['object']['from_id']
                message = update['object']['text']

                if started:
                    if message == 'Начать':
                        started = True
                        start_info(user_id)

                    elif message == 'Найти пользователя по ID':
                        # Отправляем сообщение "Введите id пользователя"
                        find_id = True
                        api.messages.send(user_id=user_id, random_id=randint(INT_MIN, INT_MAX),
                                          message='Введите id пользователя',
                                          keyboard=json.loads(json.dumps(
                                              open('keyboards/empty_keyboard.json', 'r', encoding='utf-8').read())))

                    elif message == 'О себе':
                        person_info(user_id, user_id)

                    elif message == 'Отменить':
                        started = False
                        # Отправляем сообщение "ээ джааля уцышка" и два смайлика
                        api.messages.send(user_id=user_id, random_id=randint(INT_MIN, INT_MAX),
                                          message='ээ джааля уцышка &#129305;&#128170;',
                                          keyboard=json.loads(json.dumps(
                                              open('keyboards/start_keyboard.json', 'r', encoding='utf-8').read())))

                    elif find_id:
                        request_id = update['object']['text']
                        try:
                            person_info(user_id, request_id)
                            find_id = False
                        except vk.exceptions.VkAPIError:
                            # Отправляем сообщение о неверном вводе
                            find_id = False
                            api.messages.send(user_id=user_id, random_id=randint(INT_MIN, INT_MAX),
                                              message='Неверный ID : %s' % request_id,
                                              keyboard=json.loads(json.dumps(
                                                  open('keyboards/keyboard.json', 'r', encoding='utf-8').read())))
                    else:
                        # Отправляем сообщение о неверной команда
                        api.messages.send(user_id=user_id, random_id=randint(INT_MIN, INT_MAX),
                                          message='Неверная команда',
                                          keyboard=json.loads(json.dumps(
                                              open('keyboards/keyboard.json', 'r', encoding='utf-8').read())))
                else:
                    started = True
                    start_info(user_id)

    # Меняем ts для следующего запроса
    ts = longPoll['ts']
