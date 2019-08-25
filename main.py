# -*- coding: utf-8 -*-

from modules import config # локальный модуль
import re

vk = config.bots_long_poll_api('2f894a490ab3cbcdb0776b8f53557a8c8b6e1197ef0f4485586ea1868a533d88ff384e8742f8934e2c77c', 185666679, 5.101) # создаю экземпляр класса 'bots_long_poll_api'
sql = config.sqlite3() # создаю экземпляр класса 'sqlite3'

while True: # чтобы не пропускать ни одного события
    response = vk.api_updates() # записываю событие в переменную, если оно произошло
    if response['updates']: # если событие все-таки произошло
        if response['updates'][0]['type'] == 'message_new': # если это было новое сообщение
            message = response['updates'][0]['object']['text'] # извлекаю это сообщение
            peer_id = response['updates'][0]['object']['peer_id'] # извлекаю идентификатор назначения

            if re.fullmatch(r'/ботать\s[\D\S]+', message.lower()): # если пользователь хочет получить задачу
                try: # пробую отправить задачу пользователю
                    if message.lower()[8:] == 'матешу': # если он хотел задачу по математике
                        task, value = sql.get_task_and_value(sql.table_info('files/vk_bot.db', 'mat_tasks', '*')) # получаю саму задачу и ее ответ для дальнейшей проверки
                        vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': 'Задача:', 'attachment': task}) # отправляю сообщение с задачей
                    elif message.lower()[8:] == 'русич': # если он хотел задачу по русскому
                        task, value = sql.get_task_and_value(sql.table_info('files/vk_bot.db', 'rus_tasks', '*'))  # получаю саму задачу и ее ответ для дальнейшей проверки
                        vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': 'Задача:', 'attachment': task})  # отправляю сообщение с задачей
                    elif message.lower()[8:] == 'инфу': # если он хотел задачу по информатике
                        task, value = sql.get_task_and_value(sql.table_info('files/vk_bot.db', 'inf_tasks', '*'))  # получаю саму задачу и ее ответ для дальнейшей проверки
                        vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': 'Задача:', 'attachment': task})  # отправляю сообщение с задачей
                except: # если не получится, отправлю сообщение об ошибке
                    vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': 'Задание не удалось получить'}) # отправляю сообщение об ошибке

            elif re.fullmatch(r'/ответ\s.+', message.lower()): # если пользователь отправляет ответ
                if re.findall(r'\d+,\d+', message.lower()[7:]): # если в его ответе содержится дробное число с запятой
                    message = sql.edit_message_virgule(message.lower()) # меняю сообщение с запятой на сообщение с точкой
                try: # попробую проверить ответ на верность
                    if message.lower()[7:] == value: # если ответ верный
                        from_id = response['updates'][0]['object']['from_id'] # получаю id победителя
                        response = vk.api_request('users.get', options={'user_ids': from_id, 'fields': 'sex'}) # получаю информацию о нем
                        first_name = response['response'][0]['first_name'] # извлекаю его имя
                        last_name = response['response'][0]['last_name'] # извлекаю его фамилию
                        sex = response['response'][0]['sex'] # извлекаю пол
                        if sex == 1: # если это женщина
                            vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': f'{first_name} {last_name} победила!\nЕё уровень повышен!'}) # отправляю поздравление для нее
                        elif sex == 2: # если это мужчина
                            vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': f'{first_name} {last_name} победил!\nЕго уровень повышен!'}) # отправляю поздравление для него
                        else: # иначе, если пол не определен
                            vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': f'{first_name} {last_name} победило!\nЕго уровень повышен!'}) # отправляю поздравление для кого-то
                        if len(sql.table_info('files/vk_bot.db', 'users', 'Name')) > 0: # если в базе есть хоть один игрок
                            if f'{first_name} {last_name}' in sql.table_info('files/vk_bot.db', 'users', 'Name')[0]: # если победитель есть в базе
                                sql.update_user('files/vk_bot.db', f'"{first_name} {last_name}"') # повышаю его уровень на 1
                            else:  # иначе
                                sql.add_string_table('files/vk_bot.db', 'users', f'"{first_name} {last_name}"', 1)  # добавляю его в базу с 1 уровнем
                        else: # иначе
                            sql.add_string_table('files/vk_bot.db', 'users', f'"{first_name} {last_name}"', 1) # добавляю его в базу с 1 уровнем
                        del value, task # удаляю задачу и ответ
                    else: # если пользователь ошибся
                        vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': 'Ответ неверный'}) # отправляю сообщение об ошибке
                except NameError: # если произошла такая ошибка, значит пользователь еще не получил задание
                    vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': 'Сначала получите задание'}) # отправляю сообщение об ошибке

            elif message.lower() == '/топ': # если пользователь хочет посмотреть топ-игроков
                top_users = sql.get_top_10_users('files/vk_bot.db') # получаю список
                vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': top_users}) # отправляю топ-лист

            elif message.lower() == '/команды':  # если пользователь хочет посмотреть команды
                vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': 'Мои команды:\n>> /ботать матешу (выдача задачи по математике)\n>> /ботать русич (выдача задачи по русскому)\n>> /ботать инфу (выдача задачи по информатике)\n>> /ответ {тут ваш ответ} (ответ на текущую задачу)\n>> /выйти (выход из текущей задачи)\n>> /топ (топ-10 игроков)\n>> /удалить аккаунт (удаление вашего аккаунта навсегда!)\n>> /команды (список команд)'}) # отправляю команды

            elif message.lower() == '/удалить аккаунт': # если пользователь хочет удалить свой аккаунт
                from_id = response['updates'][0]['object']['from_id'] # получаю его id
                response = vk.api_request('users.get', options={'user_ids': from_id, 'fields': 'sex'}) # получаю информацию о нем
                first_name = response['response'][0]['first_name']  # извлекаю его имя
                last_name = response['response'][0]['last_name']  # извлекаю его фамилию
                if len(sql.table_info('files/vk_bot.db', 'users', 'Name')) > 0: # если в базе есть хоть один игрок
                    if f'{first_name} {last_name}' in sql.table_info('files/vk_bot.db', 'users', 'Name')[0]: # если пользователь есть в базе
                        sql.delete_string_table('files/vk_bot.db', 'users', 'Name', f"'{first_name} {last_name}'") # удаляю его аккаунт
                        vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': 'Удаление аккаунта завершено'}) # отправляю сообщение об удалении
                    else: # если он не в базе, отправляю ошибку
                        vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': 'Вас нет в списке игроков'}) # отправляю сообщение об ошибке
                else:
                    vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': 'Вас нет в списке игроков'})  # отправляю сообщение об ошибке

            elif message.lower() == '/выйти': # если пользователь хочет выйти из текущей задачи
                try: # попробую это сделать
                    del task, value # удаляю задачу и ответ
                except NameError: # если ошибка,значит пользователь еще не вошел в режим решения задач
                    vk.api_request('messages.send', options={'peer_id': peer_id, 'random_id': 0, 'message': 'Сначала начните ботать'}) # отправляю сообщение об ошибке