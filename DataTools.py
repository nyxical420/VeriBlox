from json import load, dump

def readUserData():
    with open(r"verifystatus.json", "r") as f:
        return load(f)

def readGuildData():
    with open(r"guildsettings.json", "r") as f:
        return load(f)

def appendUserData(data : object):
    with open(r"verifystatus.json", "w") as f:
        dump(data, f, indent=4)

def appendGuildData(data : object):
    with open(r"guildsettings.json", "w") as f:
        dump(data, f, indent=4)

def refreshUserData(userid : str):
    with open(r"verifystatus.json", "r") as f:
        data =  load(f)

    try:
        data[userid]["expiredAfter"] = 60
    except:
        return

    with open(r"verifystatus.json", "w") as f:
        dump(data, f, indent=4)