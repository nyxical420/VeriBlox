from discord import app_commands, Interaction, ButtonStyle, TextStyle, utils, Embed
from discord.ui import Button, View, Modal, TextInput
from discord.ext import commands
from datetime import datetime
from requests import get
from DataTools import *
from time import time
from random import choice
from asyncio import sleep

class verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="verify", description="Verifies your Discord Account with your Roblox Account on VeriBlox")
    async def verify(self, interaction : Interaction):
        self.refreshData(userid=interaction.user.id)

        try:
            str(interaction.guild.id)
        except:
            embed = Embed(description="**You can't run this command on DMs!**")
            return await interaction.followup.send(embed=embed)

        data = self.vs_Read_Data()
        self.discordid = str(interaction.user.id)

        class verification(Modal, title="VeriBlox Verification"):
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
            username = TextInput(label=f"Roblox Username (Case Sensitive)", style=TextStyle.short, min_length=3, max_length=20)

            async def on_submit(self, interaction: Interaction):
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

                    view = View()

                    getcode = Button(label="Verification Code", style=ButtonStyle.green)
                    regencode = Button(label="Regenerate Code", style=ButtonStyle.grey)
                    verify = Button(label="Verify Account", style=ButtonStyle.green)

                    async def getverificationcode(interaction):
                        class verification_code(Modal, title="VeriBlox Verification Code"):
                            verification = TextInput(label=f"Verification Code (Copy)", style=TextStyle.long, default=data[self.discordid]["verifykey"], max_length=len(data[self.discordid]["verifykey"]))

                            async def on_submit(self, interaction: Interaction):
                                await interaction.response.defer()
                        
                        await interaction.response.send_modal(verification_code())

                    async def regverificationcode(interaction):
                        keyg = f"{choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)} {choice(self.words)}"
                        data[self.discordid]["verifykey"] = keyg
                        appendUserData(data)
                        regencode.label = "Regenerate Code"
                        regencode.style = ButtonStyle.red
                        regencode.disabled = True
                        await interaction.response.edit_message(view=view)
                        await sleep(30)
                        regencode.label = "Regenerate Code"
                        regencode.style = ButtonStyle.grey
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
                                role = utils.get(interaction.guild.roles, name=rolename)
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
                                    try:
                                        try:
                                            await interaction.user.edit(nick=f"{rbdispname} - @{rbusername}")
                                        except:
                                            pass
                                    except:
                                        try:
                                            await interaction.user.edit(nick=f"{rbusername}")
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
                                embed = Embed(description=f"Successfully Verified as **{rbusername} ({rbdispname})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                                await interaction.response.send_message(embed=embed, view=None, ephemeral=True)
                            else:
                                embed = Embed(description=f"Successfully Verified as **{rbusername} ({rbdispname}])!**")
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
                role = utils.get(interaction.guild.roles, name=rolename)
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
                embed = Embed(description="**Successfully updated information!**\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                await interaction.response.send_message(embed=embed, view=None)
            else:
                embed = Embed(description="**Successfully updated information!**")
                await interaction.response.send_message(embed=embed)

        else:
            await interaction.response.send_modal(verification())
    
async def setup(bot) -> None:
  await bot.add_cog(verify(bot))