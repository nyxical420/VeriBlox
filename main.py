import discord
import discord.ui as ui
import discord.ext.commands as commands
from discord.app_commands import CommandTree

import requests
import aiofiles
import traceback
import time as btime
from os import getenv
from shutil import copy
from asyncio import sleep
from os.path import getsize
from json import loads, dumps
from dotenv import load_dotenv
from random import choice, randint
from datetime import datetime, date, time
from simplejson.errors import JSONDecodeError

from packages.DataEdit import *
from packages.Logging import log
from packages.RateLimitTool import *
from packages.HookLogging import sendLog
from packages.RobloxAPI import getInfo, getMembership
load_dotenv("./conf/.env")

users = {}

# Testing Toggle for Testing Veriblox
testing = False

if testing == True:
    log("VeriBlox is Running on Test Mode!")

def gen():
    words = open(r"conf/verification.txt", "r").read().splitlines()
    code = ""

    for x in range(randint(4, 20)):
        code += choice(words)
        if x != 11: code += " "
    
    return code

class VeriBloxVerification(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label='Code Verification', style=discord.ButtonStyle.green, custom_id="persistent_view:codeverification")
    async def codeverification(self, interaction: discord.Interaction, button: ui.Button):
        class verificationModal(ui.Modal, title="VeriBlox Verification"):
            userID = interaction.user.id
            guildID = interaction.guild.id
            userName = ui.TextInput(label="Roblox Username", style=discord.TextStyle.short, min_length=3, max_length=20)

            async def on_submit(self, interaction: discord.Interaction):
                await interaction.response.defer(thinking=True, ephemeral=True)
                robloxUser = getInfo(str(self.userName), True)

                if robloxUser["success"] == False:
                    return await interaction.followup.send(content="**🚫 | This Roblox Account doesn't appear to exist!**", ephemeral=True)

                view = ui.View()
                getCode = ui.Button(label="Get Code", style=discord.ButtonStyle.green)
                genCode = ui.Button(label="Regenerate Code", style=discord.ButtonStyle.grey)
                verify  = ui.Button(label="Verify Account", style=discord.ButtonStyle.green)

                robloxUser = getInfo(robloxUser["id"])
                robloxID = robloxUser["id"]

                if getGuildData(self.guildID)[7] != 0:
                    if not getMembership(robloxUser):
                        return await interaction.followup.send(content=f"**🚫 | You are required to have a Roblox Premium Membership to join {interaction.guild.name}!**")

                if robloxUser["banned"] == True:
                    return await interaction.followup.send(content=f"**🚫 | This Roblox Account appears to be banned.**")

                try:
                    if robloxID in getGuildData(self.guildID)[2]:
                        return await interaction.followup.send(content="**🚫 | This Roblox Account appears to be banned from this server.**")
                except:
                    pass

                if not self.userID in getUserList():
                    addUserData(self.userID)
                    editUserData(self.userID, '"RobloxID"', f'{robloxUser["id"]}')
                    editUserData(self.userID, '"VerifyCode"', f'"{gen()}"')

                async def getVerificationCode(interaction: discord.Interaction):
                    vs = getUserData(self.userID)
                    class verificationCode(ui.Modal, title="VeriBlox Verification Code"):
                        robloxVerificationCode = ui.TextInput(label="Verification Code", style=discord.TextStyle.long, default=vs[2])

                        async def on_submit(self, interaction: discord.Interaction):
                            await interaction.response.defer()

                    await interaction.response.send_modal(verificationCode())

                async def regenVerificationCode(interaction: discord.Interaction):
                    editUserData(self.userID, '"VerifyCode"', f'"{gen()}"')
                    genCode.label = "Regenerate Code"
                    genCode.style = discord.ButtonStyle.red
                    genCode.disabled = True
                    await interaction.response.edit_message(view=view)
                    await sleep(30)
                    genCode.style = discord.ButtonStyle.grey
                    genCode.disabled = False
                    await interaction.edit_original_response(view=view)

                async def verifyUser(interaction: discord.Interaction):
                    vs = getUserData(self.userID)
                    gs = getGuildData(self.guildID)
                    robloxUser = getInfo(str(self.userName), True)
                    
                    robloxDescription = robloxUser["description"]
                    userVerifyCode = vs[2]
                    if robloxDescription.__contains__(userVerifyCode):
                        try:
                            try:
                                creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                            except:
                                creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                        except:
                            creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

                        if gs[5] != 0:
                            if round(btime.time()) - creationDate < gs[5]:
                                return await interaction.response.send_message(content="**🚫 | This Roblox Account is not Elegible to be in this server. Please use another Roblox Account that's older than this Roblox Account!**")

                        if gs[7] != 0:
                            if getMembership(robloxUser):
                                if gs[8] != 0:
                                    try: role = discord.utils.get(interaction.guild.roles, id=gs[8])
                                    except: pass

                                    try: await interaction.user.add_roles(role)
                                    except: pass

                        try:
                            role = discord.utils.get(interaction.guild.roles, id=gs[1])
                        except:
                            return await interaction.response.send_message(content="**🚫 | There was an Error while finding the Verified Role in this server.**", ephemeral=True)

                        try:
                            await interaction.user.add_roles(role)
                        except:
                            return await interaction.response.send_message(content="**🚫 | I couldn't give you the Verified Role since the role is higher than my Role Position. or i don't have the proper permission to give you one.**", ephemeral=True)

                        if interaction.guild.me.guild_permissions.manage_nicknames:
                            robloxUserName = robloxUser["username"]
                            robloxDisplayName = robloxUser["displayname"]

                            if interaction.user.id == interaction.guild.owner_id:
                                pass
                            
                            try:
                                if robloxUserName == robloxDisplayName:
                                    await interaction.user.edit(nick=robloxDisplayName)
                                else:
                                    if len(robloxUserName + robloxDisplayName) >= 32:
                                        await interaction.user.edit(nick=robloxUserName)
                                    else:
                                        await interaction.user.edit(nick=f"{robloxDisplayName} - @{robloxUserName}")
                            except: pass

                            editUserData(self.userID, '"isVerified"', '"True"')
                            editUserData(self.userID, '"VerifyCode"', f'"{gen()}"')

                            if gs[2] != "":
                                await interaction.user.send(f"Message from **{interaction.guild.name}**\n" + gs[2])

                            if interaction.user.id == interaction.guild.owner_id:
                                embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                                await interaction.response.edit_message(content=None, embed=embed, view=None)
                            else:
                                embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!")
                                await interaction.response.edit_message(content=None, embed=embed, view=None)

                    else:
                        return await interaction.response.send_message(content="**🚫 | Looks like you havent pasted the code in your Roblox Description. Please paste it and try again!**", ephemeral=True)

                addUserData(interaction.user.id)
                getCode.callback = getVerificationCode
                genCode.callback = regenVerificationCode
                verify.callback = verifyUser
                view.add_item(getCode)
                view.add_item(genCode)
                view.add_item(verify)
                robloxUserName = robloxUser["username"]
                robloxDisplayName = robloxUser["displayname"]
                await interaction.followup.send(content=f"**Account Found!** Verifying as **{robloxUserName} ({robloxDisplayName}**)\n> You can only regenerate your verification code once every **30 seconds**.", view=view, ephemeral=True)
            
        await interaction.response.send_modal(verificationModal())

    @ui.button(label='Game Verification', style=discord.ButtonStyle.green, custom_id="persistent_view:gameverification")
    async def gameverification(self, interaction: discord.Interaction, button: ui.Button):
        class verificationModal(ui.Modal, title="VeriBlox Verification"):
            userID = interaction.user.id
            guildID = interaction.guild.id
            userName = ui.TextInput(label="Roblox Username", style=discord.TextStyle.short, min_length=3, max_length=20)

            async def on_submit(self, interaction: discord.Interaction):
                view = ui.View(timeout=900)
                await interaction.response.defer(thinking=True, ephemeral=True)

                game = ui.Button(label="Join Game", style=discord.ButtonStyle.url, url="https://www.roblox.com/games/9728176745/VeriBlox-Verification")
                status = ui.Button(label="Waiting for Verification...", style=discord.ButtonStyle.red, disabled=True)
                cancel = ui.Button(label="Cancel", style=discord.ButtonStyle.red)

                embed = discord.Embed(title="Game Verification", description=f"**Verifying as: {robloxUserName} ({robloxDisplayName})**\nTo verify, Please Click **Join Game** and wait for Automatic Verification!")
                
                maxTries = 300
                
                async def cancelVerification(interaction: discord.Interaction):
                    global maxTries
                    await interaction.response.defer()
                    
                    maxTries = 0
                    await interaction.edit_original_response(content="Cancelled Game Verification.", embed=None, view=None)

                serverurl = getenv("serverurl")
                robloxUser = getInfo(str(self.userName), True)
                requests.get(serverurl + "adduser?user=" + str(robloxUser["username"]), verify=False)

                view.add_item(game)
                view.add_item(status)
                cancel.callback = cancelVerification
                await interaction.followup.send(embed=embed, view=view)

                while maxTries != 0:
                    try: data = requests.get(serverurl + "showvdata").json()
                    except JSONDecodeError: data = requests.get(serverurl + "showvdata").json()

                    if str(data).__contains__(robloxUser["username"]):
                        requests.get(serverurl + "deluser?user=" + robloxUser["username"] + "&ver=True").json()
                        status.label = "Verifying Account..."
                        status.style = discord.ButtonStyle.grey
                        await interaction.edit_original_response(embed=embed, view=view)

                        gs = getGuildData(self.guildID)
                        robloxUser = getInfo(str(self.userName), True)

                        try:
                            try:
                                creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                            except:
                                creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                        except:
                            creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

                        if gs[5] != 0:
                            if round(btime.time()) - creationDate < gs[5]:
                                return await interaction.response.send_message(content="**🚫 | This Roblox Account is not Elegible to be in this server. Please use another Roblox Account that's older than this Roblox Account!**")

                        if gs[7] != 0:
                            if getMembership(robloxUser):
                                if gs[8] != 0:
                                    try: role = discord.utils.get(interaction.guild.roles, id=gs[8])
                                    except: pass

                                    try: await interaction.user.add_roles(role)
                                    except: pass

                        try:
                            role = discord.utils.get(interaction.guild.roles, id=gs[1])
                        except:
                            return await interaction.response.send_message(content="**🚫 | There was an Error while finding the Verified Role in this server.**", ephemeral=True)

                        try:
                            await interaction.user.add_roles(role)
                        except:
                            return await interaction.response.send_message(content="**🚫 | I couldn't give you the Verified Role since the role is higher than my Role Position. or i don't have the proper permission to give you one.**", ephemeral=True)

                        if interaction.guild.me.guild_permissions.manage_nicknames:
                            robloxUserName = robloxUser["username"]
                            robloxDisplayName = robloxUser["displayname"]

                            if interaction.user.id == interaction.guild.owner_id:
                                pass
                            
                            try:
                                if robloxUserName == robloxDisplayName:
                                    await interaction.user.edit(nick=robloxDisplayName)
                                else:
                                    if len(robloxUserName + robloxDisplayName) >= 32:
                                        await interaction.user.edit(nick=robloxUserName)
                                    else:
                                        await interaction.user.edit(nick=f"{robloxDisplayName} - @{robloxUserName}")
                            except: pass

                            editUserData(self.userID, '"isVerified"', '"True"')
                            editUserData(self.userID, '"VerifyCode"', f'"{gen()}"')

                            if gs[2] != "":
                                await interaction.user.send(f"Message from **{interaction.guild.name}**\n" + gs[2])

                            if interaction.user.id == interaction.guild.owner_id:
                                embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                                await interaction.edit_original_response(content=None, embed=embed, view=None)
                            else:
                                embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!")
                                await interaction.edit_original_response(content=None, embed=embed, view=None)
                            break

                    else:
                        maxTries -= 1
                        await sleep(1)
                
                if maxTries == 0:
                    embed = discord.Embed(title="Game Verification", description="Game Verification reached Timeout.\nMax Requests has been reached. (300)")
                    await interaction.edit_original_response()

        await interaction.response.send_modal(verificationModal())            

class vbTree(CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        try: editUserData(interaction.user.id, '"dataExpiration"', '60')
        except: pass

        async with aiofiles.open(r"data/ratelimited.json", "r") as f:
            blacklist = loads(await f.read())
        
        if not str(interaction.user.id) in users:
            users[str(interaction.user.id)] = 0

        if users[str(interaction.user.id)] >= 11:
            if str(interaction.user.id) in users:
                await ratelimitUser(str(interaction.user.id), round(datetime.now().timestamp()) + 1800)
                del users[str(interaction.user.id)]
                sendLog(f"Ratelimited user: {interaction.user} ({interaction.user.id})")

        async with aiofiles.open(r"data/ratelimited.json", "r") as f:
            data = loads(await f.read())

        if not str(interaction.user.id) in data:
            users[str(interaction.user.id)] += 1

        if str(interaction.user.id) in blacklist:
            log(interaction.command.name)
            time = getrtTime(str(interaction.user.id))
            embed = discord.Embed(title="VeriBlox Blacklist", description=f"You have been Blacklisted from using VeriBlox Commands to prevent spam.\nYou can run commands again <t:{time}:R>. Please avoid spamming commands.", color=0x2F3136)
            await interaction.response.send_message(embed=embed)
            return False
        
        return True

class VeriBlox(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(command_prefix=[], intents=intents, tree_cls=vbTree, activity=discord.Game("Starting VeriBlox..."))

    async def setup_hook(self) -> None:
        self.add_view(VeriBloxVerification())
        await bot.load_extension("commands.context")
        await bot.load_extension("commands.help")
        await bot.load_extension("commands.server")
        await bot.load_extension("commands.user")

        await bot.load_extension("background.malblock")
        await bot.load_extension("background.autoverify")
        log("VeriBlox Cogs Loaded!")

    async def on_message(self, message: discord.Message):
        if bot.user.mentioned_in(message):
            if message.author == bot.user: return
            if message.author.bot: return

            msg = message.content

            if msg.startswith("@everyone"): return
            if msg.startswith("@here"): return
            
            if msg.startswith(f"<@{bot.user.id}>"):
                try:
                    if msg.split()[1] == "load":
                        if message.author.id == 583200866631155714:
                            try:
                                await bot.unload_extension(f"{msg.split()[2]}")
                                log(f"Cog {msg.split()[2]} loaded!")
                                await message.channel.send(content=f"Cog {msg.split()[2]} loaded!")
                            except:
                                log(f"Cog {msg.split()[2]} failed to load.")
                                await message.channel.send(content=f"Failed to Load Cog: {msg.split()[2]}!")

                    if msg.split()[1] == "unload":
                        if message.author.id == 583200866631155714:
                            try:
                                await bot.unload_extension(f"{msg.split()[2]}")
                                log(f"Cog {msg.split()[2]} unloaded!")
                                await message.channel.send(content=f"Cog {msg.split()[2]} unloaded!")
                            except:
                                log(f"Cog {msg.split()[2]} failed to unload.")
                                await message.channel.send(content=f"Failed to Unload Cog: {msg.split()[2]}!")

                    if msg.split()[1] == "reload":
                        if message.author.id == 583200866631155714:
                            await bot.unload_extension("commands.context")
                            await bot.unload_extension("commands.help")
                            await bot.unload_extension("commands.server")
                            await bot.unload_extension("commands.user")
                            await bot.unload_extension("background.malblock")
                            await bot.unload_extension("background.autoverify")

                            await bot.load_extension("commands.context")
                            await bot.load_extension("commands.help")
                            await bot.load_extension("commands.server")
                            await bot.load_extension("commands.user")
                            await bot.load_extension("background.malblock")
                            await bot.load_extension("background.autoverify")

                            try:
                                if msg.split()[2] == "sync":
                                    await bot.tree.sync()
                                    log("VeriBlox Commands Synced!")
                                    await message.channel.send(content="Commands Synced!")
                            except:
                                pass
                            
                            log("VeriBlox Cogs Reloaded!")
                            await message.channel.send(content="All Cogs Reloaded!")
                except:
                    await message.channel.send(f"Hello! I'm {bot.user.mention}! for commands, type in `/help`! `{round(bot.latency * 1000)}ms`")

    async def on_guild_join(self, guild: discord.Guild):
        if not guild.id in getGuildList(): addGuildData(guild.id)
        else: pass

        log(f"VeriBlox has been invited to {guild.name} ({guild.member_count} Members). VeriBlox is now in {len(bot.guilds):,} Guilds!")

    async def on_ready(self):
        async def updateActivity():
            while True:
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds):,} Servers | /help"))
                await sleep(30)
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.users):,} Users | /help"))
                await sleep(30)
        
        async def missingDataDump():
            while True:
                for guild in bot.guilds:
                    if not guild.id in getGuildList():
                        addGuildData(guild.id)
                        log(f"Added guild data for {guild.name} ({guild.id})")
                    else:
                        pass

                await sleep(300)

        async def purgeUserData():
            previousDate = 0
            currentDate = date.today().strftime("%d")
            previousDate = currentDate

            while True:
                currentDate = date.today().strftime("%d")            
                if currentDate != previousDate:
                    for x in getUserList():
                        if getUserData(x)[4] == 0:
                            deleteUserData(x)
                            log(f"UserDataPurge: Data for {x} has been Deleted.")

                        if getUserData(x)[4] != 0:
                            editUserData(x, '"dataExpiration"', f'"{getUserData(x)[4] - 1}"')

                    previousDate = currentDate

                await sleep(1800)
        
        async def purgeGuildData():
            while True:
                guildList = [guild.id for guild in bot.guilds]

                for x in getGuildList():
                    if not guildList.count(int(x)):
                        deleteGuildData(x)
                        log(f"GuildDataPurge: Data for {x} has been Deleted.")

                await sleep(1800)
                
        async def removeTempRT():
            while True:
                async with aiofiles.open(r"data/ratelimited.json", "r") as f:
                    data = loads(await f.read())

                for x in data:
                    async with aiofiles.open(r"data/ratelimited.json", "r") as f:
                        data = loads(await f.read())
                    
                    if round(datetime.now().timestamp()) >= data[str(x)]["ratelimitTime"]:
                        del data[str(x)]
                    
                    async with aiofiles.open(r"data/ratelimited.json", "w") as f:
                        f.write(dumps(data, indent=4))
                
                await sleep(0.5)

        async def resetTempRT():
            while True:
                users.clear()
                await sleep(60)

        async def clearAllUsers():
            while True:
                serverurl = getenv("serverurl")
                requests.get(serverurl + "delall", verify=False)
                await sleep(14400)

        async def createBackupData():
            while True:
                copy(r"./data/data.db", r"./data/backup")

                log("Created Backup Data!")
                await sleep(14400)

        async def autoCogReloader():
            log("AutoCogReloader: Creating bytes list...")
            fileSizes = [0, 0, 0, 0]
            fileSizes_bg = [0, 0]
            
            log("AutoCogReloader: Reading Cogs Size...")
            ctxSize = getsize(r"./commands/context.py")
            helpSize = getsize(r"./commands/help.py")
            serverSize = getsize(r"./commands/server.py")
            userSize = getsize(r"./commands/user.py")
            autoverifySize = getsize(r"./background/autoverify.py")
            malblockSize = getsize(r"./background/malblock.py")
            
            log("AutoCogReloader: Appending bytes...")
            fileSizes[0] = ctxSize
            fileSizes[1] = helpSize
            fileSizes[2] = serverSize
            fileSizes[3] = userSize
            fileSizes_bg[0] = autoverifySize
            fileSizes_bg[1] = malblockSize

            log("AutoCogReloader: Started!")
            while True:
                ctxSize = getsize(r"./commands/context.py")
                helpSize = getsize(r"./commands/help.py")
                serverSize = getsize(r"./commands/server.py")
                userSize = getsize(r"./commands/user.py")
                autoverifySize = getsize(r"./background/autoverify.py")
                malblockSize = getsize(r"./background/malblock.py")

                if fileSizes[0] != ctxSize:
                    await sleep(2)
                    await bot.unload_extension("commands.context")
                    await bot.load_extension("commands.context")
                    fileSizes[0] = ctxSize
                    log("AutoCogReloader: Reloaded Context Menu Cog!")

                if fileSizes[1] != helpSize:
                    await sleep(2)
                    await bot.unload_extension("commands.help")
                    await bot.load_extension("commands.help")
                    fileSizes[1] = helpSize
                    log("AutoCogReloader: Reloaded Help Cog!")

                if fileSizes[2] != serverSize:
                    await sleep(2)
                    await bot.unload_extension("commands.server")
                    await bot.load_extension("commands.server")
                    fileSizes[2] = serverSize
                    log("AutoCogReloader: Reloaded Server Cog!")

                if fileSizes[3] != userSize:
                    await sleep(2)
                    await bot.unload_extension("commands.user")
                    await bot.load_extension("commands.user")
                    fileSizes[3] = userSize
                    log("AutoCogReloader: Reloaded User Cog!")

                if fileSizes_bg[0] != autoverifySize:
                    await sleep(2)
                    await bot.unload_extension("background.autoverify")
                    await bot.load_extension("background.autoverify")
                    fileSizes_bg[0] = autoverifySize
                    log("AutoCogReloader: Reloaded AutoVerification Background Cog!")

                if fileSizes_bg[1] != malblockSize:
                    await sleep(2)
                    await bot.unload_extension("background.malblock")
                    await bot.load_extension("background.malblock")
                    fileSizes_bg[1] = malblockSize
                    log("AutoCogReloader: Reloaded MalBlock Background Cog!")

                await sleep(1)

        bot.loop.create_task(clearAllUsers())
        bot.loop.create_task(updateActivity())
        bot.loop.create_task(autoCogReloader())

        if testing == False:
            bot.loop.create_task(purgeUserData())
            bot.loop.create_task(purgeGuildData())
            bot.loop.create_task(createBackupData())
            bot.loop.create_task(missingDataDump())
            
        bot.loop.create_task(removeTempRT())
        bot.loop.create_task(resetTempRT())

        await bot.tree.sync()
        log("VeriBlox Ready!")
        sendLog(f"VeriBlox Ready!\n```\nShard Count: {bot.shard_count}\nServer Count: {len(bot.guilds):,}\nUser Count: {len(bot.users):,}\n```")

bot = VeriBlox()

@bot.tree.command(name="verify", description="Verifies your Discord Account with your Roblox Account on VeriBlox")
async def verify(interaction : discord.Interaction):
    class verificationModal(ui.Modal, title="VeriBlox Verification"):
        userID = interaction.user.id
        guildID = interaction.guild.id
        userName = ui.TextInput(label="Roblox Username", style=discord.TextStyle.short, min_length=3, max_length=20)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(thinking=True, ephemeral=True)
            robloxUser = getInfo(str(self.userName), True)

            if robloxUser["success"] == False:
                return await interaction.followup.send(content="**🚫 | This Roblox Account doesn't appear to exist!**", ephemeral=True)

            view = ui.View()
            getCode = ui.Button(label="Get Code", style=discord.ButtonStyle.green)
            genCode = ui.Button(label="Regenerate Code", style=discord.ButtonStyle.grey)
            verify  = ui.Button(label="Verify Account", style=discord.ButtonStyle.green)

            robloxUser = getInfo(robloxUser["id"])
            robloxID = robloxUser["id"]

            if getGuildData(self.guildID)[7] != 0:
                if not getMembership(robloxUser):
                    return await interaction.followup.send(content=f"**🚫 | You are required to have a Roblox Premium Membership to join {interaction.guild.name}!**")

            if robloxUser["banned"] == True:
                return await interaction.followup.send(content=f"**🚫 | This Roblox Account appears to be banned.**")

            try:
                if robloxID in getGuildData(self.guildID)[2]:
                    return await interaction.followup.send(content="**🚫 | This Roblox Account appears to be banned from this server.**")
            except:
                pass

            if not self.userID in getUserList():
                addUserData(self.userID)
                editUserData(self.userID, '"RobloxID"', f'{robloxUser["id"]}')
                editUserData(self.userID, '"VerifyCode"', f'"{gen()[:-1]}"')

            async def getVerificationCode(interaction: discord.Interaction):
                vs = getUserData(self.userID)
                class verificationCode(ui.Modal, title="VeriBlox Verification Code"):
                    robloxVerificationCode = ui.TextInput(label="Verification Code", style=discord.TextStyle.long, default=vs[2])

                    async def on_submit(self, interaction: discord.Interaction):
                        await interaction.response.defer()

                await interaction.response.send_modal(verificationCode())

            async def regenVerificationCode(interaction: discord.Interaction):
                editUserData(self.userID, '"VerifyCode"', f'"{gen()[:-1]}"')
                genCode.label = "Regenerate Code"
                genCode.style = discord.ButtonStyle.red
                genCode.disabled = True
                await interaction.response.edit_message(view=view)
                await sleep(30)
                genCode.style = discord.ButtonStyle.grey
                genCode.disabled = False
                await interaction.edit_original_response(view=view)

            async def verifyUser(interaction: discord.Interaction):
                vs = getUserData(self.userID)
                gs = getGuildData(self.guildID)
                robloxUser = getInfo(str(self.userName), True)

                robloxDescription = robloxUser["description"]
                userVerifyCode = vs[2]
                if robloxDescription.__contains__(userVerifyCode):
                    try:
                        try:
                            creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                        except:
                            creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                    except:
                        creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

                    if gs[5] != 0:
                        if round(btime.time()) - creationDate < gs[5]:
                            return await interaction.response.send_message(content="**🚫 | This Roblox Account is not Elegible to be in this server. Please use another Roblox Account that's older than this Roblox Account!**")

                    if gs[7] != 0:
                        if getMembership(robloxUser):
                            if gs[8] != 0:
                                try: role = discord.utils.get(interaction.guild.roles, id=gs[8])
                                except: pass

                                try: await interaction.user.add_roles(role)
                                except: pass

                    try:
                        role = discord.utils.get(interaction.guild.roles, id=gs[1])
                    except:
                        return await interaction.response.send_message(content="**🚫 | There was an Error while finding the Verified Role in this server.**", ephemeral=True)

                    try:
                        await interaction.user.add_roles(role)
                    except:
                        return await interaction.response.send_message(content="**🚫 | I couldn't give you the Verified Role since the role is higher than my Role Position. or i don't have the proper permission to give you one.**", ephemeral=True)

                    if interaction.guild.me.guild_permissions.manage_nicknames:
                        robloxUserName = robloxUser["username"]
                        robloxDisplayName = robloxUser["displayname"]

                        if interaction.user.id == interaction.guild.owner_id:
                            pass
                        
                        try:
                            if robloxUserName == robloxDisplayName:
                                await interaction.user.edit(nick=robloxDisplayName)
                            else:
                                if len(robloxUserName + robloxDisplayName) >= 32:
                                    await interaction.user.edit(nick=robloxUserName)
                                else:
                                    await interaction.user.edit(nick=f"{robloxDisplayName} - @{robloxUserName}")
                        except: pass

                        editUserData(self.userID, '"isVerified"', '"True"')
                        editUserData(self.userID, '"VerifyCode"', f'"{gen()[:-1]}"')

                        if gs[2] != "":
                            await interaction.user.send(f"Message from **{interaction.guild.name}**\n" + gs[2])

                        if interaction.user.id == interaction.guild.owner_id:
                            embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                            await interaction.response.edit_message(content=None, embed=embed, view=None)
                        else:
                            embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!")
                            await interaction.response.edit_message(content=None, embed=embed, view=None)

                else:
                    return await interaction.response.send_message(content="**🚫 | Looks like you havent pasted the code in your Roblox Description. Please paste it and try again!**", ephemeral=True)

            addUserData(interaction.user.id)
            getCode.callback = getVerificationCode
            genCode.callback = regenVerificationCode
            verify.callback = verifyUser
            view.add_item(getCode)
            view.add_item(genCode)
            view.add_item(verify)
            robloxUserName = robloxUser["username"]
            robloxDisplayName = robloxUser["displayname"]
            await interaction.followup.send(content=f"**Account Found!** Verifying as **{robloxUserName} ({robloxDisplayName}**)\n> You can only regenerate your verification code once every **30 seconds**.", view=view, ephemeral=True)

    if getUserData(interaction.user.id):
        if getUserData(interaction.user.id)[3] == "True":
            userID = str(interaction.user.id)
            guildID = str(interaction.guild.id)
            gs = getGuildData(guildID)
            robloxUser = getInfo(int(getUserData(interaction.user.id)[1]), True)

            try:
                try:
                    creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                except:
                    creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            except:
                creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

            if gs[5] != 0:
                if time() - creationDate < gs[5]:
                    return await interaction.response.send_message(content="**🚫 | This Roblox Account is not Elegible to be in this server. Please use another Roblox Account that's older than this Roblox Account!**")

            try:
                role = discord.utils.get(interaction.guild.roles, id=gs[1])
            except:
                return await interaction.response.send_message(content="**🚫 | There was an Error while finding the Verified Role in this server.**")

            try:
                await interaction.user.add_roles(role)
            except:
                return await interaction.response.send_message(content="**🚫 | I couldn't give you the Verified Role since the role is higher than my Role Position. or i don't have the proper permission to give you one.**")

            if interaction.guild.me.guild_permissions.manage_nicknames:
                robloxUserName = robloxUser["username"]
                robloxDisplayName = robloxUser["displayname"]

                if interaction.user.id == interaction.guild.owner_id:
                    pass
                
                try:
                    if robloxUserName == robloxDisplayName:
                        await interaction.user.edit(nick=robloxDisplayName)
                    else:
                        if len(robloxUserName + robloxDisplayName) >= 32:
                            await interaction.user.edit(nick=robloxUserName)
                        else:
                            await interaction.user.edit(nick=f"{robloxDisplayName} - @{robloxUserName}")
                except: pass
                
                editUserData(userID, '"isVerified"', '"True"')
                editUserData(userID, '"RobloxID"', f'{robloxUser["id"]}')
                editUserData(userID, '"VerifyCode"', f'"{gen()[:-1]}"')

                if gs[2] != "":
                    await interaction.user.send(f"Message from **{interaction.guild.name}**\n" + gs[2])

                if interaction.user.id == interaction.guild.owner_id:
                    embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                    await interaction.response.edit_message(content=None, embed=embed, view=None)
                else:
                    embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!")
                    await interaction.response.edit_message(content=None, embed=embed, view=None)
        else:
            await interaction.response.send_modal(verificationModal())

    else:
        await interaction.response.send_modal(verificationModal())

@bot.tree.command(name="setup", description="Creates a verification channel")
@discord.app_commands.describe(verifiedrole = "The role you want to be set as verified role")
async def setup(interaction: discord.Interaction, verifiedrole : discord.Role):
    gs = getGuildData(interaction.guild.id)

    if not interaction.guild:
        embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**")
        return await interaction.response.send_message(embed=embed)

    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(content="**⚠️ | You don't have proper permission to do that!\nPermission Needed: ``manage_channels`**`", ephemeral=True)

    if verifiedrole == interaction.guild.default_role:
        return await interaction.response.send_message(content="**🚫 | You can't set the Verified Role as the default role! (@everyone)**", ephemeral=True)
    
    guild = bot.get_guild(interaction.guild.id)
    verified = discord.utils.get(interaction.guild.roles, id=verifiedrole.id)

    try:
        editGuildData(interaction.guild.id, '"VerifiedRole"', f'{verifiedrole.id}')
    except KeyError:
        addGuildData(interaction.guild.id)
        editGuildData(interaction.guild.id, '"VerifiedRole"', f'{verifiedrole.id}')

    category = await guild.create_category("VeriBlox Verification")
    verifychannel = await guild.create_text_channel('verify', category=category)
    embed = discord.Embed(title="VeriBlox Verification", description="This server is a **Roblox Server**. to verify, you will need an **Roblox Account** to verify your **Discord Account** to gain full access to this server!\nFor verification instructions, [click here]().")
    embed_code = discord.Embed(title="VeriBlox Code Verification", description="**Step 1**: Click on **Code Verification** and type in your **Roblox Username** and click on **Submit**\n**Step 2**: Click on **Get Code** and go to your **Roblox Profile Page** and place the verification code in your **Roblox Description / About Me**\n**Step 3**: Click on **Verify Account** to gain full access to this server!")
    embed_game = discord.Embed(title="VeriBlox Game Verification", description="**Step 1**: Click on **Game Verification** and type in your **Roblox Username** and click on **Submit**\n**Step 2**: Visit the Verification Game and wait for Verification\n**Step 3**: Click on **Continue Verification** to gain full access to this server!")
    await verifychannel.send(embeds=[embed, embed_code, embed_game], view=VeriBloxVerification())

    overwrite = discord.PermissionOverwrite()
    overwrite.view_channel = False
    overwritedefault = discord.PermissionOverwrite()
    overwritedefault.view_channel = True
    overwritedefault.send_messages = False
    await category.set_permissions(verified, overwrite=overwrite)
    await category.set_permissions(guild.default_role, overwrite=overwritedefault)
    await interaction.response.send_message(content="**✅ | Verification channel created! to change the verified role, use the command** ``/config verifiedrole``.\nMake sure the verified role is below my role to fully verify a user!", ephemeral=True)

@bot.tree.error
async def on_command_error(interaction: discord.Interaction, error: Exception):
    embed = discord.Embed()

    if isinstance(error, discord.app_commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)

        if int(h) == 0 and int(m) == 0:
            embed.description = f"**⏱️ | `/{interaction.command.name}` is currently on cooldown. Please try again in {int(s)} seconds.**"
        elif int(h) == 0 and int(m) != 0:
            embed.description = f"**⏱️ | `/{interaction.command.name}` is currently on cooldown. Please try again in {int(m)} minutes and {int(s)} seconds.**"
        else:
            embed.description = f"**⏱️ | `/{interaction.command.name}` is currently on cooldown. Please try again in {int(h)} hours and {int(m)} minutes.**"
        
    if isinstance(error, discord.app_commands.errors.CommandInvokeError):
        error = error.original
        log(error, 1)
        embed.description = "**⚠️ | There was an error while running this command.**"

    try: await interaction.response.send_message(embed=embed, ephemeral=True)
    except: pass
    
    etype = type(error)
    trace = error.__traceback__
    lines = traceback.format_exception(etype, error, trace)
    traceback_text = ''.join(lines)
    sendLog(f"```cmd\n{traceback_text}\n```", True)
    raise error

if testing == False:    
    token = getenv("token")
else:
    token = getenv("testtoken")

bot.run(token)
