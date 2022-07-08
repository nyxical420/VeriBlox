import discord
import discord.ui as ui
from discord import app_commands
from discord.ext import commands

from requests import get
from asyncio import sleep
from random import choice
from datetime import datetime, time
from packages.DataTools import readUserData, readGuildData, appendUserData, refreshUserData

class verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="verify", description="Verifies your Discord Account with your Roblox Account on VeriBlox")
    async def verify(self, interaction : discord.Interaction):
        refreshUserData(userid=interaction.user.id)

        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed)

        data = readUserData()
        self.discordid = str(interaction.user.id)

        class verification(ui.Modal, title="VeriBlox Verification"):
            vs = readUserData()
            gs = readGuildData()

            words = ["verification", "verify", "veriblox", "roblox", "api",
                      "home", "interaction", "code", "cat", "dog",
                      "duck", "elephant", "lion", "tiger", "zebra", 
                      "panda", "frog", "bird", "eagle", "phone", 
                      "laptop", "computer", "console", "keyboard", "mouse", 
                      "screen", "watch", "camera", "movie", "backpack",
                      "cap", "speaker", "sunglasses", "fan", "mirror",
                      "gamepad", "tetris", "games", "avatar", "wireless"]
            discordid = str(interaction.user.id)
            username = ui.TextInput(label="Roblox Username")
            username = ui.TextInput(label="Roblox Username (Case Sensitive)", style=discord.TextStyle.short, min_length=3, max_length=20)

            async def on_submit(self, interaction: discord.Interaction):
                gbu = get(f"https://api.roblox.com/users/get-by-username?username={str(self.username)}").json()

                try:
                    if gbu["success"] == False:
                        return await interaction.response.send_message(content="This account doesn't appear to exist! Please check if there's any typo.", ephemeral=True)
                 
                except:
                    id = gbu["Id"]
                    user = get(f"https://users.roblox.com/v1/users/{id}").json()

                    if user["isBanned"] == True:
                        return await interaction.response.send_message(content=f"This roblox account appears to be banned. Please verify with another account if you have one!")

                    if id in self.gs[str(interaction.guild.id)]["bannedIds"]:
                        username = user["name"]
                        return await interaction.response.send_message(f"This roblox account **{username}** appears to be banned from this server.")

                    if not self.discordid in data:
                        keyg = f"{choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)}"
                        data[self.discordid] = {}
                        data[self.discordid]["username"] = user["name"]
                        data[self.discordid]["displayname"] = user["displayName"]
                        data[self.discordid]["robloxid"] = gbu["Id"]
                        data[self.discordid]["verifykey"] = keyg
                        data[self.discordid]["verified"] = False
                        data[self.discordid]["expiredAfter"] = 7

                        appendUserData(data)

                    view = ui.View()

                    getcode = ui.Button(label="Verification Code", style=discord.ButtonStyle.green)
                    regencode = ui.Button(label="Regenerate Code", style=discord.ButtonStyle.grey)
                    verify = ui.Button(label="Verify Account", style=discord.ButtonStyle.green)

                    async def getverificationcode(interaction):
                        class verification_code(ui.Modal, title="VeriBlox Verification Code"):
                            verification = ui.TextInput(label=f"Verification Code (Copy)", style=discord.TextStyle.long, default=data[self.discordid]["verifykey"], max_length=len(data[self.discordid]["verifykey"]))

                            async def on_submit(self, interaction: discord.Interaction):
                                await interaction.response.defer()
                        
                        await interaction.response.send_modal(verification_code())

                    async def regverificationcode(interaction):
                        keyg = f"{choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)}"
                        data[self.discordid]["verifykey"] = keyg
                        appendUserData(data)
                        regencode.label = "Regenerate Code"
                        regencode.style = discord.ButtonStyle.red
                        regencode.disabled = True
                        await interaction.response.edit_message(view=view)
                        await sleep(30)
                        regencode.label = "Regenerate Code"
                        regencode.style = discord.ButtonStyle.grey
                        regencode.disabled = False
                        await interaction.edit_original_message(view=view)

                    async def verifyuser(interaction):
                        id = data[self.discordid]["robloxid"]
                        user = get(f"https://users.roblox.com/v1/users/{id}").json()

                        if user["description"] == data[self.discordid]["verifykey"]:
                            guild = str(interaction.guild.id)

                            gs = readGuildData()

                            created = user["created"]
                            try:
                                try:
                                    creationdate = datetime.fromisoformat(created[:-1] + '+00:00').timestamp()
                                except:
                                    creationdate = datetime.strptime(created,"%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
                            except:
                                creationdate = datetime.fromisoformat(created.split('.')[0]).timestamp()

                            if gs[str(interaction.guild.id)]["agereq"] != 0:
                                if time() - creationdate < gs[str(interaction.guild.id)]["agereq"]:
                                    return await interaction.user.send("Unfortunately, your **Roblox Account** is not elegible to join this server since it does not meet the account age requirement. If you have an older roblox account, please use that one instead!")

                            try:
                                gs = readGuildData()
                                rolename = gs[guild]["verifiedrole"]
                                role = discord.utils.get(interaction.guild.roles, name=rolename)
                                await interaction.user.add_roles(role)
                            except:
                                return await interaction.response.send_message(content="I could not give you the verified role since the role is higher than mine, or the **Server Owner** / **Server Moderator** haven't set one. Please contact a **Server Moderator** to fix bot permissions!", ephemeral=True)

                            rbusername = user["name"]
                            rbdispname = user["displayName"]

                            if interaction.user.id == interaction.guild.owner_id:
                                pass
                            
                            try:
                                if rbusername == rbdispname:
                                    await interaction.user.edit(nick=rbusername)
                                else:
                                    if len(rbusername + rbdispname) >= 32:
                                        await interaction.user.edit(nick=rbusername)
                                    else:
                                        await interaction.user.edit(nick=f"{rbdispname} - @{rbusername}")
                            except:
                                pass

                            data[self.discordid]["verified"] = True
                            data[self.discordid]["displayname"] = rbdispname
                            keyg = f"{choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)}"
                            data[self.discordid]["verifykey"] = keyg

                            appendUserData(data)
                            
                            gs = readGuildData()

                            if gs[str(interaction.guild.id)]["welcomemessage"] != "":
                                user = self.bot.get_user(interaction.user.id)
                                await user.send(gs[str(interaction.guild.id)]["welcomemessage"])
                            
                            if interaction.user.id == interaction.guild.owner_id:
                                embed = discord.Embed(description=f"Successfully Verified as **{rbusername} ({rbdispname})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)
                            else:
                                embed = discord.Embed(description=f"Successfully Verified as **{rbusername} ({rbdispname}])!**")
                                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)
                            print(f"{interaction.user} Successfully verified to VeriBlox!")

                        else:
                            await interaction.response.send_message(content=f"Looks like you havent pasted the code in your **Roblox Description / About Me**. Change it and try again!", ephemeral=True)
                            return

                    getcode.callback = getverificationcode
                    regencode.callback = regverificationcode
                    verify.callback = verifyuser
                    view.add_item(getcode)
                    view.add_item(regencode)
                    view.add_item(verify)
                    id = data[self.discordid]["robloxid"]
                    user = get(f"https://users.roblox.com/v1/users/{id}").json()
                    rbusername = user["name"]
                    rbdispname = user["displayName"]
                    await interaction.response.send_message(content=f"**Account Found!** Verifying as **{rbusername} ({rbdispname}**)\n> You can only regenerate your verification code once every **30 seconds**.", view=view, ephemeral=True)

        if str(interaction.user.id) in data:
            id = data[self.discordid]["robloxid"]
            user = get(f"https://users.roblox.com/v1/users/{id}").json()

            guild = str(interaction.guild.id)

            gs = readGuildData()

            created = user["created"]
            try:
                try:
                    creationdate = datetime.fromisoformat(created[:-1] + '+00:00').timestamp()
                except:
                    creationdate = datetime.strptime(created,"%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            except:
                creationdate = datetime.fromisoformat(created.split('.')[0]).timestamp()

            if gs[str(interaction.guild.id)]["agereq"] != 0:
                if time() - creationdate < gs[str(interaction.guild.id)]["agereq"]:
                    return await interaction.user.send("Unfortunately, your **Roblox Account** is not elegible to join this server since it does not meet the account age requirement. If you have an older roblox account, please use that one instead!")

            try:
                gs = readGuildData()
                rolename = gs[guild]["verifiedrole"]
                role = discord.utils.get(interaction.guild.roles, name=rolename)
                await interaction.user.add_roles(role)
            except:
                return await interaction.response.send_message(content="I could not give you the verified role since the role is higher than mine, or the **Server Owner** / **Server Moderator** haven't set one. Please contact a **Server Moderator** to fix bot permissions!", ephemeral=True)

            rbusername = user["name"]
            rbdispname = user["displayName"]

            if interaction.guild.me.guild_permissions.manage_nicknames == True:
                if interaction.user.id == interaction.guild.owner_id:
                    pass
                
                try:
                    if rbusername == rbdispname:
                        await interaction.user.edit(nick=rbusername)
                    else:
                        if len(rbusername + rbdispname) >= 32:
                            await interaction.user.edit(nick=rbusername)
                        else:
                            await interaction.user.edit(nick=f"{rbdispname} - @{rbusername}")
                except: pass

            data = readUserData()

            data[self.discordid]["verified"] = True
            data[self.discordid]["displayname"] = rbdispname
            self.words = ["verification", "verify", "veriblox", "roblox", "api",
                      "home", "interaction", "code", "cat", "dog",
                      "duck", "elephant", "lion", "tiger", "zebra", 
                      "panda", "frog", "bird", "eagle", "phone", 
                      "laptop", "computer", "console", "keyboard", "mouse", 
                      "screen", "watch", "camera", "movie", "backpack",
                      "cap", "speaker", "sunglasses", "fan", "mirror",
                      "gamepad", "tetris", "games", "avatar", "wireless"]

            keyg = f"{choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)}"
            data[self.discordid]["verifykey"] = keyg

            appendUserData(data)
            
            gs = readGuildData()

            if interaction.user.id == interaction.guild.owner_id:
                embed = discord.Embed(description="**Successfully updated information!**\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")

            else:
                embed = discord.Embed(description="**Successfully updated information!**")

            try:
                await interaction.response.send_message(embed=embed, view=None)
            except AttributeError:
                pass

        else:
            await interaction.response.send_modal(verification())
    
async def setup(bot) -> None:
  await bot.add_cog(verify(bot))