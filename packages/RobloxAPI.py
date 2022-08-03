# RobloxAPI
# VeriBLox Package for Creating API Requests to Roblox

import httpx
from packages.Logging import log

async def getInfo(user, verification: bool = False):
    if isinstance(user, str):
        try:
            async with httpx.AsyncClient() as client:
                userId = await client.get(f"https://api.roblox.com/users/get-by-username?username={user}")
                id = userId.json()["Id"]
                info = await client.get(f"https://users.roblox.com/v1/users/{id}")
                info = info.json()
        except:
            log(f"Failed to get User Information for User: {user}", 1) 
            return {"success": False}

    if isinstance(user, int):
        try:
            async with httpx.AsyncClient() as cli:
                info = await cli.get(f"https://users.roblox.com/v1/users/{user}")
                info = info.json()
        except:
            log(f"Failed to get User Information for User ID: {user}", 1) 
            return {"success": False}
    
    username    = info["name"]
    displayName = info["displayName"]
    description = info["description"]
    banned      = info["isBanned"]
    created     = info["created"]
    userId      = info["id"]

    if verification == False:
        async with httpx.AsyncClient() as cli:
            status  = await cli.get(f"https://api.roblox.com/users/{userId}/onlinestatus/")
            friends = await cli.get(f"https://friends.roblox.com/v1/users/{userId}/friends/count")
            followers = await cli.get(f"https://friends.roblox.com/v1/users/{userId}/followers/count")
            following = await cli.get(f"https://friends.roblox.com/v1/users/{userId}/followings/count")

            status = status.json()["LastLocation"]
            friends = friends.json()["count"]
            followers = followers.json()["count"]
            following = following.json()["count"]
            return {"success": True, "id": userId, "status": f"{status}", "username": f"{username}", "displayname": f"{displayName}", "description": f"{description}", "created": f"{created}", "count": [friends, followers, following], "banned": banned}

    return {"success": True, "id": userId, "username": f"{username}", "displayname": f"{displayName}", "description": f"{description}", "created": f"{created}", "banned": banned}

async def getAvatar(type: str, userid: int, size : int):
    async with httpx.AsyncClient() as cli:
        if type == "headshot":
            if size == 0:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=150x150&format=Png&isCircular=false")
        
            if size == 1:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=180x180&format=Png&isCircular=false")
        
            if size == 2:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=352x352&format=Png&isCircular=false")
        
            if size == 3:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=420x420&format=Png&isCircular=false")
        
            if size == 4:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=720x720&format=Png&isCircular=false")
        
        if type == "bustshot":
            if size == 0:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=150x150&format=Png&isCircular=false")
        
            if size == 1:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=180x180&format=Png&isCircular=false")
        
            if size == 2:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=352x352&format=Png&isCircular=false")
        
            if size == 3:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={userid}&size=420x420&format=Png&isCircular=false")
        
        if type == "fullbody":
            if size == 0:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=150x150&format=Png&isCircular=false")
        
            if size == 1:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=180x180&format=Png&isCircular=false")
        
            if size == 2:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=352x352&format=Png&isCircular=false")
        
            if size == 3:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=420x420&format=Png&isCircular=false")
        
            if size == 4:
                imageUrl = await cli.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={userid}&size=720x720&format=Png&isCircular=false")
        
        return imageUrl.json()["data"][0]["imageUrl"]
        