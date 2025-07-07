import json
import logging
import os
import platform

import psutil
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_DEV1_ID = os.getenv("DEV1_ID")
TELEGRAM_DEV1_NAME = os.getenv("DEV1_NAME")

TELEGRAM_DEVS = os.getenv("TELEGRAM_DEVS")


# TODO: Talvez seja util implementar monitoramento de temperatura
# TODO: Existe uma configuração para a mensagem emitir notificação silenciosa
#       ou não, isso pode ser util para erros criticos
class TelegramLogger:
    def __init__(self, token, chat_id, log_filename):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.devs = json.loads(TELEGRAM_DEVS) if TELEGRAM_DEVS else []
        self.log_filename = log_filename

    def send_message(self, message: str) -> None:
        """Sends a message to the configured Telegram chat."""
        # TODO: Em mensagens de Warinig pode ser interessante marcar usuários de desenvolvimento
        try:

            message = self.format_message(message, self.log_filename)

            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML",
            }

            requests.post(self.api_url, data=payload)

        except Exception as e:
            print(f"[Error] Failed to send log message: {e}")

    def format_message(self, message: str, log_filename: str) -> str:
        message = message[26:]

        if "INFO" in message:
            message = "🟢 " + message

        elif "ERROR" in message:
            message = "🔴 " + message

        elif "WARNING" in message:
            message = "🟡 " + message

        elif "CRITICAL" in message:
            message = "❗❗ " + message

            mentions = []
            for dev in self.devs:
                mention = f'<a href="tg://user?id={dev["id"]}">{dev["name"]}</a>'
                mentions.append(mention)

            if mentions:
                message += "\n" + ", ".join(mentions)

        else:
            message = "🟠 " + message
        return log_filename + " " + message

    @staticmethod
    def get_operating_system() -> str:
        """Returns the name of the operating system."""
        try:
            return platform.system()
        except Exception as e:
            print(f"[Error] Failed to get operating system: {e}")
            return "Unknown"

    @staticmethod
    def get_execution_path() -> str:
        """Returns the script execution path."""
        try:
            return os.getcwd()
        except Exception as e:
            print(f"[Error] Failed to get execution path: {e}")
            return "Unknown"

    @staticmethod
    def get_logged_user() -> str:
        """Returns the logged-in user's name."""
        try:
            return os.getlogin()
        except Exception as e:
            print(f"[Error] Failed to get logged user: {e}")
            return "Unknown"

    @staticmethod
    def get_cpu_usage() -> float:
        """Returns the current CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            print(f"[Error] Failed to get CPU usage: {e}")
            return -1.0

    @staticmethod
    def get_memory_usage() -> float:
        """Returns the current memory usage percentage."""
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            print(f"[Error] Failed to get memory usage: {e}")
            return -1.0

    def make_test_message(self) -> str:
        """Creates a test log message with system information."""
        try:
            message = (
                "\U0001f4dd Log de Execução\n"
                f"\U0001f464 Usuário: {self.get_logged_user()}\n"
                f"\U0001f4c2 Caminho de execução: {self.get_execution_path()}\n"
                f"\U0001f4bb Sistema operacional: {self.get_operating_system()}\n"
                f"\U0001f4ca Uso CPU: {self.get_cpu_usage()}%\n"
                f"\U0001f4ca Uso Memória: {self.get_memory_usage()}%\n"
            )
            return message
        except Exception as e:
            print(f"[Error] Failed to create test message: {e}")
            return ""

    def send_test_message(self) -> None:
        """Sends a test log message with system information."""
        try:
            message = self.make_test_message()
            self.send_message(message)
        except Exception as e:
            print(f"[Error] Failed to send test message: {e}")


class TelegramLogHandler(logging.Handler):
    """Custom logging handler to send logs to Telegram."""

    def __init__(self, telegram_logger: TelegramLogger):
        super().__init__()
        self.telegram_logger = telegram_logger

    def emit(self, record):
        try:
            log_entry = self.format(record)  # Formata a mensagem do log
            self.telegram_logger.send_message(log_entry)  # Envia para o Telegram
        except Exception as e:
            print(f"[TelegramError] Failed to send log to Telegram: {e}")


if __name__ == "__main__":
    print("env TOKEN: ", TOKEN)
    print("env CHAT_ID: ", CHAT_ID)

    telegram_logger = TelegramLogger(TOKEN, CHAT_ID, "test.log")
    msg = """
2025-02-11 14:15:59,664 - ERROR - Ocorreu um erro no loop de agendamento: Message: 
Stacktrace:
	(No symbol) [0x00007FF6E4526B15]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF6E484F4A4+1437348]
	sqlite3_dbdata_init [0x00007FF6E48F2DE6+643190]
	(No symbol) [0x00007FF6E444C9DB]
	(No symbol) [0x00007FF6E444CAE3]
	(No symbol) [0x00007FF6E44892F7]
	(No symbol) [0x00007FF6E446C1DF]
	(No symbol) [0x00007FF6E4443437]
	(No symbol) [0x00007FF6E4486BFF]
	(No symbol) [0x00007FF6E446BE03]
	(No symbol) [0x00007FF6E4442984]
	(No symbol) [0x00007FF6E4441E30]
	(No symbol) [0x00007FF6E4442571]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF6E47FBB34+1094964]
	(No symbol) [0x00007FF6E45632C8]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF6E47FAF73+1091955]
	Microsoft::Applications::Events::EventProperty::empty [0x00007FF6E47FAAD9+1090777]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF6E4600CE1+461569]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF6E45FCA04+444452]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF6E45FCB49+444777]
	Microsoft::Applications::Events::ILogConfiguration::operator* [0x00007FF6E45F21C6+401382]
	BaseThreadInitThunk [0x00007FFEF2277614+20]
	RtlUserThreadStart [0x00007FFEF30826F1+33]


"""
    telegram_logger.send_message(msg)
    telegram_logger.send_test_message()
