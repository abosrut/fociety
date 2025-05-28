import telebot
import asyncio
import websockets
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
import output

# Display ASCII art on startup
for line in output.fsociety_ascii:
    print(line)
    sleep(0.1)

# Bot configuration
TOKEN = '7482583188:AAHTeesXXscQQZpsrpw86RJ04Z3SCy2UZBE'
ADMIN_ID = '1447911438'
bot = telebot.TeleBot(TOKEN)
menu_message_id = None
last_photo_message_id = None
connected_clients = {}

# Authorization check
def is_authorized(user):
    return str(user.id) == ADMIN_ID

# Generate main menu
def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_ip = InlineKeyboardButton('🌐 IP Address', callback_data='cmd_ip')
    btn_sysinfo = InlineKeyboardButton('💻 System Info', callback_data='cmd_sysinfo')
    btn_screenshot = InlineKeyboardButton('📸 Screenshot', callback_data='cmd_screenshot')
    btn_webcam = InlineKeyboardButton('📷 Webcam', callback_data='cmd_webcam')
    btn_shutdown = InlineKeyboardButton('⏻ Shutdown', callback_data='cmd_shutdown')
    btn_wol = InlineKeyboardButton('🔌 Wake-on-LAN', callback_data='cmd_wol')
    btn_cmd = InlineKeyboardButton('🖥️ CMD', callback_data='cmd_cmd')
    btn_kill = InlineKeyboardButton('🛑 Kill Process', callback_data='cmd_kill')
    btn_wallpaper = InlineKeyboardButton('🖼️ Wallpaper', callback_data='cmd_wallpaper')
    btn_open = InlineKeyboardButton('🌐 Open URL', callback_data='cmd_open')
    btn_play = InlineKeyboardButton('🎥 Play Video', callback_data='cmd_play')
    btn_dice = InlineKeyboardButton('🎲 Dice', callback_data='cmd_dice')
    btn_help = InlineKeyboardButton('❓ Help', callback_data='cmd_help')
    markup.add(btn_ip, btn_sysinfo, btn_screenshot, btn_webcam, btn_shutdown, btn_wol, btn_cmd, btn_kill, btn_wallpaper, btn_open, btn_play, btn_dice, btn_help)
    return markup

# Back button
def get_back_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🔙 Back', callback_data='cmd_back'))
    return markup

# Process list menu (fetched from client)
async def get_process_menu():
    if "computer_id" not in connected_clients:
        return None
    async with websockets.connect("ws://ПК_IP:8765") as websocket:
        await websocket.send(json.dumps({"command": "get_processes"}))
        response = await websocket.recv()
        processes = json.loads(response)
        markup = InlineKeyboardMarkup(row_width=1)
        for name, pid in processes:
            markup.add(InlineKeyboardButton(f"🛑 {name} (PID: {pid})", callback_data=f'kill_{pid}'))
        markup.add(InlineKeyboardButton('🔙 Back', callback_data='cmd_back'))
        return markup

# Update main menu
def update_menu(chat_id, message_id=None):
    global menu_message_id, last_photo_message_id
    text = "🎮 <b>Control Center</b>\nChoose an action below to manage your PC:"
    try:
        if message_id:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=get_main_menu(), parse_mode='HTML')
            menu_message_id = message_id
        else:
            sent_message = bot.send_message(chat_id, text, reply_markup=get_main_menu(), parse_mode='HTML')
            menu_message_id = sent_message.message_id
        if last_photo_message_id:
            try:
                bot.delete_message(chat_id, last_photo_message_id)
                last_photo_message_id = None
            except:
                pass
    except Exception as e:
        sent_message = bot.send_message(chat_id, text, reply_markup=get_main_menu(), parse_mode='HTML')
        menu_message_id = sent_message.message_id

# WebSocket server
async def handle_client(websocket, path):
    client_id = await websocket.recv()
    connected_clients[client_id] = websocket
    try:
        async for message in websocket:
            pass
    finally:
        del connected_clients[client_id]

async def start_websocket_server():
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        await asyncio.Future()

# Command handlers
async def send_command(command, data=None):
    if "computer_id" not in connected_clients:
        return {"error": "PC is offline"}
    async with websockets.connect("ws://ПК_IP:8765") as websocket:
        await websocket.send(json.dumps({"command": command, "data": data}))
        response = await websocket.recv()
        return json.loads(response)

@bot.message_handler(commands=['start'])
def start_handler(message):
    if is_authorized(message.from_user):
        update_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "🚫 <b>Access denied.</b>", parse_mode='HTML')

@bot.message_handler(commands=['ip'])
def ip_command(message):
    if is_authorized(message.from_user):
        asyncio.run_coroutine_threadsafe(handle_ip(message.chat.id, message.message_id), asyncio.get_event_loop())

@bot.message_handler(commands=['screenshot'])
def screenshot_command(message):
    if is_authorized(message.from_user):
        parts = message.text.split(' ', 1)
        monitor_index = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        asyncio.run_coroutine_threadsafe(handle_screenshot(message.chat.id, message.message_id, monitor_index), asyncio.get_event_loop())

@bot.message_handler(commands=['sysinfo'])
def sysinfo_command(message):
    if is_authorized(message.from_user):
        asyncio.run_coroutine_threadsafe(handle_sysinfo(message.chat.id, message.message_id), asyncio.get_event_loop())

@bot.message_handler(commands=['webcam'])
def webcam_command(message):
    if is_authorized(message.from_user):
        asyncio.run_coroutine_threadsafe(handle_webcam(message.chat.id, message.message_id), asyncio.get_event_loop())

@bot.message_handler(commands=['shutdown'])
def shutdown_command(message):
    if is_authorized(message.from_user):
        asyncio.run_coroutine_threadsafe(handle_shutdown(message.chat.id, message.message_id), asyncio.get_event_loop())

@bot.message_handler(commands=['wol'])
def wol_command(message):
    if is_authorized(message.from_user):
        from wakeonlan import send_magic_packet
        mac_address = 'D8-43-AE-8D-FD-2B'
        send_magic_packet(mac_address)
        bot.edit_message_text("🔌 <b>Wake-on-LAN signal sent.</b>", chat_id=message.chat.id, message_id=message.message_id, reply_markup=get_back_button(), parse_mode='HTML')

@bot.message_handler(commands=['cmd'])
def cmd_command(message):
    if is_authorized(message.from_user):
        cmd_text = message.text.split(' ', 1)
        if len(cmd_text) < 2:
            bot.edit_message_text("🖥️ <b>Введите команду, например: /cmd dir</b>", chat_id=message.chat.id, message_id=message.message_id, reply_markup=get_back_button(), parse_mode='HTML')
            return
        asyncio.run_coroutine_threadsafe(handle_cmd(message.chat.id, message.message_id, cmd_text[1]), asyncio.get_event_loop())

@bot.message_handler(commands=['kill'])
def kill_command(message):
    if is_authorized(message.from_user):
        asyncio.run_coroutine_threadsafe(handle_kill(message.chat.id, message.message_id), asyncio.get_event_loop())

@bot.message_handler(commands=['wallpaper'])
def wallpaper_command(message):
    if is_authorized(message.from_user):
        if message.reply_to_message and message.reply_to_message.photo:
            file_id = message.reply_to_message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            filename = str(uuid4()) + '.jpg'
            with open(filename, 'wb') as new_file:
                new_file.write(downloaded_file)
            asyncio.run_coroutine_threadsafe(handle_wallpaper_file(message.chat.id, message.message_id, filename), asyncio.get_event_loop())
        else:
            bot.edit_message_text("🖼️ <b>Ответьте на сообщение с изображением или укажите URL для обоев.</b>", chat_id=message.chat.id, message_id=message.message_id, reply_markup=get_back_button(), parse_mode='HTML')

@bot.message_handler(commands=['open'])
def open_command(message):
    if is_authorized(message.from_user):
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.edit_message_text("🌐 <b>Введите URL, например: /open https://example.com</b>", chat_id=message.chat.id, message_id=message.message_id, reply_markup=get_back_button(), parse_mode='HTML')
            return
        asyncio.run_coroutine_threadsafe(handle_open(message.chat.id, message.message_id, parts[1]), asyncio.get_event_loop())

@bot.message_handler(commands=['play'])
def play_command(message):
    if is_authorized(message.from_user):
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.edit_message_text("🎥 <b>Введите ссылку на YouTube видео, например: /play https://youtube.com/watch?v=...</b>", chat_id=message.chat.id, message_id=message.message_id, reply_markup=get_back_button(), parse_mode='HTML')
            return
        asyncio.run_coroutine_threadsafe(handle_play(message.chat.id, message.message_id, parts[1]), asyncio.get_event_loop())

@bot.message_handler(commands=['dice'])
def dice_command(message):
    if is_authorized(message.from_user):
        asyncio.run_coroutine_threadsafe(handle_dice(message.chat.id, message.message_id), asyncio.get_event_loop())

@bot.message_handler(commands=['help'])
def help_command(message):
    if is_authorized(message.from_user):
        help_text = """
📚 <b>Available Commands</b>
🌐 /ip - Get IP address
📸 /screenshot [monitor] - Capture screenshot (e.g., /screenshot 1 for second monitor)
💻 /sysinfo - System information
📷 /webcam - Webcam snapshot
⏻ /shutdown - Shutdown PC
🔌 /wol - Wake PC via Wake-on-LAN
🖥️ /cmd <command> - Execute command
🛑 /kill - List and terminate processes (e.g., wallpaper64.exe)
🖼️ /wallpaper - Set wallpaper (reply with image or URL)
🌐 /open <URL> - Open URL in browser
🎥 /play <URL> - Play YouTube video
🎲 /dice - Roll a dice
❓ /help - Show this help
"""
        bot.edit_message_text(help_text, chat_id=message.chat.id, message_id=message.message_id, reply_markup=get_back_button(), parse_mode='HTML')

# Async command handlers
async def handle_ip(chat_id, message_id):
    response = await send_command("get_ip")
    if "error" in response:
        bot.edit_message_text("⚠️ <b>PC is offline.</b> Try /wol to wake it.", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    else:
        bot.edit_message_text(f"🌐 <b>IP Address:</b> {response['ip']}", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')

async def handle_screenshot(chat_id, message_id, monitor_index):
    global last_photo_message_id
    response = await send_command("take_screenshot", {"monitor_index": monitor_index})
    if "error" in response:
        bot.edit_message_text("⚠️ <b>PC is offline.</b> Try /wol to wake it.", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    elif "file" in response:
        bot.delete_message(chat_id, message_id)
        sent_message = bot.send_photo(chat_id, open(response['file'], 'rb'), caption=f"📸 Screenshot (Monitor {monitor_index})", reply_markup=get_back_button())
        last_photo_message_id = sent_message.message_id
        os.remove(response['file'])
    else:
        bot.edit_message_text(f"📸 <b>Error capturing screenshot:</b> {response['message']}", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')

async def handle_sysinfo(chat_id, message_id):
    response = await send_command("get_sysinfo")
    if "error" in response:
        bot.edit_message_text("⚠️ <b>PC is offline.</b> Try /wol to wake it.", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    else:
        bot.edit_message_text(response['sysinfo'], chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')

async def handle_webcam(chat_id, message_id):
    global last_photo_message_id
    response = await send_command("take_webcam")
    if "error" in response:
        bot.edit_message_text("⚠️ <b>PC is offline.</b> Try /wol to wake it.", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    elif "file" in response:
        bot.delete_message(chat_id, message_id)
        sent_message = bot.send_photo(chat_id, open(response['file'], 'rb'), caption="📷 Webcam Snapshot", reply_markup=get_back_button())
        last_photo_message_id = sent_message.message_id
        os.remove(response['file'])
    else:
        bot.edit_message_text(f"📷 <b>Error capturing webcam:</b> {response['message']}", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')

async def handle_shutdown(chat_id, message_id):
    response = await send_command("shutdown")
    if "error" in response:
        bot.edit_message_text("⚠️ <b>PC is already off.</b>", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    else:
        bot.edit_message_text("⏻ <b>Shutting down PC...</b>", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')

async def handle_cmd(chat_id, message_id, command):
    response = await send_command("execute_cmd", {"command": command})
    if "error" in response:
        bot.edit_message_text("⚠️ <b>PC is offline.</b> Try /wol to wake it.", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    else:
        bot.edit_message_text(f"🖥️ <b>Command Output:</b>\n<pre>{response['output']}</pre>", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')

async def handle_kill(chat_id, message_id):
    markup = await get_process_menu()
    if not markup:
        bot.edit_message_text("⚠️ <b>PC is offline.</b> Try /wol to wake it.", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    else:
        bot.edit_message_text("🛑 <b>Выберите процесс для завершения:</b>", chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode='HTML')

async def handle_wallpaper_file(chat_id, message_id, file_path):
    response = await send_command("set_wallpaper_file", {"file": file_path})
    if "error" in response:
        bot.edit_message_text("⚠️ <b>PC is offline.</b> Try /wol to wake it.", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    else:
        bot.edit_message_text("🖼️ <b>Wallpaper set successfully!</b>", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
        os.remove(file_path)

async def handle_open(chat_id, message_id, url):
    response = await send_command("open_url", {"url": url})
    if "error" in response:
        bot.edit_message_text("⚠️ <b>PC is offline.</b> Try /wol to wake it.", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    else:
        bot.edit_message_text(f"🌐 <b>Opened URL:</b> {url}", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')

async def handle_play(chat_id, message_id, url):
    response = await send_command("play_video", {"url": url})
    if "error" in response:
        bot.edit_message_text("⚠️ <b>PC is offline.</b> Try /wol to wake it.", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    else:
        bot.edit_message_text(f"🎥 <b>Playing video:</b> {response['title']}", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')

async def handle_dice(chat_id, message_id):
    response = await send_command("roll_dice")
    if "error" in response:
        bot.edit_message_text("⚠️ <b>PC is offline.</b> Try /wol to wake it.", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    else:
        bot.edit_message_text(f"🎲 <b>Dice Roll:</b> **{response['result']}**", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')

# Callback query handler
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global last_photo_message_id
    if not is_authorized(call.from_user):
        bot.answer_callback_query(call.id, "🚫 Доступ запрещен.")
        return
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data == 'cmd_ip':
        asyncio.run_coroutine_threadsafe(handle_ip(chat_id, message_id), asyncio.get_event_loop())
    elif call.data == 'cmd_screenshot':
        asyncio.run_coroutine_threadsafe(handle_screenshot(chat_id, message_id, 0), asyncio.get_event_loop())
    elif call.data == 'cmd_sysinfo':
        asyncio.run_coroutine_threadsafe(handle_sysinfo(chat_id, message_id), asyncio.get_event_loop())
    elif call.data == 'cmd_webcam':
        asyncio.run_coroutine_threadsafe(handle_webcam(chat_id, message_id), asyncio.get_event_loop())
    elif call.data == 'cmd_shutdown':
        asyncio.run_coroutine_threadsafe(handle_shutdown(chat_id, message_id), asyncio.get_event_loop())
    elif call.data == 'cmd_wol':
        from wakeonlan import send_magic_packet
        mac_address = 'D8-43-AE-8D-FD-2B'
        send_magic_packet(mac_address)
        bot.edit_message_text("🔌 <b>Wake-on-LAN signal sent.</b>", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    elif call.data == 'cmd_cmd':
        bot.edit_message_text("🖥️ <b>Введите команду, например: /cmd dir</b>", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    elif call.data == 'cmd_kill':
        asyncio.run_coroutine_threadsafe(handle_kill(chat_id, message_id), asyncio.get_event_loop())
    elif call.data == 'cmd_wallpaper':
        bot.edit_message_text("🖼️ <b>Ответьте на сообщение с изображением или используйте /wallpaper с URL.</b>", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    elif call.data == 'cmd_open':
        bot.edit_message_text("🌐 <b>Введите URL, например: /open https://example.com</b>", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    elif call.data == 'cmd_play':
        bot.edit_message_text("🎥 <b>Введите ссылку на YouTube видео, например: /play https://youtube.com/watch?v=...</b>", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    elif call.data == 'cmd_dice':
        asyncio.run_coroutine_threadsafe(handle_dice(chat_id, message_id), asyncio.get_event_loop())
    elif call.data == 'cmd_help':
        help_command(call.message)
    elif call.data == 'cmd_back':
        if last_photo_message_id:
            try:
                bot.delete_message(chat_id, last_photo_message_id)
                last_photo_message_id = None
            except:
                pass
        update_menu(chat_id, message_id)
    elif call.data.startswith('kill_'):
        pid = int(call.data.split('_')[1])
        asyncio.run_coroutine_threadsafe(handle_kill_pid(chat_id, message_id, pid), asyncio.get_event_loop())

async def handle_kill_pid(chat_id, message_id, pid):
    response = await send_command("kill_process", {"pid": pid})
    if "error" in response:
        bot.edit_message_text("⚠️ <b>PC is offline.</b> Try /wol to wake it.", chat_id=chat_id, message_id=message_id, reply_markup=get_back_button(), parse_mode='HTML')
    else:
        bot.edit_message_text(f"🛑 <b>Process {response['name']} (PID: {pid}) terminated.</b>", chat_id=chat_id, message_id=message_id, reply_markup=await get_process_menu(), parse_mode='HTML')

# Start bot and WebSocket server
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_websocket_server())
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Bot error: {e}")
        sleep(5)
        bot.infinity_polling()