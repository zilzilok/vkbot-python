from vk.exceptions import VkAPIError
from random import randint
from requests import *
import json
import vk

# Указываем ключи доступа, id группы и версию API
VK_API_ACCESS_TOKEN = 'abbd9e53577540e899a6f21a16ae3f1750dd256a69094895db2e9f5723b72d01ac03f5534338266a46e17'
VK_API_VERSION = '5.95'
GROUP_ID = 196362480

session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
api = vk.API(session, v=VK_API_VERSION)

# Первый запрос к LongPoll: получаем server и key
longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']
print(longPoll)

while True:
    # Последующие запросы: меняется только ts
    longPoll = post('%s' % server, data={'act': 'a_check',
                                         'key': key,
                                         'ts': ts,
                                         'wait': 25}).json()
    print(longPoll)

    if longPoll['updates'] and len(longPoll['updates']) != 0:
        for update in longPoll['updates']:
            if update['type'] == 'message_new':
                # Помечаем сообщение от этого пользователя как прочитанное
                api.messages.markAsRead(peer_id=update['object']['from_id'])
                user_id = update['object']['from_id']
                message = update['object']['text']

                if message == 'Начать':
                    # Запрашиваем имя пользователя
                    name = api.users.get(user_ids=user_id)[0]['first_name']

                    # Загружаем картинку на сервера ВК
                    pfile = post(api.photos.getMessagesUploadServer(peer_id=update['object']['from_id'])['upload_url'],
                                 files={'photo': open('images/opa.jpg', 'rb')}).json()

                    photo = api.photos.saveMessagesPhoto(server=pfile['server'],
                                                         photo=pfile['photo'],
                                                         hash=pfile['hash'])[0]

                    # Отправляем сообщение "Привет, %name%" с картинкой
                    api.messages.send(user_id=user_id, random_id=randint(-2147483648, 2147483647),
                                      message='Привет, %s &#128169;' % name,
                                      attachment='photo%s_%s' % (photo['owner_id'], photo['id']),
                                      keyboard=json.loads(
                                          json.dumps(open('keyboards/keyboard.json', 'r', encoding='utf-8').read())))

                elif message == 'Найти пользователя по ID':
                    # Отправляем сообщение "Введите id пользователя"
                    api.messages.send(user_id=user_id, random_id=randint(-2147483648, 2147483647),
                                      message='Введите id пользователя',
                                      keyboard=json.loads(
                                          json.dumps(
                                              open('keyboards/empty_keyboard.json', 'r', encoding='utf-8').read())))

                elif message == 'Отменить':
                    api.messages.send(user_id=user_id, random_id=randint(-2147483648, 2147483647),
                                      message='ээ джааля уцышка &#129305;&#128170;',
                                      keyboard=json.loads(
                                          json.dumps(
                                              open('keyboards/start_keyboard.json', 'r', encoding='utf-8').read())))

                else:
                    request_id = update['object']['text']
                    try:
                        # Запрашиваем имя пользователя
                        first_name = api.users.get(user_ids=request_id)[0]['first_name']

                        # Запрашиваем фамилию пользователя
                        last_name = api.users.get(user_ids=request_id)[0]['last_name']

                        # Запрашиваем фото пользователя
                        photo_url = api.users.get(user_ids=user_id, fields='photo_200')[0]['photo_200']
                        pfile = post(api.photos.getMessagesUploadServer(peer_id=update['object']['from_id'])['upload_url'],
                                     files={'photo': Image.open(BytesIO(get(photo_url).content))}).json()
                        photo = api.photos.saveMessagesPhoto(server=pfile['server'],
                                                             photo=pfile['photo'],
                                                             hash=pfile['hash'])[0]

                        # Запрашиваем количество сообщений с пользователем
                        # count = api.messages.getHistory(user_id=user_id)

                        # Отправляем сообщение "Введите id пользователя"
                        api.messages.send(user_id=user_id, random_id=randint(-2147483648, 2147483647),
                                          message='Это пользователь [id%s|%s %s].' % (
                                              request_id, first_name, last_name),
                                          # attachment='photo%s_%s' % (photo['owner_id'], photo['id']),
                                          keyboard=json.loads(
                                              json.dumps(
                                                  open('keyboards/keyboard.json', 'r', encoding='utf-8').read())))

                    except vk.exceptions.VkAPIError:
                        # Отправляем сообщение о неверном вводе
                        api.messages.send(user_id=user_id, random_id=randint(-2147483648, 2147483647),
                                          message='Неверный ввод',
                                          keyboard=json.loads(
                                              json.dumps(
                                                  open('keyboards/keyboard.json', 'r', encoding='utf-8').read())))

    # Меняем ts для следующего запроса
    ts = longPoll['ts']
