from datetime import datetime
import json
import os
import random
import re
import requests
import sys
import time
from threading import Thread

import vk_api
from vk_api import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from PIL import Image

from pyrogram import Client, filters

from worker import Worker

import config


print("spider-man")


"""Смена расы"""
race_list = ["Asia", "Africa", "Europe", "India"]
race_list_rus = ["Азия", "Африка", "Европа", "Индия"]

strength_list = ["Weak", "Normal", "Strong"]
strength_list_rus = ["Слабый", "Нормальный", "Сильный"]

directory_input = "input/"
directory_output = "output/"


"""Найди клона"""
sex_list = ["Мужской", "Женский"]


"""Запросы клиентов"""
choice_list = ["Смена расы", "Найти своего двойника"]
client_requests = {}
client_requests_complete = []  # Массив где содержаться user_id с заполненными параметрами

"""TELEGRAM"""
chat_name = config.chat_name
api_id = config.api_id
api_hash = config.api_hash
session_name = "session_name"
app_telegram = Client("session1", api_id, api_hash)
app_telegram.start()
app_telegram.send_message(chat_name, "/start")


"""VK"""
sys.stdout = sys.stderr
token = config.token
group_id = config.group_id
vk_session = vk_api.VkApi(token=token)
sesstion_api = vk_session.get_api()
vk_upload = VkUpload(vk_session)
longpool = VkLongPoll(vk_session)
key_color_1 = "positive"

def clear_mem():
    os.system('killall -9 chromedriver')
    os.system('killall -9 /opt/google/chrome/chrome')


class Queue:
    def __init__(self):
        self.queue = []
        self.last_request_done = time.time() - 6000

    def add_queue(self, o):
        self.queue.append(o)

    def start(self):
        Thread(target=self.run).start()

    def run(self):
        while True:
            while self.queue:
                ct = time.time()
                if ct - self.last_request_done < 5 * 60: time.sleep((5 * 60) - (ct - self.last_request_done))
                o = self.queue[0]
                o.start()
                try:
                    o.driver.quit()
                except:
                    pass
                self.queue.pop(0)
                clear_mem()
                self.last_request_done = time.time()
                print('Осталось заявок в очереди: %s' % len(self.queue))
            time.sleep(0.1)


queue = Queue()
queue.start()

"""Переводит русские сообщения в английские"""
def translate_message_to_eng(text, rus_list, eng_list):
    index = rus_list.index(text)
    return eng_list[index]


def get_largest_photo(sizes):
    largest_w = 0
    url = None
    for size in sizes:
        if size['width'] > largest_w:
            largest_w = size['width']
            url = size['url']
    return url


def cut_photo(path):
    img = Image.open(path)
    width, height = img.size  # Get dimensions
    cropped_example = img.crop((0, 0, width, height - 60))
    cropped_example.save(path)

"""Обрезка фото для бота изменения расы"""
def cut_photo_2(path):
    img = Image.open(path)
    width, height = img.size  # Get dimensions
    cropped_example = img.crop((0, 0, width, height - width*0.065))
    cropped_example.save(path)


"""Отправить сообщение"""
def send_some_msg(user_id, some_text, attachments=None, keyboard=None):
    post = {
        "user_id": user_id,
        "message": some_text,
        "random_id": 0,
    }
    if keyboard != None:
        post["keyboard"] = keyboard.get_keyboard()
    if attachments != None:
        post["attachment"] = attachments
    vk_session.method("messages.send", post)


""" Функция находит url не сжатого изображения """
def get_url(id, id_message):
    url = "None"
    message = vk_session.method("messages.getById", {"photos": id, "message_ids": id_message})
    max_size = 0
    for items in message.get("items"):
        attachments_list = items.get("attachments")
        for attachments in attachments_list:
            sizes_list = attachments.get("photo").get("sizes")
            for size in sizes_list:
                if size.get("height") + size.get("width") > max_size:
                    max_size = size.get("height") + size.get("width")
                    url = size.get("url")
    return url


"""Получить клавиатуру с одной кнопкой отмены"""
def get_keyboard_cancel():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(label="Отмена", color="negative")
    return keyboard


"""Получить клавиатуру для выбора действия"""
def get_keyboard_choice():
    keyboard = VkKeyboard(one_time=True)
    for i in choice_list:
        keyboard.add_button(label=i, color=key_color_1)
    return keyboard


"""Получить клавиатуру для выбора расы"""
def get_keyboard_race():
    keyboard = VkKeyboard(one_time=True)
    for i in race_list_rus:
        keyboard.add_button(label=i, color=key_color_1)
    keyboard.add_line()
    keyboard.add_button(label="Отмена", color="negative")
    return keyboard


"""Получить клавиатуру для выбора силы расы"""
def get_keyboard_strength():
    keyboard = VkKeyboard(one_time=True)
    for i in strength_list_rus:
        keyboard.add_button(label=i, color=key_color_1)
    keyboard.add_line()
    keyboard.add_button(label="Отмена", color="negative")
    return keyboard


"""Получить клавиатуру для выбора пола"""
def get_keyboard_sex():
    keyboard = VkKeyboard(one_time=True)
    for i in sex_list:
        keyboard.add_button(label=i, color=key_color_1)
    keyboard.add_line()
    keyboard.add_button(label="Отмена", color="negative")
    return keyboard


"""Функция удаляет не законченый процесс пользователя"""
def delete_client_request(user_id, input_photo_path=None, output_photo_path=None):
    client_requests.pop(user_id, "dont exist")

    if input_photo_path != None:
        os.remove(input_photo_path)
    if output_photo_path != None:
        os.remove(output_photo_path)


"""Функция удаляет законченый процесс пользователя"""
def delete_client_request_complete(client_request, input_photo_path=None, output_photo_path=None):
    global client_requests_complete
    client_requests_complete.remove(client_request)

    if input_photo_path != None:
        os.remove(input_photo_path)
    if output_photo_path != None:
        os.remove(output_photo_path)


"""Функция удаляет сообщения из чата с ботом"""
def delete_messages_from_chat():
    for message in app_telegram.iter_history(chat_name, limit=15):
        app_telegram.delete_messages(chat_name, message.message_id)


"""VK SIDE"""
def vk_side():
    while True:
        try:
            global client_requests
            print("Подключение установлено vk_side")
            for event in longpool.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if not event.from_chat:
                        if event.to_me:
                            user_id = event.user_id
                            msg_text = event.text
                            msg_id = event.message_id
                            is_member = sesstion_api.groups.isMember(group_id=group_id, user_id=user_id)
                            attach = event.attachments.get("attach1")
                            attach_type = event.attachments.get("attach1_type")
                            photo_url = get_url(attach, msg_id)
                            if not is_member:
                                send_some_msg(user_id,
                                              config.not_subscribed)
                            else:
                                print("Новое сообщение vk_side")
                                """Если прислано фото, возвращаемся к начальной стадии"""
                                if attach_type == 'photo':
                                    img_id = attach
                                    name_img = str(img_id) + ".jpg"
                                    client_requests = {
                                        user_id: {
                                            "stage": "choice",
                                            "date_create": datetime.now(),
                                            "photo_url": photo_url,
                                            "photo_path": name_img
                                        }
                                    }
                                    send_some_msg(user_id, config.select_action, keyboard=get_keyboard_choice())
                                else:
                                    if user_id in client_requests:
                                        if msg_text == "Отмена":
                                            delete_client_request(user_id)
                                            send_some_msg(user_id, config.send_photo)
                                        else:
                                            """Проверяем какое действие выбрал клиент"""
                                            if client_requests.get(user_id).get("choice") == "find_clone":
                                                if client_requests.get(user_id).get("stage") == "sex":
                                                    year = re.search(r'\d\d\d\d', msg_text)
                                                    if year:
                                                        year = int(year.group(0))
                                                    else:
                                                        year = 1990
                                                    sex = None
                                                    male_patterns = [r'^М$', r'^М\s', r'\sМ$']
                                                    male_patterns.append(sex_list[0])
                                                    female_patterns = [r'^Ж$', r'^Ж\s', r'\sЖ$', r'^Д$', r'^Д\s',
                                                                       r'\sД$']
                                                    female_patterns.append(sex_list[1])
                                                    for i in male_patterns:
                                                        if re.search(i, msg_text):
                                                            sex = 'm'
                                                            break
                                                    for i in female_patterns:
                                                        if re.search(i, msg_text):
                                                            sex = 'f'
                                                            break
                                                    if not sex:
                                                        send_some_msg(user_id,
                                                                      config.set_sex)
                                                    else:
                                                        photo_url = client_requests.get(user_id).get("photo_url")
                                                        send_some_msg(user_id,
                                                                      config.request_ok + str(len(queue.queue) + 1))
                                                        w = Worker(sesstion_api, user_id, photo_url, sex, year)
                                                        queue.add_queue(w)
                                                        delete_client_request(user_id)
                                            elif client_requests.get(user_id).get("choice") == "change_race":
                                                """"Проверяем на каком этапе находиться клиент"""
                                                if client_requests.get(user_id).get("stage") == "race":
                                                    if msg_text in race_list_rus:
                                                        new_data = client_requests.get(user_id)
                                                        new_data["stage"] = "strength"
                                                        new_data["race"] = race_list[race_list_rus.index(msg_text)]
                                                        client_requests[user_id] = new_data
                                                        send_some_msg(user_id, config.set_strength,
                                                                      keyboard=get_keyboard_strength())
                                                    else:
                                                        send_some_msg(user_id,
                                                                      config.not_recognized,
                                                                      keyboard=get_keyboard_race())
                                                elif client_requests.get(user_id).get("stage") == "strength":
                                                    if msg_text in strength_list_rus:
                                                        """Скачиваем отправленную фотографию"""
                                                        photo_url = client_requests.get(user_id).get("photo_url")
                                                        file = requests.get(photo_url)
                                                        name_img = client_requests.get(user_id).get("photo_path")
                                                        out = open(directory_input + name_img, "wb")
                                                        out.write(file.content)
                                                        out.close()

                                                        """Добавляем данные"""
                                                        new_data = client_requests.get(user_id)
                                                        new_data["stage"] = "complete"
                                                        new_data["strength"] = strength_list[
                                                            strength_list_rus.index(msg_text)]
                                                        new_data["user_id"] = user_id
                                                        client_requests_complete.append(
                                                            new_data)  # Добавляем запрос клиента в список законченных запросов
                                                        delete_client_request(
                                                            user_id)  # Удаляем запрос клиента из списка не законченных

                                                        """Показываем очередь"""
                                                        num = 1
                                                        for i in client_requests_complete:
                                                            if i.get("user_id") == user_id:
                                                                send_some_msg(user_id,
                                                                              config.request_ok + str(
                                                                                  len(client_requests_complete) + 1 - num))
                                                                break
                                                            num += 1
                                                    else:
                                                        send_some_msg(user_id,
                                                                      config.not_recognized,
                                                                      keyboard=get_keyboard_strength())
                                            else:
                                                if msg_text == choice_list[0]:
                                                    new_data = client_requests.get(user_id)
                                                    new_data["choice"] = "change_race"
                                                    new_data["stage"] = "race"
                                                    new_data["category"] = "Race"
                                                    client_requests[user_id] = new_data
                                                    send_some_msg(user_id, config.set_race,
                                                                  keyboard=get_keyboard_race())
                                                    is_choice = True
                                                if msg_text == choice_list[1]:
                                                    new_data = client_requests.get(user_id)
                                                    new_data["choice"] = "find_clone"
                                                    new_data["stage"] = "sex"
                                                    client_requests[user_id] = new_data
                                                    send_some_msg(user_id,
                                                                  config.set_sex,
                                                                  keyboard=get_keyboard_sex())
                                                    is_choice = True
                                                if not is_choice:
                                                    send_some_msg(user_id, config.select_action,
                                                                  keyboard=get_keyboard_choice())
                                    else:
                                        send_some_msg(user_id, config.send_photo)
        except Exception as e:
            print(e)
            print("Переподключение vk_side")
            time.sleep(30)


proc = Thread(target=vk_side)
proc.start()


"""TELEGRAM SIDE"""
complete = False
def run_telegram_side():
    global client_requests_complete
    last_time = datetime.now()
    is_client_delete = False
    delay = 0.8
    def get_time_delta():
        delta = datetime.now() - last_time
        time_delta = delta.seconds
        return time_delta
    try:
        print("Подключение установлено telegram_side")
        while True:
            """Проверяет есть ли клиенты в очереди, если есть, то обрабатывает запрос"""
            if len(client_requests_complete) != 0 and get_time_delta() >= 30:
                print("Обработка запроса (telegram_side)")
                client_request = client_requests_complete[0]
                user_id = client_request.get("user_id")
                category = client_request.get("category")
                race = client_request.get("race")
                strength = client_request.get("strength")

                img_name = client_request.get("photo_path")
                input_photo_path = directory_input + img_name  # конечный путь до входного файла
                output_photo_path = directory_output + img_name  # конечный путь до выходного файла
                app_telegram.send_photo(chat_name, input_photo_path)  # отправляем фото боту

                time.sleep(delay)
                global complete
                complete = False
                stage = "category"
                series = 0
                while not complete:
                    """Условие если запросов для одного клиета слишком много, выдать ошибку"""
                    if series > 85:
                        send_some_msg(user_id, config.error)
                        delete_client_request_complete(client_request, input_photo_path)
                        delete_messages_from_chat()
                        last_time = datetime.now()
                        complete = True
                        break
                    """Запросы на новые сообщения"""
                    for message in app_telegram.iter_history(chat_name, limit=4):
                        print(series)
                        print(stage)
                        series += 1
                        if message.from_user.username == chat_name:
                            if not message.media:
                                """Условия для отправки параметров боту"""
                                if "category" in message.text and stage == "category":
                                    app_telegram.send_message(chat_name, category)
                                    stage = "filter_type"
                                    time.sleep(delay)
                                    break
                                elif "filter type" in message.text and stage == "filter_type":
                                    app_telegram.send_message(chat_name, race)
                                    stage = "filter_strength"
                                    time.sleep(delay)
                                    break
                                elif "strength" in message.text and stage == "filter_strength":
                                    app_telegram.send_message(chat_name, strength)
                                    stage = "get_photo"

                                    time.sleep(delay)
                                    break

                                """Условия для обработки ошибки"""
                                if "not found" in message.text:
                                    send_some_msg(user_id, config.face_not_found)
                                    delete_client_request_complete(client_request, input_photo_path)
                                    complete = True
                                    delete_messages_from_chat()

                                    last_time = datetime.now()
                                    break
                                elif "Timeout" in message.text and "not recognized":
                                    send_some_msg(user_id, config.error)
                                    delete_client_request_complete(client_request, input_photo_path)
                                    complete = True
                                    delete_messages_from_chat()

                                    last_time = datetime.now()
                                    break
                            if message.media and stage == "get_photo":
                                app_telegram.download_media(message.photo, output_photo_path)
                                cut_photo_2(output_photo_path)
                                upload_image = vk_upload.photo_messages(photos=output_photo_path)[
                                    0]  # загружаем файл на сервер
                                owner_id = upload_image['owner_id']
                                photo_id = upload_image['id']
                                access_key = upload_image['access_key']
                                attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                                send_some_msg(user_id, "Результат: ", attachment)  # отправляем сообщение с вложением

                                delete_client_request_complete(client_request, input_photo_path, output_photo_path)
                                complete = True

                                delete_messages_from_chat()

                                last_time = datetime.now()
            time.sleep(1)

            """В 11 часов удаляем все запросы, которые храняться более 5 часов"""
            now = datetime.now()
            if now.hour == 23 and not is_client_delete:
                is_client_delete = True
                for user_id in client_requests:
                    delta = now - client_request.get(user_id).get("date_create")
                    if delta.hour > 5:
                        delete_client_request(client_request)
            if now.hour != 23:
                is_client_delete = False
    except Exception as e:
        print(e)
        print("Переподключение telegram_side")
        if len(client_requests_complete) != 0:
            send_some_msg(user_id,config.error)
            delete_client_request_complete(client_request, input_photo_path)
            complete = True
        time.sleep(30)


run_telegram_side()