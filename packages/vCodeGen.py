# vCodeGen
# VeriBlox Package for Generating Verification Codes
from random import choice

words = ["verification", "verify", "veriblox", "roblox", "api",
         "home", "interaction", "code", "cat", "dog",
         "duck", "elephant", "lion", "tiger", "zebra", 
         "panda", "frog", "bird", "eagle", "phone", 
         "laptop", "computer", "console", "keyboard", "mouse", 
         "screen", "watch", "camera", "movie", "backpack",
         "cap", "speaker", "sunglasses", "fan", "mirror",
         "gamepad", "tetris", "games", "avatar", "wireless"]

def gen():
    code = ""

    for x in range(12):
        code += choice(words)
        if x != 11: code += " "
    
    return code