# RobloxAPI
# VeriBlox Package for Creating API Requests to Roblox

from requests import get
from packages.Logging import log

def getByUsername(username: str):
    try:
        robloxUser = get(f"https://api.roblox.com/users/get-by-username?username={username}").json()
        robloxUserName = robloxUser["Username"]
        robloxUserId   = robloxUser["Id"]
        
        try:
            robloxUser["success"]
            return {"success": False}
        except:
            return {"success": True, "Id": f"{robloxUserId}", "Username": f"{robloxUserName}"}
    except:
        return {"success": False}

def getInfo(userid : int):
    try:
        info = get(f"https://users.roblox.com/v1/users/{userid}").json()
        username    = info["name"]
        displayname = info["displayName"]
        description = info["description"]
        banned      = info["isBanned"]
        created     = info["created"]
        return {"username": f"{username}", "displayname": f"{displayname}", "description": f"{description}", "banned": banned, "created": f"{created}"}
    except:
        log(f"Failed to get user information for ID: {userid}", 1)
        return {"username": "???", "displayname": "???", "description": "**VeriBlox Error**: This user does not exist.", "banned": True, "created": "2006-09-1T02:01:00.000Z"}


def getOnlineStatus(userid : int):
    try:
        status  = get(f"https://api.roblox.com/users/{userid}/onlinestatus/").json()["LastLocation"]
    except:
        log(f"Failed to get user online status for ID: {userid}", 1)
        return {"status": "Offline"}
        
    return {"status": f"{status}"}

def getCount(userid : int):
    try:
        friends = get(f"https://friends.roblox.com/v1/users/{userid}/friends/count").json()["count"]
        followers = get(f"https://friends.roblox.com/v1/users/{userid}/followers/count").json()["count"]
        following = get(f"https://friends.roblox.com/v1/users/{userid}/followings/count").json()["count"]

    except:
        log(f"Failed to get user count for ID: {userid}", 1)
        return {"friends": "???", "followers": "???", "following": f"???"}

    return {"friends": f"{friends:,}", "followers": f"{followers:,}", "following": f"{following:,}"}

def getAvatar(type: str, userid: int, size : str):
    if type == "headshot":
        if size == 0:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=150x150&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 1:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=180x180&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 2:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=352x352&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 3:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=420x420&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 4:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=720x720&format=Png&isCircular=false").json()["data"][0]["imageUrl"]


    if type == "bustshot":
        if size == 0:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=150x150&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 1:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=180x180&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 2:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=352x352&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 3:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=420x420&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

    if type == "fullbody":
        if size == 0:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=150x150&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 1:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=180x180&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 2:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=352x352&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 3:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=420x420&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

        if size == 4:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=720x720&format=Png&isCircular=false").json()["data"][0]["imageUrl"]

    return imageUrl
