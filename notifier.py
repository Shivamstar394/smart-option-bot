import requests


class Notifier:
    def __init__(self, console=True, telegram=None):
        self.console = console
        self.telegram = telegram or {"enabled": False}

    def send(self, msg: str):
        if self.console:
            print(msg)
        if self.telegram.get("enabled"):
            bot_token = self.telegram.get("bot_token")
            chat_id = self.telegram.get("chat_id")
            if bot_token and chat_id:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = {"chat_id": chat_id, "text": msg}
                try:
                    requests.post(url, data=data, timeout=5)
                except Exception as e:
                    print(f"❌ Telegram notification failed: {e}")
        print("✅ Notification sent")
