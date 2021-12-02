from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import access as access

chat_name = access.chat_name
my_name = access.my_name
api_id = access.api_id
api_hash = access.api_hash

directory_input = "/home/ell/bot-vk/input/"
directory_output = "/home/ell/bot-vk/output/"

directory_user_donut = '/home/elliot/test/depoy/longpool/donut_users'

driver_path = "chromedriver/chromedriver"

token = access.token
group_id = access.group_id

"response_reference"
""""telegram"""
error = "Невозможно выполнить запрос."
face_not_found = "Лицо не найдено! Пожалуйста, используйте другое фото."
not_recognized = "Команда не опознанна. Попробуйте снова."
time_clean = 23

"""vk"""
donute_text = "Вы имеете полный доступ."
admins_list = access.admins_list
pattern_admin_add_donut = "/add-user"  # Предоставить пользователю расширенный доступ на один запрос
pattern_admin_remove_all = "/remove-all"  # Удалить всех юзеров с расширенным доступом
admin_remove_all_text = "Список пользователей, имеющих полный доступ на 1, запрос был очищен."  # Удалить всех юзеров с расширенным доступом

pattern_user_help = "/help"  # Запрос на помощь от администратора


send_photo = "Пожалуйста, отправьте фото."
select_action = "Выберите действие."
request_ok = "Ваша заявка принята\nВаш номер в очереди: "
not_subscribed = 'К сожалению, мы не можем обработать ваш запрос, пока вы не подпишитесь на нашу группу)'
set_level = "Пожалуйста, выберите уровень запроса."
set_pay = "Пожалуйста, осуществите платеж."
choice_list = ["Смена расы", "Найти двойника"]

"""Смена расы"""
set_race = "Oк. Выберите рассу."
set_strength = "Oк. Выберите силу фильтра."
race_list = ["Asia", "Africa", "Europe", "India"]
race_list_rus = ["Азия", "Африка", "Европа", "Индия"]
strength_list = ["Weak", "Normal", "Strong"]
strength_list_rus = ["Слабый", "Нормальный", "Сильный"]


"""Найди клона"""
level_find_clone_list = ['Обычный', 'Продвинутый']
buy_methods_list = ['Оформить подписку', 'Купить через администратора']
buy_advanced_level_text = "Купить полный доступ"
sex_list = ["Мужской", "Женский"]
set_sex = 'Пожалуйста, укажите ваш пол ("Мужской" - искать близнецов среди мужчин, "Женский" - среди женщин).'
contact_clone_text = "Связаться с двойником"
accept_response_text = "Ваша заявка принята, ожидайте ответа администратора."
how_get_advance_level_text = "Способы получения полного доступа.\n1. Приобрести платную подписку на месяц.\n2. Приобрести полный доступ на один запрос у администратора."
key_color_1 = "positive"


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


"""Получить клавиатуру для выбора уровн запроса"""
def get_keyboard_level():
    keyboard = VkKeyboard(one_time=True)
    for i in level_find_clone_list:
        keyboard.add_button(label=i, color=key_color_1)
    keyboard.add_line()
    keyboard.add_button(label="Отмена", color="negative")
    return keyboard


"""Получить клавиатуру для оплаты"""
def get_keyboard_pay():
    keyboard = VkKeyboard(one_time=True)
    g_id = 209170407
    hash = "action=pay-to-group&amount=1&group_id="+str(g_id)+"."
    keyboard.add_vkpay_button(hash=hash, payload={"type": "canel_payment"})
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


"""Получить клавиатуру для выбора связи с двойником"""
def get_keyboard_contact():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(label=contact_clone_text, color=key_color_1)
    keyboard.add_line()
    keyboard.add_button(label="Отмена", color="negative")
    return keyboard


"""Получить клавиатуру для выбора связи с двойником и покупки полного доступа"""
def get_keyboard_contact_and_level():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(label=contact_clone_text, color=key_color_1)
    keyboard.add_line()
    keyboard.add_button(label=buy_advanced_level_text, color=key_color_1)
    keyboard.add_line()
    keyboard.add_button(label="Отмена", color="negative")
    return keyboard


"""Получить клавиатуру для получения полного доступа"""
def get_keyboard_buy_advance_level():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_openlink_button(link=access.donut_link, label=buy_methods_list[0])
    keyboard.add_line()
    keyboard.add_button(label=buy_methods_list[1], color=key_color_1)
    keyboard.add_line()
    keyboard.add_button(label="Отмена", color="negative")
    return keyboard
