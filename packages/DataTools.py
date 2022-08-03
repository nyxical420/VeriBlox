# DataTools
# VeriBlox Package for Editing Data

import aiofiles
from json import loads, dumps
from packages.Logging import log

async def readUserData():
    async with aiofiles.open(r"data/users.json", "r") as f:
        data = loads(await f.read())
        return data

async def readGuildData():
    async with aiofiles.open(r"data/guilds.json", "r") as f:
        data = loads(await f.read())
        return data

async def appendUserData(data: object):
    async with aiofiles.open(r"data/users.json", "w") as f:
        await f.write(dumps(data, indent=4))

async def appendGuildData(data: object):
    async with aiofiles.open(r"data/guilds.json", "w") as f:
        await f.write(dumps(data, indent=4))

async def refreshUserData(userid: str):
    userData = await readUserData()

    try:
        userData[userid]["expiredAfter"] = 60
    except:
        return

    await appendUserData(userData)
    log(f"Refreshed user data for {userid}")

async def getrtTime(userid: str):
    async with aiofiles.open(r"data/ratelimited.json", "r") as f:
        data = loads(await f.read())
    
    return data[userid]["ratelimitTime"]

async def ratelimitUser(userid: str, time: int):
    async with aiofiles.open(r"data/ratelimited.json", "r") as f:
        data = loads(await f.read())

    if not userid in data:
        data[userid] = {}
        data[userid]["ratelimitTime"] = time

    else: data[userid]["ratelimitTime"] = time
    
    async with aiofiles.open(r"data/ratelimited.json", "w") as f:
        await f.write(dumps(data, indent=4))