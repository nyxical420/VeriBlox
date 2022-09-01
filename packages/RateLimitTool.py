# RateLimitTool
# VeriBlox Package for Ratelimiting Users

import aiofiles
from packages.Logging import log
from json import loads, dumps

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
        log(f"RateLimitTool: Successfully Ratelimited user with ID: {userid} with unix: {time}")
        await f.write(dumps(data, indent=4))