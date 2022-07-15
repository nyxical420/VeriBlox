# Logging
# VeriBlox Package for Mimicking Discord.py Prints 

from datetime import datetime
from colorama import Fore, init
init(autoreset=True)

def log(text: str, color: int = 0):
    if color == 0:
        color = Fore.LIGHTBLUE_EX
        type = "INFO     "
        
    if color == 1:
        color = Fore.LIGHTRED_EX
        type = "ERROR    "

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return print(f"{Fore.LIGHTBLACK_EX}{date}{Fore.RESET} {color}{type}{Fore.RESET}{text}")
