import telebot
import socket
import pyautogui
import platform
import cv2
import os
import subprocess
import ctypes
import requests
import pytube
import random
from wakeonlan import send_magic_packet
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Токен бота от BotFather
TOKEN = '7482583188:AAEm8k_3W4wJA6C5IrzfYt4uOT_0FwVFBUo'
# Твой Telegram ID (узнай через @userinfobot)
ADMIN_ID = '1447911438'
# ID группы для отправки сообщений
GROUP_ID = '-1002571744053'

bot = telebot.TeleBot(TOKEN)
menu_message_id = None  # Храним ID сообщения с меню

# Проверка авторизации
def is_authorized(user):
    return str(user.id) == ADMIN_ID

# Проверка доступности ПК
def is_pc_available():
    try:
        # Проверяем доступность ПК через простой ping (замени 'localhost' на IP твоего ПК, если бот на сервере)
        result = subprocess.run('ping -n 1 localhost', shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return result.returncode == 0
    except:
        return False

# Главное меню с кнопками
def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_ip = InlineKeyboardButton('🌐 Get IP', callback_data='cmd_ip')
    btn_screenshot = InlineKeyboardButton('📸 Screenshot', callback_data='cmd_screenshot')
    btn_sysinfo = InlineKeyboardButton('💻 Sys Info', callback_data='cmd_sysinfo')
    btn_webcam = InlineKeyboardButton('📷 Webcam', callback_data='cmd_webcam')
    btn_shutdown = InlineKeyboardButton('⏻ Shutdown', callback_data='cmd_shutdown')
    btn_wol = InlineKeyboardButton('🔌 Wake-on-LAN', callback_data='cmd_wol')
    btn_cmd = InlineKeyboardButton('🖥️ CMD', callback_data='cmd_cmd')
    btn_wallpaper = InlineKeyboardButton('🖼️ Wallpaper', callback_data='cmd_wallpaper')
    btn_open = InlineKeyboardButton('🌐 Open URL', callback_data='cmd_open')
    btn_play = InlineKeyboardButton('🎥 Play Video', callback_data='cmd_play')
    btn_dice = InlineKeyboardButton('🎲 Dice', callback_data='cmd_dice')
    btn_help = InlineKeyboardButton('❓ Help', callback_data='cmd_help')
    markup.add(btn_ip, btn_screenshot, btn_sysinfo, btn_webcam, btn_shutdown, btn_wol, btn_cmd, btn_wallpaper, btn_open, btn_play, btn_dice, btn_help)
    return markup

# Кнопка "Назад"
def get_back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🔙 Назад', callback_data='cmd_back'))
    return markup

# Функция для обновления меню
def update_menu(chat_id, message_id=None):
    global menu_message_id
    text = "Добро пожаловать! Используйте кнопки ниже для управления компьютером."
    try:
        if message_id:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=get_main_menu(), parse_mode='HTML')
            menu_message_id = message_id
        else:
            sent_message = bot.send_message(chat_id, text, reply_markup=get_main_menu(), parse_mode='HTML')
            menu_message_id = sent_message.message_id
    except Exception as e:
        sent_message = bot.send_message(chat_id, text, reply_markup=get_main_menu(), parse_mode='HTML')
        menu_message_id = sent_message.message_id

# Функции для команд
def get_ip():
    if not is_pc_available():
        bot.send_message(GROUP_ID, "⚠️ ПК выключен. Попробуйте включить через /wol.")
        return
    ip = socket.gethostbyname(socket.gethostname())
    bot.send_message(GROUP_ID, f"🌐 <b>IP-адрес:</b> {ip}", parse_mode='HTML')

def take_screenshot():
    if not is_pc_available():
        bot.send_message(GROUP_ID, "⚠️ ПК выключен. Попробуйте включить через /wol.")
        return
    screenshot = pyautogui.screenshot()
    screenshot.save('screenshot.png')
    bot.send_photo(GROUP_ID, open('screenshot.png', 'rb'), caption="📸 Скриншот сделан")
    os.remove('screenshot.png')

def get_sysinfo():
    if not is_pc_available():
        bot.send_message(GROUP_ID, "⚠️ ПК выключен. Попробуйте включить через /wol.")
        return
    sysinfo = f"""
💻 <b>Информация о системе</b>
• <b>Система:</b> {platform.system()}
• <b>Имя узла:</b> {platform.node()}
• <b>Релиз:</b> {platform.release()}
• <b>Версия:</b> {platform.version()}
• <b>Архитектура:</b> {platform.machine()}
• <b>Процессор:</b> {platform.processor()}
"""
    bot.send_message(GROUP_ID, sysinfo, parse_mode='HTML')

def take_webcam_screenshot():
    if not is_pc_available():
        bot.send_message(GROUP_ID, "⚠️ ПК выключен. Попробуйте включить через /wol.")
        return
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        bot.send_message(GROUP_ID, "📷 Веб-камера недоступна.")
        return
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('webcam.png', frame)
        bot.send_photo(GROUP_ID, open('webcam.png', 'rb'), caption="📷 Снимок с веб-камеры")
        os.remove('webcam.png')
    else:
        bot.send_message(GROUP_ID, "📷 Не удалось сделать снимок.")
    cap.release()

def shutdown_computer():
    if not is_pc_available():
        bot.send_message(GROUP_ID, "⚠️ ПК уже выключен.")
        return
    if platform.system() == 'Windows':
        os.system("shutdown /s /t 0")
    elif platform.system() == 'Linux':
        os.system("shutdown now")
    bot.send_message(GROUP_ID, "⏻ Компьютер выключается.")

def wake_on_lan():
    mac_address = '5A:57:F7:C7:D7:0A'
    send_magic_packet(mac_address)
    bot.send_message(GROUP_ID, "🔌 Отправлен сигнал Wake-on-LAN.")

def execute_cmd(command):
    if not is_pc_available():
        bot.send_message(GROUP_ID, "⚠️ ПК выключен. Попробуйте включить через /wol.")
        return
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        output = result.stdout if result.stdout else result.stderr
        bot.send_message(GROUP_ID, f"🖥️ <b>Результат команды:</b>\n<pre>{output}</pre>", parse_mode='HTML')
    except Exception as e:
        bot.send_message(GROUP_ID, f"🖥️ Ошибка при выполнении команды: {e}")

def set_wallpaper_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open('wallpaper.jpg', 'wb') as f:
                f.write(response.content)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath('wallpaper.jpg'), 3)
            bot.send_message(GROUP_ID, "🖼️ Обои успешно установлены!")
            os.remove('wallpaper.jpg')
        else:
            bot.send_message(GROUP_ID, "🖼️ Не удалось скачать изображение.")
    except Exception as e:
        bot.send_message(GROUP_ID, f"🖼️ Ошибка при установке обоев: {e}")

def set_wallpaper_from_file(file_path):
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(file_path), 3)
        bot.send_message(GROUP_ID, "🖼️ Обои успешно установлены!")
        os.remove(file_path)
    except Exception as e:
        bot.send_message(GROUP_ID, f"🖼️ Ошибка при установке обоев: {e}")

def open_url(url):
    if not is_pc_available():
        bot.send_message(GROUP_ID, "⚠️ ПК выключен. Попробуйте включить через /wol.")
        return
    try:
        import webbrowser
        webbrowser.open(url)
        bot.send_message(GROUP_ID, f"🌐 URL открыт: {url}")
    except Exception as e:
        bot.send_message(GROUP_ID, f"🌐 Ошибка при открытии URL: {e}")

def play_video(url):
    if not is_pc_available():
        bot.send_message(GROUP_ID, "⚠️ ПК выключен. Попробуйте включить через /wol.")
        return
    try:
        yt = pytube.YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        stream.download(filename='video.mp4')
        os.startfile('video.mp4')
        bot.send_message(GROUP_ID, f"🎥 Воспроизведение видео: {yt.title}")
    except Exception as e:
        bot.send_message(GROUP_ID, f"🎥 Ошибка при воспроизведении видео: {e}")

def roll_dice():
    if not is_pc_available():
        bot.send_message(GROUP_ID, "⚠️ ПК выключен. Попробуйте включить через /wol.")
        return
    result = random.randint(1, 6)
    bot.send_message(GROUP_ID, f"🎲 Бросаю кубик... Результат: **{result}**", parse_mode='HTML')

def send_help():
    help_text = """
Доступные команды:
🌐 /ip - Получить IP-адрес
📸 /screenshot - Сделать скриншот
💻 /sysinfo - Информация о системе
📷 /webcam - Снимок с веб-камеры
⏻ /shutdown - Выключить компьютер
🔌 /wol - Отправить сигнал Wake-on-LAN
🖥️ /cmd [команда] - Выполнить команду в консоли
🖼️ /wallpaper [URL] - Установить обои через URL или прикрепите изображение
🌐 /open [URL] - Открыть URL
🎥 /play [URL] - Воспроизвести видео
🎲 /dice - Бросить кубик
"""
    bot.send_message(GROUP_ID, help_text)

# Обработчики команд
@bot.message_handler(commands=['start'])
def start_message(message):
    global menu_message_id
    if is_authorized(message.from_user):
        update_menu(message.chat.id, menu_message_id)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этому боту.")

@bot.message_handler(commands=['ip'])
def ip_command(message):
    if is_authorized(message.from_user):
        get_ip()
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.message_handler(commands=['screenshot'])
def screenshot_command(message):
    if is_authorized(message.from_user):
        take_screenshot()
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.message_handler(commands=['sysinfo'])
def sysinfo_command(message):
    if is_authorized(message.from_user):
        get_sysinfo()
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.message_handler(commands=['webcam'])
def webcam_command(message):
    if is_authorized(message.from_user):
        take_webcam_screenshot()
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.message_handler(commands=['shutdown'])
def shutdown_command(message):
    if is_authorized(message.from_user):
        shutdown_computer()
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.message_handler(commands=['wol'])
def wol_command(message):
    if is_authorized(message.from_user):
        wake_on_lan()
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.message_handler(commands=['cmd'])
def cmd_command(message):
    global menu_message_id
    if is_authorized(message.from_user):
        command = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ''
        if command:
            execute_cmd(command)
        else:
            try:
                bot.edit_message_text("🖥️ Укажите команду, например: /cmd dir", chat_id=message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            except:
                sent_message = bot.send_message(message.chat.id, "🖥️ Укажите команду, например: /cmd dir", reply_markup=get_back_button())
                menu_message_id = sent_message.message_id
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.message_handler(commands=['wallpaper'])
def wallpaper_command(message):
    global menu_message_id
    if is_authorized(message.from_user):
        url = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ''
        if url:
            if not is_pc_available():
                bot.send_message(GROUP_ID, "⚠️ ПК выключен. Попробуйте включить через /wol.")
                return
            set_wallpaper_from_url(url)
        elif message.photo:
            if not is_pc_available():
                bot.send_message(GROUP_ID, "⚠️ ПК выключен. Попробуйте включить через /wol.")
                return
            try:
                file_info = bot.get_file(message.photo[-1].file_id)
                file = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
                with open('wallpaper.jpg', 'wb') as f:
                    f.write(file.content)
                set_wallpaper_from_file('wallpaper.jpg')
            except Exception as e:
                bot.send_message(GROUP_ID, f"🖼️ Ошибка при установке обоев: {e}")
        else:
            try:
                bot.edit_message_text("🖼️ Укажите URL изображения (например: /wallpaper https://example.com/image.jpg) или прикрепите изображение.", chat_id=message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            except:
                sent_message = bot.send_message(message.chat.id, "🖼️ Укажите URL изображения (например: /wallpaper https://example.com/image.jpg) или прикрепите изображение.", reply_markup=get_back_button())
                menu_message_id = sent_message.message_id
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.message_handler(commands=['open'])
def open_command(message):
    global menu_message_id
    if is_authorized(message.from_user):
        url = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ''
        if url:
            open_url(url)
        else:
            try:
                bot.edit_message_text("🌐 Укажите URL, например: /open https://google.com", chat_id=message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            except:
                sent_message = bot.send_message(message.chat.id, "🌐 Укажите URL, например: /open https://google.com", reply_markup=get_back_button())
                menu_message_id = sent_message.message_id
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.message_handler(commands=['play'])
def play_command(message):
    global menu_message_id
    if is_authorized(message.from_user):
        url = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ''
        if url:
            play_video(url)
        else:
            try:
                bot.edit_message_text("🎥 Укажите URL видео, например: /play https://youtube.com/watch?v=video_id", chat_id=message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            except:
                sent_message = bot.send_message(message.chat.id, "🎥 Укажите URL видео, например: /play https://youtube.com/watch?v=video_id", reply_markup=get_back_button())
                menu_message_id = sent_message.message_id
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.message_handler(commands=['dice'])
def dice_command(message):
    if is_authorized(message.from_user):
        roll_dice()
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

# Обработчик кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global menu_message_id
    if is_authorized(call.from_user):
        bot.answer_callback_query(call.id, "Команда принята, проверьте группу для результатов.")
        try:
            if call.data == 'cmd_ip':
                get_ip()
                bot.edit_message_text("Добро пожаловать! Используйте кнопки ниже для управления компьютером.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_main_menu())
            elif call.data == 'cmd_screenshot':
                take_screenshot()
                bot.edit_message_text("Добро пожаловать! Используйте кнопки ниже для управления компьютером.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_main_menu())
            elif call.data == 'cmd_sysinfo':
                get_sysinfo()
                bot.edit_message_text("Добро пожаловать! Используйте кнопки ниже для управления компьютером.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_main_menu())
            elif call.data == 'cmd_webcam':
                take_webcam_screenshot()
                bot.edit_message_text("Добро пожаловать! Используйте кнопки ниже для управления компьютером.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_main_menu())
            elif call.data == 'cmd_shutdown':
                shutdown_computer()
                bot.edit_message_text("Добро пожаловать! Используйте кнопки ниже для управления компьютером.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_main_menu())
            elif call.data == 'cmd_wol':
                wake_on_lan()
                bot.edit_message_text("Добро пожаловать! Используйте кнопки ниже для управления компьютером.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_main_menu())
            elif call.data == 'cmd_cmd':
                bot.edit_message_text("🖥️ Укажите команду, например: /cmd dir", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            elif call.data == 'cmd_wallpaper':
                bot.edit_message_text("🖼️ Укажите URL изображения (например: /wallpaper https://example.com/image.jpg) или прикрепите изображение.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            elif call.data == 'cmd_open':
                bot.edit_message_text("🌐 Укажите URL, например: /open https://google.com", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            elif call.data == 'cmd_play':
                bot.edit_message_text("🎥 Укажите URL видео, например: /play https://youtube.com/watch?v=video_id", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            elif call.data == 'cmd_dice':
                roll_dice()
                bot.edit_message_text("Добро пожаловать! Используйте кнопки ниже для управления компьютером.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_main_menu())
            elif call.data == 'cmd_help':
                send_help()
                bot.edit_message_text("Добро пожаловать! Используйте кнопки ниже для управления компьютером.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_main_menu())
            elif call.data == 'cmd_back':
                bot.edit_message_text("Добро пожаловать! Используйте кнопки ниже для управления компьютером.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_main_menu())
        except Exception as e:
            update_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "У вас нет доступа.")

# Запуск бота
bot.polling()