# RobloxAPI
# VeriBLox Package for Creating API Requests to Roblox

from os import getenv
from httpx import get
from datetime import datetime
from dotenv import load_dotenv
from packages.Logging import log
load_dotenv(r"./conf/.env")
rbxcookie = getenv("rbxcookie")

def getInfo(user, verification: bool = False):
    if isinstance(user, str):
        log(f"RobloxAPI: Getting User Information for User: {user}")
        try:
            userId = get(f"https://api.roblox.com/users/get-by-username?username={user}")
            id = userId.json()["Id"]
            info = get(f"https://users.roblox.com/v1/users/{id}")
            info = info.json()
        except:
            log(f"RobloxAPI: Failed to get User Information for User: {user}", 1) 
            return {"success": False}

    if isinstance(user, int):
        log(f"RobloxAPI: Getting User Information for User ID: {user}")
        try:
            info = get(f"https://users.roblox.com/v1/users/{user}")
            info = info.json()
        except:
            log(f"RobloxAPI: Failed to get User Information for User ID: {user}", 1) 
            return {"success": False}
    
    log(f"RobloxAPI: Getting basic User Information...")
    username    = info["name"]
    displayName = info["displayName"]
    description = info["description"]
    banned      = info["isBanned"]
    created     = info["created"]
    userId      = info["id"]

    if verification == False:
        log(f"RobloxAPI: Getting additional User Information...")
        status  = get(f"https://api.roproxy.com/users/{userId}/onlinestatus/")
        friends = get(f"https://friends.roblox.com/v1/users/{userId}/friends/count")
        followers = get(f"https://friends.roblox.com/v1/users/{userId}/followers/count")
        following = get(f"https://friends.roblox.com/v1/users/{userId}/followings/count")

        status_pt = status.json()["PresenceType"]
        status = status.json()["LastLocation"]
        friends = friends.json()["count"]
        followers = followers.json()["count"]
        following = following.json()["count"]

        try:
            try:
                creationdate = datetime.fromisoformat(created[:-1] + '+00:00')
                created = f"Account Created on {creationdate.strftime('%d %B, %Y')}"
            except:
                creationdate = datetime.strptime(created,"%Y-%m-%dT%H:%M:%S.%fZ")
                created = f"Account Created on {creationdate.strftime('%d %B, %Y')}"
        except:
            creationdate = datetime.fromisoformat(created.split('.')[0])
            created = f"Account Created on {creationdate.strftime('%d %B, %Y')}"

        log(f"RobloxAPI: Information Sent with Additional User Information!")
        return {"success": True, "id": userId, "status": f"{status}", "pType": status_pt, "username": f"{username}", "displayname": f"{displayName}", "description": f"{description}", "created": f"{created}", "count": [friends, followers, following], "banned": banned}
    
    log(f"RobloxAPI: Information Sent!")
    return {"success": True, "id": userId, "username": f"{username}", "displayname": f"{displayName}", "description": f"{description}", "created": f"{created}", "banned": banned}

def getAvatar(type: str, userid: int, size : int):
    log(f"RobloxAPI: Getting Avatar URL for User ID: {userid} with Type: {type}")
    if type == "headshot":
        if size == 0:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=150x150&format=Png&isCircular=false")
        
        if size == 1:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=180x180&format=Png&isCircular=false")
        
        if size == 2:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=352x352&format=Png&isCircular=false")
        
        if size == 3:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=420x420&format=Png&isCircular=false")
        
        if size == 4:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=720x720&format=Png&isCircular=false")
        
    if type == "bustshot":
        if size == 0:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=150x150&format=Png&isCircular=false")
        
        if size == 1:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=180x180&format=Png&isCircular=false")
        
        if size == 2:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=352x352&format=Png&isCircular=false")
        
        if size == 3:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=420x420&format=Png&isCircular=false")
        
    if type == "fullbody":
        if size == 0:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=150x150&format=Png&isCircular=false")
        
        if size == 1:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=180x180&format=Png&isCircular=false")
        
        if size == 2:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=352x352&format=Png&isCircular=false")
        
        if size == 3:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=420x420&format=Png&isCircular=false")
        
        if size == 4:
            imageUrl = get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=720x720&format=Png&isCircular=false")
        
    log(f"RobloxAPI: Avatar Image Data Sent!")
    return imageUrl.json()["data"][0]["imageUrl"]

def getGame(game):
    if isinstance(game, str):
        log(f"RobloxAPI: Getting Game Information with Name: {game}")
        game = get(f"https://games.roblox.com/v1/games/list?model.keyword={game}&model.maxRows=1").json()

    if isinstance(game, int):
        log(f"RobloxAPI: Getting Game Information with ID: {game}")
        game = get(f"https://develop.roblox.com/v1/universes/{game}").json()["name"]
        game = get(f"https://games.roblox.com/v1/games/list?model.keyword={game}&model.maxRows=1").json()

    try:
        gameName  = game["games"][0]["name"]
        gameID    = game["games"][0]["placeId"]
        gameDesc  = game["games"][0]["gameDescription"]
        gameUID   = game["games"][0]["universeId"]
        gameOwner = game["games"][0]["creatorName"]
        gameOType = game["games"][0]["creatorType"]
        gameOwner = f"{gameOwner} ({gameOType})"

        players   = game["games"][0]["playerCount"]
        upvotes   = game["games"][0]["totalUpVotes"]
        downvotes = game["games"][0]["totalDownVotes"]

        img  = get(f"https://thumbnails.roblox.com/v1/games/icons?universeIds={gameUID}&size=512x512&format=Png&isCircular=false").json()["data"][0]["imageUrl"]
    except IndexError:
        return {"success": False}

    log("RobloxAPI: Game Data Sent!")
    return {"success": True, "name": f"{gameName}", "id": gameID, "description": f"{gameDesc}","owner": f"{gameOwner}", "playing": players, "l": upvotes, "d": downvotes, "imageURL": f"{img}"}

def getMembership(user):
    if isinstance(user, str):
        log(f"RobloxAPI: Getting Membership Status for User: {user}")
        try:
            user = get(f"https://api.roblox.com/users/get-by-username?username={user}")
            user = user.json()["Id"]
        except:
            log(f"RobloxAPI: Failed to get User Information for User: {user}", 1) 
            return {"success": False}

    else:
        log(f"RobloxAPI: Getting Membership Status for User ID: {user}")

    log("RobloxAPI: Membership Status Sent!")
    return get(f"https://premiumfeatures.roblox.com/v1/users/{user}/validate-membership", cookies={".ROBLOSECURITY": rbxcookie}).json()

def getGroupRoles(id: int):
    try:
        roles = get(f"https://groups.roblox.com/v1/groups/{id}/roles").json()["roles"]
        tempRoleList = []

        for x in range(len(roles) - 1):
            role = roles[x + 1]
            #                    ID          NAME
            tempRoleList.append((role["id"], role["name"], role["memberCount"]))
        return {"success": True, "roleList": tempRoleList}
    except:
        return {"success": False}
