import discord
import discord.ui as ui
import discord.ext.commands as commands
from discord.app_commands import CommandTree

import topgg
import httpx
import aiofiles
import traceback
import time as btime
from os import getenv
from asyncio import sleep
from os.path import getsize
from json import loads, dumps
from datetime import datetime
from dotenv import load_dotenv
from random import choice, randint
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
if testing == True: log("VeriBlox is Running on Test Mode!")

def gen():
    words = open(r"conf/verification.txt", "r").read().splitlines()
    code = ""
    n = randint(4, 13)

    for x in range(n):
        code += choice(words).replace(" ", "")
        if x != n - 1: code += " "
    
    return code

class VeriBloxVerification(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label='Code Verification', style=discord.ButtonStyle.green, custom_id="persistent_view:codeverification")
    async def codeverification(self, interaction: discord.Interaction, button: ui.Button):
        class verificationModal(ui.Modal, title="VeriBlox Code Verification"):
            userID = interaction.user.id
            guildID = interaction.guild.id
            userName = ui.TextInput(label="Roblox Username", style=discord.TextStyle.short, min_length=3, max_length=20)

            async def on_submit(self, interaction: discord.Interaction):
                await interaction.response.defer(thinking=True, ephemeral=True)
                robloxUser = getInfo(str(self.userName), True)

                if robloxUser["success"] == False:
                    embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                    embed.description = "The Roblox Account your attempting to verify as doesn't appear to exist. Please check for any Typo in your Roblox Username!"
                    return await interaction.followup.send(embed=embed, ephemeral=True)

                view = ui.View()
                getCode = ui.Button(label="Get Code", style=discord.ButtonStyle.green)
                genCode = ui.Button(label="Regenerate Code", style=discord.ButtonStyle.grey)
                verify  = ui.Button(label="Verify Account", style=discord.ButtonStyle.green)
                robloxID = robloxUser["id"]

                #if getGuildData(self.guildID)[7] != 0:
                #    if not getMembership(robloxUser):
                #        embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                #        embed.description = "Your Roblox Account requires a Roblox Premium Membership to be verified on this server."
                #        return await interaction.followup.send(embed=embed, ephemeral=True)

                if robloxUser["banned"] == True:
                    embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                    embed.description = "The Roblox Account your attempting to verify as appears to be banned. Please use another Roblox Account!"
                    return await interaction.followup.send(embed=embed, ephemeral=True)

                if str(getGuildData(self.guildID)[2]).__contains__(str(robloxID)):
                    embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                    embed.description = "Your Roblox Account appears to be banned in this server."
                    return await interaction.followup.send(embed=embed)

                gs = getGuildData(self.guildID)

                try:
                    try: creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                    except: creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                except: creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

                if gs[5] != 0:
                    if round(btime.time()) - creationDate < gs[5]:
                        embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                        embed.description = "Your Roblox Account is not old enough to be Verified in this server. please Retry Verification by using an older account!"
                        return await interaction.response.send_message(embed=embed, ephemeral=True)

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
                            role = discord.utils.get(interaction.guild.roles, id=gs[1])
                        except:
                            embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                            embed.description = "There was an unexpected error while getting the Verified Role for this Server. please Retry Verification!"
                            return await interaction.response.send_message(embed=embed, ephemeral=True)

                        try:
                            await interaction.user.add_roles(role)
                        except discord.Forbidden:
                            embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                            embed.description = "I couldn't Verify you in the Server since i don't have the proper permission to give you one. Please contact a Server Moderator who can fix this issue and Retry Verification!"
                            return await interaction.response.send_message(embed=embed, ephemeral=True)
                        except discord.HTTPException:
                            embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                            embed.description = "There was an error that wouldn't allow me to give you the Verified Role. please Retry Verification!"
                            return await interaction.response.send_message(embed=embed, ephemeral=True)
                        except:
                            embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                            embed.description = "There was an unexpected error while giving you the Verified Role for this server. please Retry Verification!"
                            return await interaction.response.send_message(embed=embed)

                        #if gs[7] != 0:
                        #    if getMembership(robloxUser):
                        #        if gs[8] != 0:
                        #            try: role = discord.utils.get(interaction.guild.roles, id=gs[8])
                        #            except: pass

                        #            try: await interaction.user.add_roles(role)
                        #            except: pass

                        if interaction.guild.me.guild_permissions.manage_nicknames:
                            nameFormat = getGuildData(interaction.guild.id)[9]
                            robloxUserName = robloxUser["username"]
                            robloxDisplayName = robloxUser["displayname"]
                            robloxUserId = robloxUser["id"]

                            nameFormat = nameFormat.replace("<robloxUsername>", robloxUserName)
                            nameFormat = nameFormat.replace("<robloxDisplay>", robloxDisplayName)
                            nameFormat = str(nameFormat).replace("<robloxId>", str(robloxUserId))
                            nameFormat = nameFormat.replace("<discordUsername>", interaction.user.name)

                            if interaction.user.id == interaction.guild.owner_id: pass
                            
                            try:
                                if len(nameFormat) >= 33: await interaction.user.edit(nick=robloxUserName)
                                else: await interaction.user.edit(nick=nameFormat)
                            except: pass

                            editUserData(self.userID, '"isVerified"', '"True"')
                            editUserData(self.userID, '"VerifyCode"', f'"{gen()}"')

                            if gs[2] != "":
                                await interaction.user.send(f"Message from **{interaction.guild.name}**\n" + gs[2])

                            if interaction.user.id == interaction.guild.owner_id:
                                embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.", color=0x2F3136)
                                await interaction.response.edit_message(content=None, embed=embed, view=None)
                            else:
                                embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!", color=0x2F3136)
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
        class verificationModal(ui.Modal, title="VeriBlox Game Verification"):
            userID = interaction.user.id
            guildID = interaction.guild.id
            userName = ui.TextInput(label="Roblox Username", style=discord.TextStyle.short, min_length=3, max_length=20)

            async def on_submit(self, interaction: discord.Interaction):
                await interaction.response.defer(thinking=True, ephemeral=True)

                serverurl = getenv("serverurl")
                if httpx.get(serverurl + r"/api").status_code != 200:
                    embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                    embed.description = "Game Verification is currently not available since the VeriBlox API appears to be down."
                    return await interaction.followup.send(embed=embed, ephemeral=True)

                view = ui.View(timeout=300)
                robloxUser = getInfo(str(self.userName), True)

                if robloxUser["success"] == False:
                    embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                    embed.description = "The Roblox Account your attempting to verify as doesn't appear to exist. Please check for any Typo in your Roblox Username!"
                    return await interaction.followup.send(embed=embed, ephemeral=True)

                robloxID = robloxUser["id"]

                #if getGuildData(self.guildID)[7] != 0:
                #    if not getMembership(robloxID):
                #        embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                #        embed.description = "Your Roblox Account requires a Roblox Premium Membership to be verified on this server."
                #        return await interaction.followup.send(embed=embed, ephemeral=True)

                if robloxUser["banned"] == True:
                    embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                    embed.description = "The Roblox Account your attempting to verify as appears to be banned. Please use another Roblox Account!"
                    return await interaction.followup.send(embed=embed, ephemeral=True)

                if str(getGuildData(self.guildID)[2]).__contains__(str(robloxID)):
                    embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                    embed.description = "Your Roblox Account appears to be banned in this server."
                    return await interaction.followup.send(embed=embed, ephemeral=True)
                
                gs = getGuildData(self.guildID)

                try:
                    try: creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                    except: creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                except: creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

                if gs[5] != 0:
                    if round(btime.time()) - creationDate < gs[5]:
                        embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                        embed.description = "Your Roblox Account is not old enough to be Verified in this server. please Retry Verification by using an older account!"
                        return await interaction.followup.send(embed=embed, ephemeral=True)

                game = ui.Button(label="Join Game", style=discord.ButtonStyle.url, url="https://www.roblox.com/games/9728176745/VeriBlox-Verification")
                status = ui.Button(label="Waiting for Verification...", style=discord.ButtonStyle.red, disabled=True)
                cancel = ui.Button(label="Cancel", style=discord.ButtonStyle.red)

                robloxUserName = robloxUser["username"]
                robloxDisplayName = robloxUser["displayname"]
                embed = discord.Embed(title="Game Verification", description=f"Verifying as: **{robloxUserName} ({robloxDisplayName})**\nTo verify, Please Click **Join Game** and wait for Automatic Verification!", color=0x2F3136)
                
                global maxTries
                maxTries = 60
                
                async def cancelVerification(interaction: discord.Interaction):
                    global maxTries
                    await interaction.response.defer()
                    
                    maxTries -= maxTries
                    httpx.get(serverurl + r"/api/deluser?user=" + robloxUser["username"]).json()
                    await interaction.edit_original_response(content="Cancelled Game Verification.", embed=None, view=None)

                serverurl = getenv("serverurl")
                httpx.get(serverurl + r"/api/adduser?user=" + str(robloxUser["username"]), verify=False)

                view.add_item(game)
                view.add_item(status)
                view.add_item(cancel)
                cancel.callback = cancelVerification
                await interaction.followup.send(embed=embed, view=view)

                while maxTries != 0:
                    if httpx.get(serverurl + r"/status").status_code != 200:
                        maxTries -= maxTries
                        embed = discord.Embed(title="Game Verification", description=f"Verifying as: **{robloxUserName} ({robloxDisplayName})**\nGame Verification Cancelled forcefully. VeriBlox API didn't return Status Code 200. (the VeriBlox API might be down right now.)", color=0x2F3136)
                        await interaction.edit_original_response(embed=embed, view=None)
                        return log("Game Verification Cancelled. VeriBlox API didn't return Status Code 200.")

                    try: data = httpx.get(serverurl + r"/api/showvdata").json()
                    except JSONDecodeError: data = httpx.get(serverurl + r"/api/showvdata").json()

                    if str(data).__contains__(robloxUser["username"]):
                        httpx.get(serverurl + r"/api/deluser?user=" + robloxUser["username"]).json()
                        status.label = "Verifying Account..."
                        status.style = discord.ButtonStyle.grey
                        view.remove_item(cancel)
                        await interaction.edit_original_response(embed=embed, view=view)

                        gs = getGuildData(self.guildID)
                        robloxUser = getInfo(str(self.userName), True)

                        try:
                            role = discord.utils.get(interaction.guild.roles, id=gs[1])
                        except:
                            embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                            embed.description = "There was an unexpected error while getting the Verified Role for this Server. please Retry Verification!"
                            return await interaction.response.send_message(embed=embed, ephemeral=True)

                        try:
                            await interaction.user.add_roles(role)
                        except discord.Forbidden:
                            embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                            embed.description = "I couldn't Verify you in the Server since i don't have the proper permission to give you one. Please contact a Server Moderator who can fix this issue and Retry Verification!"
                            return await interaction.response.send_message(embed=embed, ephemeral=True)
                        except discord.HTTPException:
                            embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                            embed.description = "There was an error that wouldn't allow me to give you the Verified Role. please Retry Verification!"
                            return await interaction.response.send_message(embed=embed, ephemeral=True)
                        except:
                            embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                            embed.description = "There was an unexpected error while giving you the Verified Role for this server. please Retry Verification!"
                            return await interaction.response.send_message(embed=embed, ephemeral=True)

                        #if gs[7] != 0:
                        #    if getMembership(robloxUser):
                        #        if gs[8] != 0:
                        #            try: role = discord.utils.get(interaction.guild.roles, id=gs[8])
                        #            except: pass

                        #            try: await interaction.user.add_roles(role)
                        #            except: pass

                        if interaction.guild.me.guild_permissions.manage_nicknames:
                            nameFormat = getGuildData(interaction.guild.id)[9]
                            robloxUserName = robloxUser["username"]
                            robloxDisplayName = robloxUser["displayname"]
                            robloxUserId = robloxUser["id"]

                            nameFormat = nameFormat.replace("<robloxUsername>", robloxUserName)
                            nameFormat = nameFormat.replace("<robloxDisplay>", robloxDisplayName)
                            nameFormat = str(nameFormat).replace("<robloxId>", str(robloxUserId))
                            nameFormat = nameFormat.replace("<discordUsername>", interaction.user.name)

                            if interaction.user.id == interaction.guild.owner_id: pass
                            
                            try:
                                if len(nameFormat) >= 33: await interaction.user.edit(nick=robloxUserName)
                                else: await interaction.user.edit(nick=nameFormat)
                            except: pass

                            editUserData(self.userID, '"isVerified"', '"True"')
                            editUserData(self.userID, '"VerifyCode"', f'"{gen()}"')

                            if gs[2] != "":
                                await interaction.user.send(f"Message from **{interaction.guild.name}**\n" + gs[2])

                            if interaction.user.id == interaction.guild.owner_id:
                                embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.", color=0x2F3136)
                            else:
                                embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!", color=0x2F3136)
                            
                            await interaction.edit_original_response(content=None, embed=embed, view=None)
                            break

                    else:
                        maxTries -= 1
                        await sleep(5)
                
                if maxTries == 0:
                    embed = discord.Embed(title="Game Verification", description="Game Verification Timed Out. Max API httpx has been reached. Please Try Again!", color=0x2F3136)
                    await interaction.edit_original_response()

        await interaction.response.send_modal(verificationModal())            

class vbTree(CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
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
                            except IndexError:
                                log(f"Cog {msg.split()[2]} failed to load.")
                                await message.channel.send(content=f"Failed to Load Cog: {msg.split()[2]}!")

                    if msg.split()[1] == "unload":
                        if message.author.id == 583200866631155714:
                            try:
                                await bot.unload_extension(f"{msg.split()[2]}")
                                log(f"Cog {msg.split()[2]} unloaded!")
                                await message.channel.send(content=f"Cog {msg.split()[2]} unloaded!")
                            except IndexError:
                                log(f"Cog {msg.split()[2]} failed to unload.")
                                await message.channel.send(content=f"Failed to Unload Cog: {msg.split()[2]}!")

                    if msg.split()[1] == "deltemp":
                        serverurl = getenv("serverurl")

                        try:
                            if msg.split()[2] != "force":
                                if httpx.get(serverurl + r"/api/showdata").json() != {}:
                                    return await message.channel.send(content="Failed to delete all Temporary Data from VeriBlox API. There are currently users verifying through Game Verification.")
                                else:
                                    httpx.get(serverurl + r"/api/delall")
                                    return await message.channel.send(content="Deleted all Temporary Data from VeriBlox API!")
                        except IndexError: 
                            if httpx.get(serverurl + r"/api/showdata").json() != {}:
                                return await message.channel.send(content="Failed to delete all Temporary Data from VeriBlox API. There are currently users verifying through Game Verification.")

                        httpx.get(serverurl + r"/api/delall")
                        await message.channel.send(content="Deleted all Temporary Data from VeriBlox API!")


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
                            except IndexError:
                                pass
                            
                            log("VeriBlox Cogs Reloaded!")
                            await message.channel.send(content="All Cogs Reloaded!")
                except:
                    await message.channel.send(f"Hello! I'm {bot.user.mention}! for commands, type in </help:981132603329482752>! `{round(bot.latency * 1000)}ms`")

    async def on_guild_join(self, guild: discord.Guild):
        if not guild.id in getGuildList(): addGuildData(guild.id)
        else: pass

        log(f"VeriBlox has been invited to {guild.name} ({guild.member_count} Members)! VeriBlox is now in {len(bot.guilds):,} Guilds!")

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
                    else: pass

                await sleep(300)
                
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

        async def createBackupData():
            while True:
                deleteDuplicateData()
                await bot.get_channel(1017749220620517436).send(file=discord.File(r'./data/data.db'))
                log("Sent Backup Data!")
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

        bot.loop.create_task(updateActivity())
        bot.loop.create_task(autoCogReloader())

        if testing == False:
            topggToken = getenv("ggtoken")
            topgg.client.DBLClient(bot, topggToken, autopost=True, post_shard_count=False)
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
    class verificationModal(ui.Modal, title="VeriBlox Code Verification"):
        userID = interaction.user.id
        guildID = interaction.guild.id
        userName = ui.TextInput(label="Roblox Username", style=discord.TextStyle.short, min_length=3, max_length=20)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(thinking=True, ephemeral=True)
            robloxUser = getInfo(str(self.userName), True)

            if robloxUser["success"] == False:
                embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                embed.description = "The Roblox Account your attempting to verify as doesn't appear to exist. Please check for any Typo in your Roblox Username!"
                return await interaction.followup.send(embed=embed, ephemeral=True)

            view = ui.View()
            getCode = ui.Button(label="Get Code", style=discord.ButtonStyle.green)
            genCode = ui.Button(label="Regenerate Code", style=discord.ButtonStyle.grey)
            verify  = ui.Button(label="Verify Account", style=discord.ButtonStyle.green)

            robloxID = robloxUser["id"]

            #if getGuildData(self.guildID)[7] != 0:
            #    if not getMembership(robloxUser):
            #        embed = discord.Embed(title="Verification Failed", color=0x2F3136)
            #        embed.description = "Your Roblox Account requires a Roblox Premium Membership to be verified on this server."
            #        return await interaction.followup.send(embed=embed, ephemeral=True)

            if robloxUser["banned"] == True:
                embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                embed.description = "The Roblox Account your attempting to verify as appears to be banned. Please use another Roblox Account!"
                return await interaction.followup.send(embed=embed, ephemeral=True)

            if str(getGuildData(self.guildID)[2]).__contains__(str(robloxID)):
                embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                embed.description = "Your Roblox Account appears to be banned in this server."
                return await interaction.followup.send(embed=embed)
            
            gs = getGuildData(self.guildID)

            try:
                try: creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                except: creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            except: creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

            if gs[5] != 0:
                if round(btime.time()) - creationDate < gs[5]:
                    embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                    embed.description = "Your Roblox Account is not old enough to be Verified in this server. please Retry Verification by using an older account!"
                    return await interaction.response.send_message(embed=embed, ephemeral=True)

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
                        role = discord.utils.get(interaction.guild.roles, id=gs[1])
                    except:
                        embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                        embed.description = "There was an unexpected error while getting the Verified Role for this Server. please Retry Verification!"
                        return await interaction.response.send_message(embed=embed, ephemeral=True)

                    try:
                        await interaction.user.add_roles(role)
                    except discord.Forbidden:
                        embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                        embed.description = "I couldn't Verify you in the Server since i don't have the proper permission to give you one. Please contact a Server Moderator who can fix this issue and Retry Verification!"
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    except discord.HTTPException:
                        embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                        embed.description = "There was an error that wouldn't allow me to give you the Verified Role. please Retry Verification!"
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    except:
                        embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                        embed.description = "There was an unexpected error while giving you the Verified Role for this server. please Retry Verification!"
                        return await interaction.response.send_message(embed=embed, ephemeral=True)

                    #if gs[7] != 0:
                    #    if getMembership(robloxUser):
                    #        if gs[8] != 0:
                    #            try: role = discord.utils.get(interaction.guild.roles, id=gs[8])
                    #            except: pass

                    #            try: await interaction.user.add_roles(role)
                    #            except: pass

                    if interaction.guild.me.guild_permissions.manage_nicknames:
                        nameFormat = getGuildData(interaction.guild.id)[9]
                        robloxUserName = robloxUser["username"]
                        robloxDisplayName = robloxUser["displayname"]
                        robloxUserId = robloxUser["id"]

                        nameFormat = nameFormat.replace("<robloxUsername>", robloxUserName)
                        nameFormat = nameFormat.replace("<robloxDisplay>", robloxDisplayName)
                        nameFormat = str(nameFormat).replace("<robloxId>", str(robloxUserId))
                        nameFormat = nameFormat.replace("<discordUsername>", interaction.user.name)

                        if interaction.user.id == interaction.guild.owner_id: pass
                        
                        try:
                            if len(nameFormat) >= 33: await interaction.user.edit(nick=robloxUserName)
                            else: await interaction.user.edit(nick=nameFormat)
                        except: pass

                        editUserData(self.userID, '"isVerified"', '"True"')
                        editUserData(self.userID, '"VerifyCode"', f'"{gen()}"')

                        if gs[2] != "":
                            await interaction.user.send(f"Message from **{interaction.guild.name}**\n" + gs[2])

                        if interaction.user.id == interaction.guild.owner_id:
                            embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.", color=0x2F3136)
                            await interaction.response.edit_message(content=None, embed=embed, view=None)
                        else:
                            embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!", color=0x2F3136)
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

    if interaction.user.id in getUserList():
        if getUserData(interaction.user.id)[3] == "True":
            guildID = str(interaction.guild.id)
            gs = getGuildData(guildID)
            robloxUser = getInfo(int(getUserData(interaction.user.id)[1]), True)

            try:
                try: creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                except: creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            except: creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

            if gs[5] != 0:
                if round(btime.time()) - creationDate < gs[5]:
                    embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                    embed.description = "Your Roblox Account is not old enough to be Verified in this server. please Retry Verification by using an older account!"
                    return await interaction.response.send_message(embed=embed, ephemeral=True)

            try:
                role = discord.utils.get(interaction.guild.roles, id=gs[1])
            except:
                embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                embed.description = "There was an unexpected error while getting the Verified Role for this Server. please Retry Verification!"
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            try:
                await interaction.user.add_roles(role)
            except discord.Forbidden:
                embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                embed.description = "I couldn't Verify you in the Server since i don't have the proper permission to give you one. Please contact a Server Moderator who can fix this issue and Retry Verification!"
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            except discord.HTTPException:
                embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                embed.description = "There was an error that wouldn't allow me to give you the Verified Role. please Retry Verification!"
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                embed = discord.Embed(title="Verification Failed", color=0x2F3136)
                embed.description = "There was an unexpected error while giving you the Verified Role for this server. please Retry Verification!"
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            #if gs[7] != 0:
            #    if getMembership(robloxUser):
            #        if gs[8] != 0:
            #            try: role = discord.utils.get(interaction.guild.roles, id=gs[8])
            #            except: pass

            #            try: await interaction.user.add_roles(role)
            #            except: pass

            if interaction.guild.me.guild_permissions.manage_nicknames:
                nameFormat = getGuildData(interaction.guild.id)[9]
                robloxUserName = robloxUser["username"]
                robloxDisplayName = robloxUser["displayname"]
                robloxUserId = robloxUser["id"]

                nameFormat = nameFormat.replace("<robloxUsername>", robloxUserName)
                nameFormat = nameFormat.replace("<robloxDisplay>", robloxDisplayName)
                nameFormat = str(nameFormat).replace("<robloxId>", str(robloxUserId))
                nameFormat = nameFormat.replace("<discordUsername>", interaction.user.name)

                if interaction.user.id == interaction.guild.owner_id: pass
                
                try:
                    if len(nameFormat) >= 33: await interaction.user.edit(nick=robloxUserName)
                    else: await interaction.user.edit(nick=nameFormat)
                except: pass

                if gs[2] != "":
                    await interaction.user.send(f"Message from **{interaction.guild.name}**\n" + gs[2])

            if interaction.user.id == interaction.guild.owner_id: embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.", color=0x2F3136)
            else: embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!", color=0x2F3136)
            await interaction.response.send_message(embed=embed)
        else: await interaction.response.send_modal(verificationModal())
    else: await interaction.response.send_modal(verificationModal())

@bot.tree.command(name="setup", description="Creates a verification channel")
@discord.app_commands.describe(verifiedrole = "The role you want to be set as verified role")
async def setup(interaction: discord.Interaction, verifiedrole : discord.Role):
    if not interaction.guild:
        embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
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
    embed = discord.Embed(title="VeriBlox Verification", description="This server is a **Roblox Server**. in order to verify in this server, you will need a **Roblox Account** to verify your **Discord Account** in this server!.\n\nFor Verification Instructions, click one of the Hyperlinks Below.\n**[Code Verification Instructions (Image)](https://media.discordapp.net/attachments/1006854052010807366/1041612500640206909/VeriBlox-CodeVerification.png)\n[Game Verification Instructions (Image)](https://cdn.discordapp.com/attachments/1006854052010807366/1041612500325630002/VeriBlox-GameVerification.png)**", color=0x2F3136)
    await verifychannel.send(embed=embed, view=VeriBloxVerification())

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
    embed = discord.Embed(color=0x2F3136)

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

    if isinstance(error, discord.errors.NotFound):
        log("Interaction Not Found: Defered User Interaction.")
        await interaction.response.defer()

    try: await interaction.response.send_message(embed=embed, ephemeral=True)
    except: pass
    
    etype = type(error)
    trace = error.__traceback__
    lines = traceback.format_exception(etype, error, trace)
    traceback_text = ''.join(lines)
    sendLog(f"```cmd\n{traceback_text}\n```", True)
    raise error

if testing == False: token = getenv("token")
else: token = getenv("testtoken")

bot.run(token)
