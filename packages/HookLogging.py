# HookLogging
# VeriBlox Package for Logging through Discord

from httpx import post
from dotenv import load_dotenv
from os import getenv

load_dotenv()

def sendLog(text: str, error: bool = False):
    data = {"embeds": [{
      "title": "VeriBlox Log",
      "description": f"{text}",
      "color": 3092790
    }]}

    if error == True:
        data["embeds"][0]["title"] = "VeriBlox Error Log"
        data["embeds"][0]["color"] = 16738657

    hookURL = getenv("webhookurl")
    post(hookURL, json=data)