import requests

# PyBloxAPI - a VeriBlox Package for creating API Requests
# PyBloxAPI Version: v1.2

# User
def getInfo(userid : int):
    try:
        info = requests.get(f"https://users.roblox.com/v1/users/{userid}").json()
        username    = info["name"]
        displayname = info["displayName"]
        description = info["description"]
        banned      = info["isBanned"]
        created     = info["created"]
    except:
        return {"username": "???", "displayname": "???", "description": "**VeriBlox Error**: This user does not exist.", "banned": True, "created": "2006-09-1T02:01:00.000Z"}

    return {"username": f"{username}", "displayname": f"{displayname}", "description": f"{description}", "banned": banned, "created": f"{created}"}

def getOnlineStatus(userid : int):
    try:
        status  = requests.get(f"https://api.roblox.com/users/{userid}/onlinestatus/").json()["LastLocation"]
    except:
        return {"status": "Offline"}
        
    return {"status": f"{status}"}

def getCount(userid : int):
    try:
        friends = requests.get(f"https://friends.roblox.com/v1/users/{userid}/friends/count").json()["count"]
        followers = requests.get(f"https://friends.roblox.com/v1/users/{userid}/followers/count").json()["count"]
        following = requests.get(f"https://friends.roblox.com/v1/users/{userid}/followings/count").json()["count"]

    except:
        return {"friends": "???", "followers": "???", "following": f"???"}

    return {"friends": f"{friends:,}", "followers": f"{followers:,}", "following": f"{following:,}"}

# User Avatar
def getAvatar(type: str, userid: int, size : str):
    # Sizes
    # 150 x 150 - 0
    # 180 x 180 - 1
    # 352 x 352 - 2
    # 420 x 420 - 3
    # 720 x 720 - 4
    if type == "headshot":
        if size == 0:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=150x150&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 1:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=180x180&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 2:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=352x352&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 3:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=420x420&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 4:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=720x720&format=Png&isCircular=false").json()["data"][0]["imageUrl"]


    if type == "bustshot":
        if size == 0:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=150x150&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 1:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=180x180&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 2:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=352x352&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 3:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=420x420&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

    if type == "fullbody":
        if size == 0:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=150x150&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 1:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=180x180&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 2:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=352x352&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 3:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=420x420&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 4:
            imageUrl = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=720x720&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

    return imageUrl