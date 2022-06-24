from discord.ui import Button, View, Modal, TextInput
from discord import app_commands, Interaction
from discord.ext import commands
from discord.ui import TextInput
from datetime import datetime, date
import requests
import asyncio
import discord
import random
import time
import json
import os

start = time.process_time()

class persistentVerify(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Start Verification', style=discord.ButtonStyle.green, custom_id='persistent_view:verification')
    async def verification(self, interaction: Interaction, button: Button):
        class verification(Modal, title="VeriBlox Verification"):
            with open(r"verifystatus.json", "r") as f:
                vs = json.load(f)
            with open(r"guildsettings.json", "r") as f:
                gs = json.load(f)

            words = ["verification", "verify", "veriblox", "roblox", "api",
                      "home", "interaction", "code", "cat", "dog",
                      "duck", "elephant", "lion", "tiger", "zebra", 
                      "panda", "frog", "bird", "eagle", "phone", 
                      "laptop", "computer", "console", "keyboard", "mouse", 
                      "screen", "watch", "camera", "movie", "backpack",
                      "cap", "speaker", "sunglasses", "fan", "mirror",
                      "gamepad", "tetris", "games", "avatar", "wireless"]
            discordid = str(interaction.user.id)
            username = TextInput(label=f"Roblox Username (Case Sensitive)", style=discord.TextStyle.short, min_length=3, max_length=20)

            async def on_submit(self, interaction: Interaction):
                gbu = requests.get(f"https://api.roblox.com/users/get-by-username?username={str(self.username)}").json()

                try:
                    if gbu["success"] == False:
                        return await interaction.response.send_message(content="This account doesn't appear to exist! Please check if there's any typo.", ephemeral=True)
                 
                except:
                    id = gbu["Id"]
                    user = requests.get(f"https://users.roblox.com/v1/users/{id}").json()

                    if user["isBanned"] == True:
                        return await interaction.response.send_message(content=f"This roblox account appears to be banned. Please verify with another account if you have one!")

                    try:
                        if id in self.gs[str(interaction.guild.id)]["bannedIds"]:
                            username = user["name"]
                            return await interaction.response.send_message(f"This roblox account **{username}** appears to be banned from this server.")
                    except:
                        pass

                    if not self.discordid in self.vs:
                        keyg = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
                        self.vs[self.discordid] = {}
                        self.vs[self.discordid]["username"] = user["name"]
                        self.vs[self.discordid]["displayname"] = user["displayName"]
                        self.vs[self.discordid]["robloxid"] = gbu["Id"]
                        self.vs[self.discordid]["verifykey"] = keyg
                        self.vs[self.discordid]["verified"] = False
                        self.vs[self.discordid]["expiredAfter"] = 7

                        with open(r"verifystatus.json", "w") as f:
                            json.dump(self.vs, f, indent=4)

                    view = View()

                    getcode = Button(label="Verification Code", style=discord.ButtonStyle.green)
                    regencode = Button(label="Regenerate Code", style=discord.ButtonStyle.grey)
                    verify = Button(label="Verify Account", style=discord.ButtonStyle.green)

                    async def getverificationcode(interaction):
                        class verification_code(Modal, title="VeriBlox Verification Code"):
                            verification = TextInput(label=f"Verification Code (Copy)", style=discord.TextStyle.long, default=self.vs[self.discordid]["verifykey"], max_length=len(self.vs[self.discordid]["verifykey"]))

                            async def on_submit(self, interaction: discord.Interaction):
                                await interaction.response.defer()
                        
                        await interaction.response.send_modal(verification_code())

                    async def regverificationcode(interaction):
                        keyg = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
                        self.vs[self.discordid]["verifykey"] = keyg
                        with open(r"verifystatus.json", "w") as f:
                            json.dump(self.vs, f, indent=4)
                        regencode.label = "Regenerate Code"
                        regencode.style = discord.ButtonStyle.red
                        regencode.disabled = True
                        await interaction.response.edit_message(view=view)
                        await asyncio.sleep(30)
                        regencode.label = "Regenerate Code"
                        regencode.style = discord.ButtonStyle.grey
                        regencode.disabled = False
                        await interaction.edit_original_message(view=view)

                    async def verifyuser(interaction):
                        id = self.vs[self.discordid]["robloxid"]
                        user = requests.get(f"https://users.roblox.com/v1/users/{id}").json()

                        if user["description"] == self.vs[self.discordid]["verifykey"]:
                            guild = str(interaction.guild.id)

                            with open(r"guildsettings.json", "r") as f:
                                gs = json.load(f)

                            created = user["created"]
                            try:
                                try:
                                    creationdate = datetime.fromisoformat(created[:-1] + '+00:00').timestamp()
                                except:
                                    creationdate = datetime.strptime(created,"%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                            except:
                                creationdate = datetime.fromisoformat(created.split('.')[0]).timestamp()

                            if gs[str(interaction.guild.id)]["agereq"] != 0:
                                if time.time() - creationdate < gs[str(interaction.guild.id)]["agereq"]:
                                    return await interaction.user.send("Unfortunately, your **Roblox Account** is not elegible to join this server since it does not meet the account age requirement. If you have an older roblox account, please use that one instead!")

                            try:
                                with open(r"guildsettings.json", "r") as f:
                                    gs = json.load(f)
                                rolename = gs[guild]["verifiedrole"]
                                role = discord.utils.get(interaction.guild.roles, name=rolename)
                                await interaction.user.add_roles(role)
                            except:
                                return await interaction.response.send_message(content="I could not give you the verified role since the role is higher than mine, or the **Server Owner** / **Server Moderator** haven't set one. Please contact a **Server Moderator** to fix bot permissions!", ephemeral=True)

                            rbusername = user["name"]
                            rbdispname = user["displayName"]

                            if interaction.user.id == interaction.guild.owner_id:
                                pass
                            
                            else:
                                if rbusername == rbdispname:
                                    try:
                                        await interaction.user.edit(nick=f"{rbusername}")
                                    except:
                                        pass
                                else:
                                    u = f"{rbdispname} - @{rbusername}"
                                    
                                    if len(u) >= 31:
                                        try:
                                            await interaction.user.edit(nick=f"{rbusername}")
                                        except:
                                            pass
                                    else:
                                        try:
                                            await interaction.user.edit(nick=f"{rbdispname} - @{rbusername}")
                                        except:
                                            pass

                            self.vs[self.discordid]["verified"] = True
                            self.vs[self.discordid]["displayname"] = rbdispname
                            keyg = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
                            self.vs[self.discordid]["verifykey"] = keyg

                            with open(r"verifystatus.json", "w") as f:
                                json.dump(self.vs, f, indent=4)
                            
                            with open(r"guildsettings.json", "r") as f:
                                gs = json.load(f)

                            if gs[str(interaction.guild.id)]["welcomemessage"] != "":
                                user = bot.get_user(interaction.user.id)
                                await user.send(gs[str(interaction.guild.id)]["welcomemessage"])
                            
                            if interaction.user.id == interaction.guild.owner_id:
                                embed = discord.Embed(description=f"**Successfully Verified as **{rbusername} ({rbdispname})**!**\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)
                            else:
                                embed = discord.Embed(description=f"**Successfully Verified as **{rbusername} ({rbdispname}])!**")
                                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)

                        else:
                            await interaction.response.send_message(content=f"Looks like you havent pasted the code in your **Roblox Description / About Me**. Change it and try again!", ephemeral=True)
                            return

                    getcode.callback = getverificationcode
                    regencode.callback = regverificationcode
                    verify.callback = verifyuser
                    view.add_item(getcode)
                    view.add_item(regencode)
                    view.add_item(verify)
                    id = self.vs[self.discordid]["robloxid"]
                    user = requests.get(f"https://users.roblox.com/v1/users/{id}").json()
                    rbusername = user["name"]
                    rbdispname = user["displayName"]
                    await interaction.response.send_message(content=f"**Account Found!** Verifying as **{rbusername} ({rbdispname}**)\n> You can only regenerate your verification code once every **30 seconds**.", view=view, ephemeral=True)

        await interaction.response.send_modal(verification())

class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('v.'), intents=intents)
    
    async def setup_hook(self) -> None:
        self.add_view(persistentVerify())
        await bot.load_extension("cogs.malblock")
        await bot.load_extension("cogs.help")
        await bot.load_extension("cogs.user")
        await bot.load_extension("cogs.mod")
        await bot.load_extension("cogs.util")
        await bot.load_extension("cogs.verify")

    async def on_ready(self):
        async def activityLoop():
            while True:
                day = date.today().strftime("%d")
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"/help | {len(bot.guilds):,} Servers | {day} / 31"))
                await asyncio.sleep(30)
        
        async def missingDataDump():
            while True:
                for guild in bot.guilds:
                    with open(r"guildsettings.json", "r") as f:
                        gs = json.load(f)

                    if not str(guild.id) in gs:
                        gs[str(guild.id)] = {}
                        gs[str(guild.id)]["verifiedrole"] = "Verified"
                        gs[str(guild.id)]["welcomemessage"] = ""
                        gs[str(guild.id)]["bannedIds"] = []
                        gs[str(guild.id)]["malblock"] = True
                        gs[str(guild.id)]["agereq"] = 0
                    else:
                        pass

                with open(r"guildsettings.json", "w") as f:
                    json.dump(gs, f, indent=4)

                await asyncio.sleep(300)

        async def expiredUserData():
            previousDate = 0
            currentDate = date.today().strftime("%d")
            previousDate = currentDate

            while True:
                currentDate = date.today().strftime("%d")            
                if currentDate != previousDate:
                    with open(r"verifystatus.json", "r") as f:
                        vs = json.load(f)

                    previousDate = currentDate

                    for x in vs:
                        if vs[str(x)]["expiredAfter"] != 0:
                            vs[str(x)]["expiredAfter"] -= 1
                        
                        if vs[str(x)]["expiredAfter"] == 0:
                            print(f"Deleted user data for {x}")
                            del vs[str(x)]

                        with open(r"verifystatus.json", "w") as f:
                            json.dump(vs, f, indent=4)

                await asyncio.sleep(60)
                
        bot.loop.create_task(activityLoop())
        bot.loop.create_task(missingDataDump())
        bot.loop.create_task(expiredUserData())
        await bot.tree.sync()
        print(f"VeriBlox Started - - - - -\nLogged in as {bot.user}\tID: {bot.user.id}\nShards: {bot.shard_count}\n\nBot Started in {time.process_time() - start}s")
    
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
                    if msg.split()[1] == "getdata":
                        if message.author.id == 583200866631155714:
                            with open("guildsettings.json", "rb") as guilddata:
                                with open("verifystatus.json", "rb") as userdata:
                                    await message.channel.send(files=[discord.File(guilddata, "guildsettings.json"), discord.File(userdata, "verifystatus.json")], delete_after=300)

                    if msg.split()[1] == "reload":
                        if message.author.id == 583200866631155714:
                            await bot.unload_extension("cogs.malblock")
                            await bot.unload_extension("cogs.help")
                            await bot.unload_extension("cogs.user")
                            await bot.unload_extension("cogs.mod")
                            await bot.unload_extension("cogs.util")
                            await bot.unload_extension("cogs.verify")

                            await bot.load_extension("cogs.malblock")
                            await bot.load_extension("cogs.help")
                            await bot.load_extension("cogs.user")
                            await bot.load_extension("cogs.mod")
                            await bot.load_extension("cogs.util")
                            await bot.load_extension("cogs.verify")

                            try:
                                if msg.split()[2] == "sync":
                                    await bot.tree.sync()
                                    await message.channel.send(content="Commands Synced!")
                            except:
                                pass

                            await message.channel.send(content="All Cogs Reloaded!")

                except: 
                    await message.channel.send(f"Hello! I'm {bot.user.mention}! for commands, type in `/help`! `{round(bot.latency * 1000)}ms`")

    # Create Guild Data
    async def on_guild_join(self, guild):
        with open(r"guildsettings.json", "r") as f:
            gs = json.load(f)

        if not str(guild.id) in gs:
            gs[str(guild.id)] = {}
            gs[str(guild.id)]["verifiedrole"] = "Verified"
            gs[str(guild.id)]["welcomemessage"] = ""
            gs[str(guild.id)]["bannedIds"] = []
            gs[str(guild.id)]["malblock"] = True
            gs[str(guild.id)]["agereq"] = 0
        else:
            pass

        with open(r"guildsettings.json", "w") as f:
            json.dump(gs, f, indent=4)

        print(f"VeriBlox has been invited to {guild.name} ({len(bot.guilds):,})!")

    # Auto Verification
    async def on_member_join(self, member):
        with open(r"verifystatus.json", "r") as f:
            self.vs = json.load(f)
        
        self.discordid = str(member.id)

        try:
            self.vs[self.discordid]
        except:
            return

        if self.vs[self.discordid]["verified"] == True:
            id = self.vs[self.discordid]["robloxid"]
            user = requests.get(f"https://users.roblox.com/v1/users/{id}").json()

            with open(r"guildsettings.json", "r") as f:
                gs = json.load(f)

            created = user["created"]
            try:
                creationdate = datetime.fromisoformat(created[:-1] + '+00:00').timestamp()
            except:
                creationdate = datetime.strptime(created,"%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            
            if gs[str(member.guild.id)]["agereq"] != 0:
                if time.time() - creationdate < gs[str(member.guild.id)]["agereq"]:
                    return await member.send("Your roblox account has been verified to VeriBlox! but unfortunately, your **Roblox Account** is not elegible to join this server since it does not meet the account age requirement. If you have an older roblox account, please use that one instead!")

            guild = str(member.guild.id)
            print(guild)
            try:
                with open(r"guildsettings.json", "r") as f:
                    gs = json.load(f)
                rolename = gs[guild]["verifiedrole"]
                role = discord.utils.get(member.guild.roles, name=rolename)
                await member.add_roles(role)
            except:
                await member.send("I could not give you the verified role since the role is higher than mine, or the **Server Owner** / **Server Moderator** haven't set one. Please contact a **Server Moderator** to fix bot permissions!")

            rbusername = user["name"]
            rbdispname = user["displayName"]
            
            if member.id == member.guild.owner_id:
                pass
            
            else:
                if rbusername == rbdispname:
                    try:
                        await member.edit(nick=f"{rbusername}")
                    except commands.MissingPermissions:
                        pass
                else:
                    u = f"{rbdispname} - @{rbusername}"
                    
                    if len(u) >= 31:
                        await member.edit(nick=f"{rbusername}")
                    
                    else:
                        try:
                            await member.edit(nick=f"{rbdispname} - @{rbusername}")
                        except commands.MissingPermissions:
                            pass

            if gs[str(member.guild.id)]["welcomemessage"] != "":
                await member.send(gs[str(member.guild.id)]["welcomemessage"])
 
            print(f"Verified {member.id} on {member.guild.name}")

bot = PersistentViewBot()

@bot.tree.command(name="setup", description="Creates a verification category")
@app_commands.describe(verifiedrole = "The role you want to be set as verified role")
async def setup(interaction: Interaction, verifiedrole : discord.Role):
    with open(r"guildsettings.json", "r") as f:
        gs = json.load(f)

    try:
        str(interaction.guild.id)
    except:
        embed = discord.Embed(description="**You can't run this command on DMs!**")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(content="You do not have a proper permission to do that!\nPermission Needed: ``manage_channels``", ephemeral=True)
    
    if verifiedrole == interaction.guild.default_role:
        return await interaction.response.send_message(content="You can't set the Verified Role as the default role! (@everyone)", ephemeral=True)

    try:
        guild = bot.get_guild(interaction.guild.id) 
    except:
        return await interaction.response.send_message(content="You can't run this command in **DMs**!")
    
    if not discord.utils.get(interaction.guild.roles, name=verifiedrole.name):
        return await interaction.response.send_message(content=f"I could not find the role {verifiedrole}.", ephemeral=True)
    else:
        verified = discord.utils.get(interaction.guild.roles, name=verifiedrole.name)
        gs[str(interaction.guild.id)]["verifiedrole"] = verifiedrole.name

    with open(r"guildsettings.json", "w") as f:
        json.dump(gs, f, indent=4)

    overwrite = discord.PermissionOverwrite()
    overwrite.view_channel = False

    overwritedefault = discord.PermissionOverwrite()
    overwritedefault.view_channel = True
    overwritedefault.send_messages = False
    
    category = await guild.create_category("VeriBlox Verification")
    verifychannel = await guild.create_text_channel('verify', category=category)
    embed=discord.Embed(title="VeriBlox Verification", description="This server is a **Roblox Server**. to verify, you will need an **Roblox Account** to verify your **Discord Account** to gain full access to this server!")
    embed_inst=discord.Embed(title="VeriBlox Verification Instructions", description="**Step 1**: Click on **Start Verification** and type in your **Roblox Username** and click on **Submit**\n**Step 2**: Click on **Get Verification Code** and go to your **Roblox Profile Page** and place the verification code in your **Roblox Description / About Me**\n**Step 3**: Click on **Verify Account** to gain full access to this server!")
    await verifychannel.send(embeds=[embed, embed_inst], view=persistentVerify())
    await category.set_permissions(verified, overwrite=overwrite)
    await category.set_permissions(guild.default_role, overwrite=overwritedefault)
    await interaction.response.send_message(content="Verification category and channel created! to change the verified role, use the command ``/verifiedrole RoleNameHere``.\nMake sure the verified role is below my role to fully verify a user!", ephemeral=True)

@bot.tree.error
async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)
        if int(h) == 0 and int(m) == 0:
            embed = discord.Embed(description=f"**⏱️ | `/{interaction.command.name}` is currently on cooldown. Please try again in {int(s)} seconds.**")
        elif int(h) == 0 and int(m) != 0:
            embed = discord.Embed(description=f"**⏱️ | `/{interaction.command.name}` is currently on cooldown. Please try again in {int(m)} minutes and {int(s)} seconds.**")
        else:
            embed = discord.Embed(description=f"**⏱️ | `/{interaction.command.name}` is currently on cooldown. Please try again in {int(h)} hours {int(m)} minutes and {int(s)} seconds.**")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if isinstance(error, discord.HTTPException):
        embed = discord.Embed(description=f"**⚠️ | There was an error while using the command `/{interaction.command.name}`. Please try again later!**")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if isinstance(error, discord.GatewayNotFound):
        bot.connect(reconnect=True)

    if isinstance(error, discord.NotFound):
        return

    raise error

try:
    #from webserver import keep_alive
    #keep_alive()
    bot.run(os.environ["token"])
except discord.HTTPException:
    print("Re-run Bot")
    os.system("kill 1")
