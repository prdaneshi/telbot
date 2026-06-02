import requests
import time

TOKEN = "2079808815:XW2j1AM2OrgpOSTQ2YeoAztTNKyWAQ3fvfA"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"

offset = 0

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    payload = {
        "offset": offset,
        "timeout": 30
    }
    response = requests.post(url, json=payload, timeout=35)
    response.raise_for_status()
    return response.json()

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()

def main():
    global offset

    print("Echo bot is running...")

    while True:
        try:
            data = get_updates(offset)

            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1

                    message = update.get("message")
                    if not message:
                        continue

                    chat = message.get("chat", {})
                    chat_id = chat.get("id")
                    text = message.get("text")

                    if chat_id and text:
                        print(f"Received from {chat_id}: {text}")
                        send_message(chat_id, text)

        except requests.exceptions.RequestException as e:
            print("Request error:", e)
            time.sleep(5)
        except Exception as e:
            print("Error:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
  
