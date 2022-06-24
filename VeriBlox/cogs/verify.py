from discord.ui import Button, View, Modal, TextInput
from discord import app_commands, Interaction
from discord.ext import commands
from datetime import datetime
import requests
import discord
import asyncio
import random
import json
import time

class verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def vs_Read_Data(self):
        with open(r"verifystatus.json", "r") as f:
            return json.load(f)
        
    def gs_Read_Data(self):
        with open(r"guildsettings.json", "r") as f:
            return json.load(f)
        
    def vs_Append_Data(self, data : object):
        with open(r"verifystatus.json", "w") as f:
            json.dump(data, f, indent=4)
    
    def gs_Append_Data(self, data : object):
        with open(r"guildsettings.json", "w") as f:
            json.dump(data, f, indent=4)
    
    def refreshData(self, userid : str):
        with open(r"verifystatus.json", "r") as f:
            data =  json.load(f)

        try:
            data[userid]["expiredAfter"] = 60
        except:
            return

        with open(r"verifystatus.json", "w") as f:
            json.dump(data, f, indent=4)

    @app_commands.command(name="verify", description="Verifies your Discord Account with your Roblox Account on VeriBlox")
    async def verify(self, interaction : Interaction):
        self.refreshData(userid=interaction.user.id)

        try:
            str(interaction.guild.id)
        except:
            embed = discord.Embed(description="**You can't run this command on DMs!**")
            return await interaction.followup.send(embed=embed)

        data = self.vs_Read_Data()
        self.discordid = str(interaction.user.id)

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

                    if id in self.gs[str(interaction.guild.id)]["bannedIds"]:
                        username = user["name"]
                        return await interaction.response.send_message(f"This roblox account **{username}** appears to be banned from this server.")

                    if not self.discordid in data:
                        keyg = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
                        data[self.discordid] = {}
                        data[self.discordid]["username"] = user["name"]
                        data[self.discordid]["displayname"] = user["displayName"]
                        data[self.discordid]["robloxid"] = gbu["Id"]
                        data[self.discordid]["verifykey"] = keyg
                        data[self.discordid]["verified"] = False
                        data[self.discordid]["expiredAfter"] = 7

                        with open(r"verifystatus.json", "w") as f:
                            json.dump(data, f, indent=4)

                    view = View()

                    getcode = Button(label="Verification Code", style=discord.ButtonStyle.green)
                    regencode = Button(label="Regenerate Code", style=discord.ButtonStyle.grey)
                    verify = Button(label="Verify Account", style=discord.ButtonStyle.green)

                    async def getverificationcode(interaction):
                        class verification_code(Modal, title="VeriBlox Verification Code"):
                            verification = TextInput(label=f"Verification Code (Copy)", style=discord.TextStyle.long, default=data[self.discordid]["verifykey"], max_length=len(data[self.discordid]["verifykey"]))

                            async def on_submit(self, interaction: discord.Interaction):
                                await interaction.response.defer()
                        
                        await interaction.response.send_modal(verification_code())

                    async def regverificationcode(interaction):
                        keyg = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
                        data[self.discordid]["verifykey"] = keyg
                        with open(r"verifystatus.json", "w") as f:
                            json.dump(data, f, indent=4)
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
                        id = data[self.discordid]["robloxid"]
                        user = requests.get(f"https://users.roblox.com/v1/users/{id}").json()

                        if user["description"] == data[self.discordid]["verifykey"]:
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
                            keyg = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
                            data[self.discordid]["verifykey"] = keyg

                            with open(r"verifystatus.json", "w") as f:
                                json.dump(data, f, indent=4)
                            
                            with open(r"guildsettings.json", "r") as f:
                                gs = json.load(f)

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
                    user = requests.get(f"https://users.roblox.com/v1/users/{id}").json()
                    rbusername = user["name"]
                    rbdispname = user["displayName"]
                    await interaction.response.send_message(content=f"**Account Found!** Verifying as **{rbusername} ({rbdispname}**)\n> You can only regenerate your verification code once every **30 seconds**.", view=view, ephemeral=True)

        if str(interaction.user.id) in data:
            id = data[self.discordid]["robloxid"]
            user = requests.get(f"https://users.roblox.com/v1/users/{id}").json()

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

            with open(r"verifystatus.json", "r") as f:
                data = json.load(f)

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
            keyg = f"{random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)} {random.choice(self.words)}"
            data[self.discordid]["verifykey"] = keyg

            with open(r"verifystatus.json", "w") as f:
                json.dump(data, f, indent=4)
            
            with open(r"guildsettings.json", "r") as f:
                gs = json.load(f)

            if interaction.user.id == interaction.guild.owner_id:
                embed = discord.Embed(description="**Successfully updated information!**\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                await interaction.response.send_message(embed=embed, view=None)
            else:
                embed = discord.Embed(description="**Successfully updated information!**")
                await interaction.response.send_message(embed=embed)

        else:
            await interaction.response.send_modal(verification())
    
async def setup(bot) -> None:
  await bot.add_cog(verify(bot))