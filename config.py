# -*- coding: utf-8 -*-

import sqlite3 as sql # СУБД
import requests as req # для работы с запросами
import random # для рандомных вещей

class bots_long_poll_api():
    """работа с bots long poll api"""

    """инициализирую ключ доступа группы, id группы, версию long poll api соответственно"""
    def __init__(self, access_token, group_id, v_long_poll_api):
        self.access_token = access_token
        self.group_id = group_id
        self.v_long_poll_api = v_long_poll_api

    """запросы к api"""
    def api_request(self, method_name, options={}):
        options['v'] = self.v_long_poll_api
        options['access_token'] = self.access_token
        return req.get(f'https://api.vk.com/method/{method_name}', params=options).json()

    """получение событий от long poll api"""
    def api_updates(self):
        response = bots_long_poll_api.api_request(self, 'groups.getLongPollServer', options={'group_id': self.group_id})
        server = response['response']['server']
        key = response['response']['key']
        ts = response['response']['ts']
        return req.get(f'{server}?act=a_check&key={key}&ts={ts}&wait=25', params={'access_token': self.access_token, 'v': self.v_long_poll_api}).json()

class sqlite3():
    """работа с sqlite3"""

    """код в разработке"""
    def __init__(self):
        pass

    """создание таблицы пользователей"""
    def create_table_users(self, directory):
        base_date = sql.connect(f'{directory}')
        cursor = base_date.cursor()
        cursor.execute(f'CREATE TABLE IF NOT EXISTS users (Name TEXT, Level INTEGER)')
        base_date.commit()
        cursor.close()
        base_date.close()

    """создание таблицы задач"""
    def create_table_tasks(self, directory, name_table):
        base_date = sql.connect(f'{directory}')
        cursor = base_date.cursor()
        cursor.execute(f'CREATE TABLE IF NOT EXISTS {name_table} (Task TEXT, Value TEXT)')
        base_date.commit()
        cursor.close()
        base_date.close()

    """удаление таблицы"""
    def delete_table(self, directory, name_table):
        base_date = sql.connect(f'{directory}')
        cursor = base_date.cursor()
        cursor.execute(f'DROP TABLE IF EXISTS {name_table}')
        base_date.commit()
        cursor.close()
        base_date.close()

    """добавление строки в таблицу"""
    def add_string_table(self, directory, name_table, value1, value2):
        base_date = sql.connect(f'{directory}')
        cursor = base_date.cursor()
        cursor.execute(f'INSERT INTO {name_table} VALUES({value1}, {value2})')
        base_date.commit()
        cursor.close()
        base_date.close()

    """удаление строки из таблицы по парамтерам"""
    def delete_string_table(self, directory, name_table, key, value):
        base_date = sql.connect(f'{directory}')
        cursor = base_date.cursor()
        cursor.execute(f'DELETE FROM {name_table} WHERE {key} = {value}')
        base_date.commit()
        cursor.close()
        base_date.close()

    """получение данных из таблицы по определенному парметру"""
    def table_info(self, directory, name_table, element):
        base_date = sql.connect(f'{directory}')
        cursor = base_date.cursor()
        cursor.execute(f"SELECT {element} FROM {name_table}")
        info = cursor.fetchall()
        cursor.close()
        base_date.close()
        return info

    """обновление уровня пользователя"""
    def update_user(self, directory, name_user):
        base_date = sql.connect(f'{directory}')
        cursor = base_date.cursor()
        cursor.execute(f"UPDATE users SET Level = Level + 1 WHERE Name = {name_user}")
        base_date.commit()
        cursor.close()
        base_date.close()

    """изменение уровня пользователя"""
    def edit_user(self, directory, name_user, new_level):
        base_date = sql.connect(f'{directory}')
        cursor = base_date.cursor()
        cursor.execute(f"UPDATE users SET Level = {new_level} WHERE Name = {name_user}")
        base_date.commit()
        cursor.close()
        base_date.close()

    """получение задачи и ее ответа"""
    def get_task_and_value(self, object):
        random_index = random.randint(0, len(object)-1)
        task, value = object[random_index]
        return task, value

    """получение списка топ-10 игроков"""
    def get_top_10_users(self, directory):
        sql = sqlite3()
        users, message, flag = sql.table_info(f'{directory}', 'users', '*'), 'Топ 10 игроков:\n', 1
        for name, level in users:
            message += f'{flag} >> Имя: {name}, Уровень: {level}\n'
        if len(message) == 16:
            return 'Еще нет ни одного игрока'
        else:
            return message

    """редактирование сообщения с запятой на соощение с точкой"""
    def edit_message_virgule(self, message):
        new_message = ''
        for symbol in message:
            if symbol != ',':
                new_message += symbol
            else:
                new_message += '.'
        return new_message