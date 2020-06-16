import os
from random import randint
from requests import *
import vk

# Указываем ключи доступа, id группы и версию API
VK_API_ACCESS_TOKEN = 'abbd9e53577540e899a6f21a16ae3f1750dd256a69094895db2e9f5723b72d01ac03f5534338266a46e17'
VK_API_VERSION = '5.110'
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
                print(update)
                # Помечаем сообщение от этого пользователя как прочитанное
                api.messages.markAsRead(peer_id=update['object']['from_id'])

                # Запрашиваем имя пользователя
                name = api.users.get(user_ids=update['object']['from_id'])[0]['first_name']

                # Загружаем картинку на сервера ВК
                pfile = post(api.photos.getMessagesUploadServer(peer_id=update['object']['from_id'])['upload_url'],
                             files={'photo': open('images/opa.jpg', 'rb')}).json()

                photo = \
                    api.photos.saveMessagesPhoto(server=pfile['server'], photo=pfile['photo'], hash=pfile['hash'])[0]

                # Отправляем сообщение "Привет, %name%" с картинкой
                api.messages.send(user_id=update['object']['from_id'], random_id=randint(-2147483648, 2147483647),
                                  message='Привет, %s &#128521;' % name,
                                  attachment='photo%s_%s' % (photo['owner_id'], photo['id']))

    # Меняем ts для следующего запроса
    ts = longPoll['ts']
