import discord
import discord.ui as ui
import discord.ext.commands as commands
from discord.app_commands import CommandTree

import traceback
import aiofiles
from os import getenv
from asyncio import sleep
from json import loads, dumps
from dotenv import load_dotenv
from datetime import datetime, date, time

from packages.DataTools import ratelimitUser, readUserData, readGuildData, appendUserData, appendGuildData, getrtTime, refreshUserData
from packages.RobloxAPI import getInfo
from packages.Logging import log
from packages.vCodeGen import gen
from packages.HookLogging import sendLog

load_dotenv("./conf/.env")

users = {}
apicmds = ["whois", "username", "id", "avatar"]

class VeriBloxVerification(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label='Verify', style=discord.ButtonStyle.green, custom_id="persistent_view:verification")
    async def verification(self, interaction: discord.Interaction, button: ui.Button):
        vs, gs = await readUserData(), await readGuildData()
        class verificationModal(ui.Modal, title="VeriBlox Verification"):
            userID = str(interaction.user.id)
            guildID = str(interaction.guild.id)
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

                if robloxUser["banned"] == True:
                    return await interaction.followup.send(content=f"**🚫 | This Roblox Account appears to be banned.**")

                try:
                    if robloxID in gs[self.guildID]["bannedIds"]:
                        return await interaction.followup.send(content="**🚫 | This Roblox Account appears to be banned from this server.**")
                except:
                    pass

                if not self.userID in vs:
                    vs[self.userID] = {}
                    vs[self.userID]["username"] = robloxUser["username"]
                    vs[self.userID]["displayname"] = robloxUser["displayname"]
                    vs[self.userID]["robloxid"] = robloxUser["id"]
                    vs[self.userID]["verifyCode"] = gen()
                    vs[self.userID]["verified"] = False
                    vs[self.userID]["expiredAfter"] = 60
                    await appendUserData(vs)

                async def getVerificationCode(interaction: discord.Interaction):
                    vs = await readUserData()
                    class verificationCode(ui.Modal, title="VeriBlox Verification Code"):
                        robloxVerificationCode = ui.TextInput(label="Verification Code", style=discord.TextStyle.long, default=vs[self.userID]["verifyCode"])

                        async def on_submit(self, interaction: discord.Interaction):
                            await interaction.response.defer()

                    await interaction.response.send_modal(verificationCode())

                async def regenVerificationCode(interaction: discord.Interaction):
                    vs = await readUserData()
                    vs[self.userID]["verifyCode"] = gen()
                    appendUserData(vs)
                    genCode.label = "Regenerate Code"
                    genCode.style = discord.ButtonStyle.red
                    genCode.disabled = True
                    await interaction.response.edit_message(view=view)
                    await sleep(30)
                    genCode.style = discord.ButtonStyle.grey
                    genCode.disabled = False
                    await interaction.edit_original_message(view=view)

                async def verifyUser(interaction: discord.Interaction):
                    vs = await readUserData()
                    robloxUser = getInfo(str(self.userName), True)
                    if vs[self.userID]["verifyCode"] == robloxUser["description"]:
                        try:
                            try:
                                creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                            except:
                                creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                        except:
                            creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

                        if gs[self.guildID]["agereq"] != 0:
                            if time() - creationDate < gs[self.guildID]["agereq"]:
                                return await interaction.response.send_message(content="**🚫 | This Roblox Account is not Elegible to be in this server. Please use another Roblox Account that's older than this Roblox Account!**")

                        try:
                            role = discord.utils.get(interaction.guild.roles, id=gs[self.guildID]["verifiedrole"])
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

                            vs = await readUserData()
                            vs[self.userID]["verified"] = True
                            vs[self.userID]["robloxid"] = robloxUser["id"]
                            vs[self.userID]["verifyCode"] = gen()
                            appendUserData(vs)

                            if gs[self.guildID]["welcomemessage"] != "":
                                await interaction.user.send(f"Message from **{interaction.guild.name}**\n" + gs[self.guildID]["welcomemessage"])

                            if interaction.user.id == interaction.guild.owner_id:
                                embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                                await interaction.response.edit_message(content=None, embed=embed, view=None)
                            else:
                                embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!")
                                await interaction.response.edit_message(content=None, embed=embed, view=None)

                    else:
                        return await interaction.response.send_message(content="**🚫 | Looks like you havent pasted the code in your Roblox Description. Please paste it and try again!**", ephemeral=True)

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

class vbTree(CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        try: await refreshUserData(str(interaction.user.id))
        except: pass

        async with aiofiles.open(r"data/ratelimited.json", "r") as f:
            blacklist = loads(await f.read())
        
        if not str(interaction.user.id) in users:
            users[str(interaction.user.id)] = 0

        if users[str(interaction.user.id)] >= 7:
            if str(interaction.user.id) in users:
                ratelimitUser(str(interaction.user.id), round(datetime.now().timestamp()) + 1800)
                del users[str(interaction.user.id)]
                sendLog(f"Ratelimited user: {interaction.user} ({interaction.user.id})")

        if interaction.command.name in apicmds:
            async with aiofiles.open(r"data/ratelimited.json", "r") as f:
                data = loads(await f.read())

            if not str(interaction.user.id) in data:
                users[str(interaction.user.id)] += 1

            if str(interaction.user.id) in blacklist:
                log(interaction.command.name)
                time = getrtTime(str(interaction.user.id))
                embed = discord.Embed(title="VeriBlox Ratelimit", description=f"You are being ratelimited from using VeriBlox Commands that uses the Roblox API!\nYou can run commands again <t:{time}:R>", color=0x2F3136)
                await interaction.response.send_message(embed=embed)
                return False
        
        return True

class VeriBlox(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=[], intents=intents, tree_cls=vbTree)

    async def setup_hook(self) -> None:
        self.add_view(VeriBloxVerification())
        await bot.load_extension("commands.help")
        await bot.load_extension("commands.server")
        await bot.load_extension("commands.user")

        await bot.load_extension("background.malblock")
        await bot.load_extension("background.autoverify")
        log("VeriBlox Cogs Loaded!")

    async def on_message(self, message: discord.Message):
        if bot.user.mentioned_in(message):
            if message.author == bot.user:
                return

            if message.author.bot:
                return

            msg = message.content

            if msg.startswith("@everyone"):
                return

            if msg.startswith("@here"):
                return
            
            if msg.startswith(f"<@{bot.user.id}>"):
                try:
                    if msg.split()[1] == "reload":
                        if message.author.id == 583200866631155714:
                            await bot.unload_extension("commands.help")
                            await bot.unload_extension("commands.server")
                            await bot.unload_extension("commands.user")
                            await bot.unload_extension("background.malblock")
                            await bot.unload_extension("background.autoverify")

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

    async def on_guild_join(self, guild):
        gs = await readGuildData()

        if not str(guild.id) in gs:
            gs[str(guild.id)] = {}
            gs[str(guild.id)]["verifiedrole"] = 0
            gs[str(guild.id)]["welcomemessage"] = ""
            gs[str(guild.id)]["bannedIds"] = []
            gs[str(guild.id)]["malblock"] = True
            gs[str(guild.id)]["auto"] = True
            gs[str(guild.id)]["agereq"] = 0
        else:
            pass

        appendGuildData(gs)

        log(f"VeriBlox has been invited to {guild.name} ({len(bot.guilds):,}, {guild.member_count})!")

    async def on_ready(self):
        async def updateActivity():
            while True:
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds):,} Servers | /help"))
                await sleep(60)
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.users):,} Users | /help"))
                await sleep(60)
        
        async def missingDataDump():
            while True:
                for guild in bot.guilds:
                    gs = await readGuildData()

                    if not str(guild.id) in gs:
                        gs[str(guild.id)] = {}
                        gs[str(guild.id)]["verifiedrole"] = 0
                        gs[str(guild.id)]["welcomemessage"] = ""
                        gs[str(guild.id)]["bannedIds"] = []
                        gs[str(guild.id)]["malblock"] = True
                        gs[str(guild.id)]["auto"] = True
                        gs[str(guild.id)]["agereq"] = 0
                        await appendGuildData(gs)
                        log(f"Added guild data for {guild.name} ({guild.id})")
                    else:
                        pass

                await sleep(60)

        async def expireUserData():
            previousDate = 0
            currentDate = date.today().strftime("%d")
            previousDate = currentDate

            for x in await readUserData():
                vs = await readUserData()
                if vs[str(x)]["expiredAfter"] == 0:
                    del vs[str(x)]
                    log(f"User {x} data expired, Deleted.")
                await appendUserData(vs)

            while True:
                currentDate = date.today().strftime("%d")            
                if currentDate != previousDate:
                    for x in await readUserData():
                        vs = await readUserData()
                        if vs[str(x)]["expiredAfter"] != 0:
                            vs[str(x)]["expiredAfter"] -= 1
                        
                        if vs[str(x)]["expiredAfter"] == 0:
                            del vs[str(x)]
                            log(f"User {x} data expired, Deleted.")
                        await appendUserData(vs)

                    previousDate = currentDate

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
                
                await sleep(1)

        async def resetTempRT():
            while True:
                users.clear()
                await sleep(60)

        bot.loop.create_task(updateActivity())
        bot.loop.create_task(missingDataDump())
        bot.loop.create_task(expireUserData())
        bot.loop.create_task(removeTempRT())
        bot.loop.create_task(resetTempRT())
        log("Tasks Started!")

        await bot.tree.sync()
        log("VeriBlox Started!")
        sendLog(f"VeriBlox Started!\n```\nShard Count: {bot.shard_count}\nServer Count: {len(bot.guilds):,}\nUser Count: {len(bot.users):,}\n```")

bot = VeriBlox()

@bot.tree.command(name="verify", description="Verifies your Discord Account with your Roblox Account on VeriBlox")
async def verify(interaction : discord.Interaction):
    vs, gs = await readUserData(), await readGuildData()
    class verificationModal(ui.Modal, title="VeriBlox Verification"):
        userID = str(interaction.user.id)
        guildID = str(interaction.guild.id)
        userName = ui.TextInput(label="Roblox Username", style=discord.TextStyle.short, min_length=3, max_length=20)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(thinking=True, ephemeral=True)
            robloxUser = getInfo(str(self.userName), True)
            robloxID = robloxUser["id"]

            if robloxUser["success"] == False:
                return await interaction.followup.send(content="**🚫 | This Roblox Account doesn't appear to exist!**", ephemeral=True)

            view = ui.View()
            getCode = ui.Button(label="Get Code", style=discord.ButtonStyle.green)
            genCode = ui.Button(label="Regenerate Code", style=discord.ButtonStyle.grey)
            verify  = ui.Button(label="Verify Account", style=discord.ButtonStyle.green)


            if robloxUser["banned"] == True:
                return await interaction.followup.send(content=f"**🚫 | This Roblox Account appears to be banned.**")

            try:
                if robloxID in gs[self.guildID]["bannedIds"]:
                    return await interaction.followup.send(content="**🚫 | This Roblox Account appears to be banned from this server.**")
            except:
                pass

            if not self.userID in vs:
                vs[self.userID] = {}
                vs[self.userID]["username"] = robloxUser["username"]
                vs[self.userID]["displayname"] = robloxUser["displayname"]
                vs[self.userID]["robloxid"] = robloxUser["id"]
                vs[self.userID]["verifyCode"] = gen()
                vs[self.userID]["verified"] = False
                vs[self.userID]["expiredAfter"] = 60
                appendUserData(vs)

            async def getVerificationCode(interaction: discord.Interaction):
                vs = await readUserData()
                class verificationCode(ui.Modal, title="VeriBlox Verification Code"):
                    robloxVerificationCode = ui.TextInput(label="Verification Code", style=discord.TextStyle.long, default=vs[self.userID]["verifyCode"])

                    async def on_submit(self, interaction: discord.Interaction):
                        await interaction.response.defer()

                await interaction.response.send_modal(verificationCode())

            async def regenVerificationCode(interaction: discord.Interaction):
                vs = await readUserData()
                vs[self.userID]["verifyCode"] = gen()
                appendUserData(vs)
                genCode.label = "Regenerate Code"
                genCode.style = discord.ButtonStyle.red
                genCode.disabled = True
                await interaction.response.edit_message(view=view)
                await sleep(30)
                genCode.style = discord.ButtonStyle.grey
                genCode.disabled = False
                await interaction.edit_original_message(view=view)

            async def verifyUser(interaction: discord.Interaction):
                vs = readUserData()
                robloxUser = getInfo(str(self.userName), True)
                if vs[self.userID]["verifyCode"] == robloxUser["description"]:
                    try:
                        try:
                            creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                        except:
                            creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                    except:
                        creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

                    if gs[self.guildID]["agereq"] != 0:
                        if time() - creationDate < gs[self.guildID]["agereq"]:
                            return await interaction.response.send_message(content="**🚫 | This Roblox Account is not Elegible to be in this server. Please use another Roblox Account that's older than this Roblox Account!**")

                    try:
                        role = discord.utils.get(interaction.guild.roles, id=gs[self.guildID]["verifiedrole"])
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

                        vs = await readUserData()
                        vs[self.userID]["verified"] = True
                        vs[self.userID]["robloxid"] = robloxUser["id"]
                        vs[self.userID]["verifyCode"] = gen()
                        appendUserData(vs)

                        if gs[self.guildID]["welcomemessage"] != "":
                            await interaction.user.send(f"Message from **{interaction.guild.name}**\n" + gs[self.guildID]["welcomemessage"])

                        if interaction.user.id == interaction.guild.owner_id:
                            embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                            await interaction.response.edit_message(content=None, embed=embed, view=None)
                        else:
                            embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!")
                            await interaction.response.edit_message(content=None, embed=embed, view=None)

                else:
                    return await interaction.response.send_message(content="**🚫 | Looks like you havent pasted the code in your Roblox Description. Please paste it and try again!**", ephemeral=True)

            getCode.callback = getVerificationCode
            genCode.callback = regenVerificationCode
            verify.callback = verifyUser
            view.add_item(getCode)
            view.add_item(genCode)
            view.add_item(verify)
            robloxUserName = robloxUser["username"]
            robloxDisplayName = robloxUser["displayname"]
            await interaction.followup.send(content=f"**Account Found!** Verifying as **{robloxUserName} ({robloxDisplayName}**)\n> You can only regenerate your verification code once every **30 seconds**.", view=view, ephemeral=True)

    data = await readUserData()

    if str(interaction.user.id) in data:
        if data[str(interaction.user.id)]["verified"] == True:
            robloxUser = getInfo(int(data[str(interaction.user.id)]["robloxid"]))
            userID = str(interaction.user.id)
            guildID = str(interaction.guild.id)
            vs = await readUserData()
            gs = await readGuildData()

            try:
                try:
                    creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                except:
                    creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            except:
                creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

            if gs[guildID]["agereq"] != 0:
                if time() - creationDate < gs[guildID]["agereq"]:
                    return await interaction.response.send_message(content="**🚫 | This Roblox Account is not Elegible to be in this server. Please use another Roblox Account that's older than this Roblox Account!**")

            try:
                role = discord.utils.get(interaction.guild.roles, id=gs[guildID]["verifiedrole"])
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

                vs[userID]["verified"] = True
                vs[userID]["displayname"] = robloxDisplayName
                vs[userID]["verifyCode"] = gen()
                appendUserData(vs)

                if interaction.user.id == interaction.guild.owner_id:
                    embed = discord.Embed(description=f"**Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!**\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(description=f"**Successfully Verified as **{robloxUserName} ({robloxDisplayName}])!**")
                    await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            await interaction.response.send_modal(verificationModal())

    else:
        await interaction.response.send_modal(verificationModal())

@bot.tree.command(name="setup", description="Creates a verification channel")
@discord.app_commands.describe(verifiedrole = "The role you want to be set as verified role")
async def setup(interaction: discord.Interaction, verifiedrole : discord.Role):
    gs = await readGuildData()

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
        gs[str(guild.id)]["verifiedrole"] = verifiedrole.id
    except KeyError:
        gs[str(guild.id)] = {}
        gs[str(guild.id)]["verifiedrole"] = verifiedrole.id
        gs[str(guild.id)]["welcomemessage"] = ""
        gs[str(guild.id)]["bannedIds"] = []
        gs[str(guild.id)]["malblock"] = True
        gs[str(guild.id)]["agereq"] = 0

    appendGuildData(gs)

    category = await guild.create_category("VeriBlox Verification")
    verifychannel = await guild.create_text_channel('verify', category=category)
    embed = discord.Embed(title="VeriBlox Verification", description="This server is a **Roblox Server**. to verify, you will need an **Roblox Account** to verify your **Discord Account** to gain full access to this server!\nFor verification instructions, [click here]().")
    embed_inst = discord.Embed(title="VeriBlox Verification Instructions", description="**Step 1**: Click on **Verify** and type in your **Roblox Username** and click on **Submit**\n**Step 2**: Click on **Get Code** and go to your **Roblox Profile Page** and place the verification code in your **Roblox Description / About Me**\n**Step 3**: Click on **Verify Account** to gain full access to this server!")
    await verifychannel.send(embeds=[embed, embed_inst], view=VeriBloxVerification())

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


token = getenv("token")
bot.run(token)