import telebot
import socket
import platform
import os
import requests
import random
import time
import subprocess
from wakeonlan import send_magic_packet
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytube import YouTube

TOKEN = '7482583188:AAFj3GdfbPG1LGrnX0lVX-CBIcbAK1R8mA4'
ADMIN_ID = '1447911438'
GROUP_ID = '-1002571744053'

bot = telebot.TeleBot(TOKEN)
menu_message_id = None

def is_authorized(user):
    return str(user.id) == ADMIN_ID

def is_device_available():
    try:
        result = subprocess.run(['ping', '-c', '1', 'localhost'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def clean_chat():
    try:
        message_id = 1
        deleted_count = 0
        while True:
            try:
                bot.delete_message(GROUP_ID, message_id)
                deleted_count += 1
                message_id += 1
                time.sleep(0.1)
            except telebot.apihelper.ApiTelegramException as e:
                if "message to delete not found" in str(e):
                    message_id += 1
                    continue
                elif "chat not found" in str(e) or "bot is not a member" in str(e):
                    bot.send_message(GROUP_ID, "🧹 Ошибка: Бот не является админом группы или не имеет доступа.")
                    return
                else:
                    break
        if deleted_count > 0:
            bot.send_message(GROUP_ID, f"🧹 Удалено {deleted_count} сообщений!")
        else:
            bot.send_message(GROUP_ID, "🧹 Нет сообщений для удаления.")
    except Exception as e:
        bot.send_message(GROUP_ID, f"🧹 Ошибка при очистке чата: {e}")

def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [
        ('🌐 Get IP', 'cmd_ip'),
        ('📸 Screenshot', 'cmd_screenshot'),
        ('💻 Sys Info', 'cmd_sysinfo'),
        ('📷 Webcam', 'cmd_webcam'),
        ('🔌 Wake-on-LAN', 'cmd_wol'),
        ('🖥️ CMD', 'cmd_cmd'),
        ('🖼️ Wallpaper', 'cmd_wallpaper'),
        ('🌐 Open URL', 'cmd_open'),
        ('🎥 Play Video', 'cmd_play'),
        ('🎲 Dice', 'cmd_dice'),
        ('❓ Help', 'cmd_help'),
        ('🧹 Clean Chat', 'cmd_clean')
    ]
    for text, data in buttons:
        markup.add(InlineKeyboardButton(text, callback_data=data))
    return markup

def get_back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🔙 Назад', callback_data='cmd_back'))
    return markup

def update_menu(chat_id, message_id=None):
    global menu_message_id
    text = "Добро пожаловать! Используйте кнопки ниже для управления устройством."
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

def get_ip():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        bot.send_message(GROUP_ID, f"🌐 <b>IP-адрес:</b> {ip}", parse_mode='HTML')
    except Exception as e:
        bot.send_message(GROUP_ID, f"🌐 Ошибка получения IP: {e}")

def take_screenshot():
    try:
        subprocess.run(['termux-screenshot', '/sdcard/screenshot.png'], check=True)
        bot.send_photo(GROUP_ID, open('/sdcard/screenshot.png', 'rb'), caption="📸 Скриншот сделан")
        os.remove('/sdcard/screenshot.png')
    except Exception as e:
        bot.send_message(GROUP_ID, f"📸 Ошибка при создании скриншота: {e}")

def get_sysinfo():
    try:
        sysinfo = f"""
💻 <b>Информация о системе</b>
• <b>Система:</b> {platform.system()}
• <b>Имя узла:</b> {platform.node()}
• <b>Релиз:</b> {platform.release()}
• <b>Версия:</b> {platform.version()}
• <b>Архитектура:</b> {platform.machine()}
"""
        bot.send_message(GROUP_ID, sysinfo, parse_mode='HTML')
    except Exception as e:
        bot.send_message(GROUP_ID, f"💻 Ошибка получения информации: {e}")

def take_webcam_screenshot():
    try:
        subprocess.run(['termux-camera-photo', '-c', '0', '/sdcard/webcam.jpg'], check=True)
        bot.send_photo(GROUP_ID, open('/sdcard/webcam.jpg', 'rb'), caption="📷 Снимок с камеры")
        os.remove('/sdcard/webcam.jpg')
    except Exception as e:
        bot.send_message(GROUP_ID, f"📷 Ошибка при использовании камеры: {e}")

def shutdown_device():
    bot.send_message(GROUP_ID, "⏻ Выключение недоступно на Android без root.")

def wake_on_lan():
    mac_address = '5A:57:F7:C7:D7:0A'
    send_magic_packet(mac_address)
    bot.send_message(GROUP_ID, "🔌 Отправлен сигнал Wake-on-LAN.")

def execute_cmd(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        bot.send_message(GROUP_ID, f"🖥️ <b>Результат:</b>\n<code>{output}</code>", parse_mode='HTML')
    except Exception as e:
        bot.send_message(GROUP_ID, f"🖥️ Ошибка при выполнении команды: {e}")

def set_wallpaper_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open('/sdcard/wallpaper.jpg', 'wb') as f:
                f.write(response.content)
            subprocess.run(['termux-wallpaper', '-f', '/sdcard/wallpaper.jpg'], check=True)
            bot.send_message(GROUP_ID, "🖼️ Обои установлены!")
            os.remove('/sdcard/wallpaper.jpg')
        else:
            bot.send_message(GROUP_ID, "🖼️ Не удалось скачать изображение.")
    except Exception as e:
        bot.send_message(GROUP_ID, f"🖼️ Ошибка при установке обоев: {e}")

def set_wallpaper_from_file(file_path):
    try:
        subprocess.run(['termux-wallpaper', '-f', file_path], check=True)
        bot.send_message(GROUP_ID, "🖼️ Обои установлены!")
        os.remove(file_path)
    except Exception as e:
        bot.send_message(GROUP_ID, f"🖼️ Ошибка при установке файла: {e}")

def open_url(url):
    try:
        subprocess.run(['termux-open-url', url], check=True)
        bot.send_message(GROUP_ID, f"🌐 URL открыт: {url}")
    except Exception as e:
        bot.send_message(GROUP_ID, f"🌐 Ошибка при открытии URL: {e}")

def play_video(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        stream.download(filename='/sdcard/video.mp4')
        subprocess.run(['termux-open', '/sdcard/video.mp4'], check=True)
        bot.send_message(GROUP_ID, f"🎥 Воспроизведение видео: {yt.title}")
        os.remove('/sdcard/video.mp4')
    except Exception as e:
        bot.send_message(GROUP_ID, f"🎥 Ошибка при воспроизведении видео: {e}")

def roll_dice():
    result = random.randint(1, 6)
    bot.send_message(GROUP_ID, f"🎲 Бросаю кубик... Результат: **{result}**", parse_mode='HTML')

def send_help():
    help_text = """
Доступные команды:
🌐 /ip - Получить IP-адрес
📸 /screenshot - Сделать скриншот
💻 /sysinfo - Информация о системе
📷 /webcam - Снимок с камеры
🔌 /wol - Отправить сигнал Wake-on-LAN
🖥️ /cmd [команда] - Выполнить команду в Termux
🖼️ /wallpaper [URL] - Установить обои через URL или прикрепить изображение
🌐 /open [URL] - Открыть URL
🎥 /play [URL] - Воспроизвести видео
🎲 /dice - Бросить кубик
🧹 /clean - Очистить чат группы
"""
    bot.send_message(GROUP_ID, help_text)

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
        shutdown_device()
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
                bot.edit_message_text("🖥️ Укажите команду, например: /cmd ls", chat_id=message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            except:
                sent_message = bot.send_message(message.chat.id, "🖥️ Укажите команду, например: /cmd ls", reply_markup=get_back_button())
                menu_message_id = sent_message.message_id
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.message_handler(commands=['wallpaper'])
def wallpaper_command(message):
    global menu_message_id
    if is_authorized(message.from_user):
        url = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ''
        if url:
            set_wallpaper_from_url(url)
        elif message.photo:
            try:
                file_info = bot.get_file(message.photo[-1].file_id)
                file = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
                with open('/sdcard/wallpaper.jpg', 'wb') as f:
                    f.write(file.content)
                set_wallpaper_from_file('/sdcard/wallpaper.jpg')
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

@bot.message_handler(commands=['clean'])
def clean_command(message):
    if is_authorized(message.from_user):
        clean_chat()
    else:
        bot.send_message(message.chat.id, "Нет доступа.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global menu_message_id
    if is_authorized(call.from_user):
        bot.answer_callback_query(call.id, "Команда принята, проверьте группу для результатов.")
        try:
            commands = {
                'cmd_ip': get_ip,
                'cmd_screenshot': take_screenshot,
                'cmd_sysinfo': get_sysinfo,
                'cmd_webcam': take_webcam_screenshot,
                'cmd_shutdown': shutdown_device,
                'cmd_wol': wake_on_lan,
                'cmd_dice': roll_dice,
                'cmd_help': send_help,
                'cmd_clean': clean_chat
            }
            if call.data in commands:
                commands[call.data]()
                bot.edit_message_text("Добро пожаловать! Используйте кнопки ниже для управления устройством.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_main_menu())
            elif call.data == 'cmd_cmd':
                bot.edit_message_text("🖥️ Укажите команду, например: /cmd ls", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            elif call.data == 'cmd_wallpaper':
                bot.edit_message_text("🖼️ Укажите URL изображения (например: /wallpaper https://example.com/image.jpg) или прикрепите изображение.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            elif call.data == 'cmd_open':
                bot.edit_message_text("🌐 Укажите URL, например: /open https://google.com", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            elif call.data == 'cmd_play':
                bot.edit_message_text("🎥 Укажите URL видео, например: /play https://youtube.com/watch?v=video_id", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_back_button())
            elif call.data == 'cmd_back':
                bot.edit_message_text("Добро пожаловать! Используйте кнопки ниже для управления устройством.", chat_id=call.message.chat.id, message_id=menu_message_id, reply_markup=get_main_menu())
        except Exception as e:
            update_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "У вас нет доступа.")

try:
    bot.get_updates(offset=-1)
except:
    pass

bot.remove_webhook()
bot.polling(none_stop=True)