import os
import time
import pyttsx3
import speech_recognition as sr
import pyautogui
import webbrowser
import requests
import datetime
from threading import Thread
import json

# Инициализация движка озвучивания
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Скорость речи
engine.setProperty('volume', 1)  # Громкость

# Список программ для запуска
programs = {
    "хром": "chrome",
    "проводник": "explorer",
    "калькулятор": "calc",
    "блокнот": "notepad",
    "пейнт": "mspaint",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "skype": "skype",
    "telegram": "telegram",
    "фото": "photoshop",
    "firefox": "firefox",
    "sublime": "sublime_text",
    "vlc": "vlc",
    "steam": "steam",
    "discord": "discord",
    "zoom": "zoom",
    "твиттер": "chrome --new-tab https://twitter.com",
    "вконтакте": "chrome --new-tab https://vk.com",
    "youtube": "chrome --new-tab https://youtube.com",
    "telegram": "chrome --new-tab https://web.telegram.org"
}

# Глобальные переменные
last_interaction_time = time.time()
conversation_history = []  # История разговоров
current_query = ""  # Текущий запрос пользователя

# Функция озвучивания текста
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Функция для записи разговора в лог
def log_conversation(user_input, response):
    timestamp = datetime.datetime.now().strftime("%H:%M")
    conversation_history.append(f"Пользователь ({timestamp}): {user_input}")
    conversation_history.append(f"Джарвис ({timestamp}): {response}")

# Функция для распознавания речи
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language='ru-RU').lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""

# Функция для обработки команд пользователя
def process_command(command):
    global last_interaction_time, current_query
    current_query = command
    last_interaction_time = time.time()

    # Если команда "Джарвис"
    if "джарвис" in command:
        speak("Слушаю, сэр")
        log_conversation(command, "Слушаю, сэр")
        return

    # Если команда на запуск программы
    for program_name, program_command in programs.items():
        if f"открой {program_name}" in command or f"запусти {program_name}" in command:
            os.system(program_command)
            speak(f"Открываю {program_name}, что-то еще, сэр?")
            log_conversation(command, f"Открываю {program_name}, что-то еще, сэр?")
            return

    # Если команда на поиск в интернете
    if "найди в интернете" in command:
        query = command.replace("найди в интернете", "").strip()
        search_internet(query)
        return

    # Если команда на поиск в браузере
    if "найди в браузере" in command:
        query = command.replace("найди в браузере", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        speak("Открываю браузер с вашим запросом")
        log_conversation(command, "Открываю браузер с вашим запросом")
        return

    # Если команда на завершение разговора
    if "спасибо" in command or "нет, спасибо" in command:
        speak("До свидания, сэр")
        log_conversation(command, "До свидания, сэр")
        return_to_background()

# Функция для поиска в интернете
def search_internet(query):
    response = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json")
    data = response.json()
    if "AbstractText" in data:
        result = data["AbstractText"]
        with open("answer.txt", "w", encoding="utf-8") as f:
            f.write(result)
        speak(f"Найдено: {result}. Вам озвучить или сами прочитаете?")
        log_conversation(current_query, f"Найдено: {result}. Вам озвучить или сами прочитаете?")
        return

# Функция для возврата в фоновый режим
def return_to_background():
    global last_interaction_time
    last_interaction_time = time.time()

# Функция для фонового режима
def background_mode():
    global last_interaction_time
    while True:
        if time.time() - last_interaction_time > 20:
            speak("Пока, сэр")
            log_conversation("Пока", "Пока")
            break
        command = recognize_speech()
        if command:
            process_command(command)

# Функция для записи и отправки в Telegram
def send_to_telegram():
    token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    messages = "\n".join(conversation_history)
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={messages}"
    requests.get(url)

# Запуск программы
if __name__ == "__main__":
    speak("Здравствуйте, сэр. Готов к выполнению команд.")
    log_conversation("Приветствие", "Здравствуйте, сэр. Готов к выполнению команд.")
    background_mode_thread = Thread(target=background_mode)
    background_mode_thread.start()
