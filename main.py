import requests
import time
import threading
import codecs
import json
from sseclient import SSEClient as OriginalSSEClient

#================== LOGO ==================#
def print_logo():
    logo = r'''
╔══════════════════════════════════════╗
║   ♡ SWEETHEART AI GROUP GUARD BOT ♡  ║
╠══════════════════════════════════════╣
║  Made with Love by Broken Nadeem     ║
╚══════════════════════════════════════╝
'''
    print(logo)

#=============== CONFIG ===================#
ACCESS_TOKEN = "EAABXXX"  # ← यहाँ टोकन डालो
GROUP_ID = "1234567890123456"  # ← यहाँ ग्रुप ID डालो
LOCKED_NAME = "Testing"
GUARD_ACTIVE = False
#==========================================#

def send_message(msg):
    url = f"https://graph.facebook.com/v19.0/{GROUP_ID}/messages"
    data = {
        "message": msg,
        "access_token": ACCESS_TOKEN
    }
    requests.post(url, data=data)

def get_group_name():
    url = f"https://graph.facebook.com/v19.0/{GROUP_ID}?fields=thread_name&access_token={ACCESS_TOKEN}"
    res = requests.get(url)
    return res.json().get("thread_name")

def set_group_name(name):
    url = f"https://graph.facebook.com/v19.0/{GROUP_ID}"
    data = {
        "thread_name": name,
        "access_token": ACCESS_TOKEN
    }
    requests.post(url, data=data)

def name_guard():
    global GUARD_ACTIVE
    while True:
        if GUARD_ACTIVE:
            current = get_group_name()
            if current and current != LOCKED_NAME:
                send_message(f"⚠️ नाम बदलने की कोशिश हुई!\nनाम वापस सेट किया गया: {LOCKED_NAME}")
                set_group_name(LOCKED_NAME)
        time.sleep(5)

# ========= FULLY PATCHED SSEClient ========== #
class PatchedSSEClient:
    def __init__(self, url):
        self.url = url
        self.resp = requests.get(self.url, stream=True)
        self.decoder = codecs.getreader("utf-8")(self.resp.raw)

    def events(self):
        data = ""
        for line in self.decoder:
            line = line.strip()
            if not line:
                if data.startswith("data: "):
                    json_data = data[6:]
                    yield Event(json_data)
                data = ""
            else:
                data += line + "\n"

class Event:
    def __init__(self, data):
        self.data = data

def listen_for_commands():
    global GUARD_ACTIVE, LOCKED_NAME
    url = f"https://streaming-graph.facebook.com/v19.0/{GROUP_ID}/messages?access_token={ACCESS_TOKEN}"
    messages = PatchedSSEClient(url)
    for msg in messages.events():
        if msg.data:
            try:
                data = json.loads(msg.data)
                message = data.get("message", "")
                sender = data.get("from", {}).get("name", "Unknown")

                if message.lower() == "#nameguard on":
                    GUARD_ACTIVE = True
                    send_message(f"✅ Name Guard चालू किया गया {sender} द्वारा")
                elif message.lower() == "#nameguard off":
                    GUARD_ACTIVE = False
                    send_message(f"❌ Name Guard बंद कर दिया गया {sender} द्वारा")
                elif message.lower().startswith("#setname "):
                    new_name = message[9:].strip()
                    LOCKED_NAME = new_name
                    send_message(f"🔒 अब नया नाम लॉक है: {LOCKED_NAME}")
            except Exception as e:
                print("Error:", e)

#================= START ===================#
if __name__ == "__main__":
    print_logo()
    print("Bot चालू हो गया है... Command सुन रहा है...")
    threading.Thread(target=name_guard, daemon=True).start()
    listen_for_commands()
