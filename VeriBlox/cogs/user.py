from discord.ui import Button, View
from discord import app_commands, Interaction
from discord.ext import commands
from datetime import datetime
from typing import Optional
import PyBloxAPI
import requests
import discord
import json

class userView(discord.ui.View):
    def __init__(self, user: discord.User, timeout: int = 600):
        super().__init__(timeout=timeout)
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user and interaction.user.id == self.user.id:
            return interaction.user and interaction.user.id == self.user.id
        else:
            await interaction.response.send_message(f"<@{self.user.id}> can only interact with this!", ephemeral=True)
    
    async def on_timeout(self):
        return await super().on_timeout()

class usercommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def vs_Read_Data(self):
        with open(r"verifystatus.json", "r") as f:
            return json.load(f)
    
    def vs_Append_Data(self, data : object):
        with open(r"verifystatus.json", "w") as f:
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

    @app_commands.command(name="whois", description="Views the mebmer's Roblox Profile")
    @app_commands.choices(moreinfo=[app_commands.Choice(name='False (Faster)', value="false"), app_commands.Choice(name='True', value="true")])
    @app_commands.describe(member="The member you want to view their Roblox Profile", moreinfo="Whenever to show more information of the user or not")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def whois(self, interaction : Interaction, moreinfo : str, member : Optional[discord.Member] = None):
        self.refreshData(userid=str(interaction.user.id))
        data = self.vs_Read_Data()

        await interaction.response.defer(thinking=True)
        
        if not str(interaction.user.id) in data:
            return await interaction.followup.send("Looks like you aren't verified to VeriBlox. Please verify to use this command!")
            
        try:
            str(interaction.guild.id)
        except:
            embed = discord.Embed(description="**You can't run this command on DMs!**")
            return await interaction.followup.send(embed=embed)

        member = interaction.user if not member else member
        member_id = str(member.id)
        view = userView(interaction.user, timeout=300)
        
        try:
            if data[member_id]["verified"] == False:
                await interaction.followup.send(content=f"{member.mention} doesn't seem to be verified.")
                return
        except:
            await interaction.followup.send(content=f"{member.mention} doesn't seem to be verified.")
            return

        async def deletewhois(interaction):
            await interaction.response.defer()
            try:
                await interaction.delete_original_message()
            except:
                pass
        
        async def timeout():
            view.remove_item(delete)
            try:
                await interaction.edit_original_message(view=view)
            except:
                return
                
        uid = data[member_id]["robloxid"]
        info = PyBloxAPI.getInfo(uid)
        status = PyBloxAPI.getOnlineStatus(uid)["status"]
        description = info["description"]

        profile_button = Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
        avatarimage = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={uid}&size=420x420&format=Png&isCircular=false").json()
        delete = Button(label="Delete", style=discord.ButtonStyle.red)

        s = f"{status}"
        
        if len(description) >= 1001:
            description = "Description could not be displayed since it exceeds more than **1000 characters**."

        if info["banned"] == True:
            embed=discord.Embed(title=f"{member.name}'s Roblox Profile", description=f"**Banned**\n{description}", color=0xFF6961)
        else:
            if s.startswith("Online"):
                embed=discord.Embed(title=f"{member.name}'s Roblox Profile", description=f"**Online**\n{description}", color=0x00A2FF)
            if s.startswith("Playing"):
                embed=discord.Embed(title=f"{member.name}'s Roblox Profile", description=f"**Playing**\n{description}", color=0x02B757)
            if s.startswith("Creating"):
                embed=discord.Embed(title=f"{member.name}'s Roblox Profile", description=f"**Creating (On Studio)**\n{description}", color=0xF68802)
            if s.startswith("Offline"):
                embed=discord.Embed(title=f"{member.name}'s Roblox Profile", description=f"**Offline**\n{description}", color=0x202225)
            view.add_item(profile_button)

        try:
            try:
                creationdate = datetime.fromisoformat(info["created"][:-1] + '+00:00')
                embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
            except:
                creationdate = datetime.strptime(info["created"],"%Y-%m-%dT%H:%M:%S.%fZ")
                embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
        except:
            creationdate = datetime.fromisoformat(info["created"].split('.')[0])
            embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")

        embed.set_thumbnail(url=avatarimage["data"][0]["imageUrl"]) 
        embed.add_field(name="Roblox Username", value="**" + info["username"] + "**", inline=True)
        embed.add_field(name="Roblox Display Name", value="**" + info["displayname"] + "**", inline=True)
        embed.add_field(name="Roblox ID", value=f"**{uid}**", inline=True)

        if moreinfo == "true":
            count = PyBloxAPI.getCount(uid)
            embed.add_field(name="Friends", value="**" + count["friends"] + "/200**", inline=True)
            embed.add_field(name="Followers", value="**" + count["followers"] + "**", inline=True)
            embed.add_field(name="Following", value=("**" + count["following"] + "**"), inline=True)

        delete.callback = deletewhois
        view.on_timeout = timeout
        view.add_item(delete)
        await interaction.followup.send(embed=embed, view=view)
    
    @app_commands.command(name="avatar", description="Shows the member's Roblox Avatar")
    @app_commands.describe(member="The member you want to view their Roblox Avatar", viewtype="Type of view the camera you want to show", imageres="The resolution of the image")
    @app_commands.choices(viewtype=[app_commands.Choice(name='Headshot', value="headshot"), app_commands.Choice(name='Bustshot', value="bustshot"), app_commands.Choice(name='Fullbody', value="fullbody")])
    @app_commands.choices(imageres=[app_commands.Choice(name='150 x 150', value=0), app_commands.Choice(name='180 x 180', value=1), app_commands.Choice(name='352 x 352', value=2), app_commands.Choice(name='420 x 420', value=3), app_commands.Choice(name='720 x 720 (Headshot and Fullbody Only)', value=4)])
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def avatar(self, interaction : Interaction, member : Optional[discord.Member], viewtype : str, imageres : int):
        member = interaction.user if not member else member
        member_id = str(member.id)
        data = self.vs_Read_Data()

        if not str(interaction.user.id) in data:
            return await interaction.response.send_message("Looks like you aren't verified to VeriBlox. Please verify to use this command!")
            
        try:
            str(interaction.guild.id)
        except:
            embed = discord.Embed(description="**You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed)
        
        if viewtype == "bustshot":
            if imageres == 4:
                imageres = 3
                

        uid = data[member_id]["robloxid"]
        if imageres == 0:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (150 x 150)")
        if imageres == 1:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (180 x 180)")
        if imageres == 2:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (352 x 352)")
        if imageres == 3:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (420 x 420)")
        if imageres == 4:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (720 x 720)")

        embed.set_image(url=PyBloxAPI.getAvatar(type=viewtype, userid=int(uid), size=imageres))

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="search", description="Searches for a Roblox User")
    @app_commands.choices(search_type=[app_commands.Choice(name='Roblox Username', value="username"), app_commands.Choice(name='Roblox User ID', value="userid")])
    @app_commands.choices(moreinfo=[app_commands.Choice(name='False (Faster)', value="false"), app_commands.Choice(name='True', value="true")])
    @app_commands.describe(search_type="If you want to search for a Roblox User's Name or Id", search="The Username or User ID of the Roblox User you want to search", moreinfo="Whenever to show more information of the user or not")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def search(self, interaction : Interaction, search_type : str, search : str, moreinfo : str):
        self.refreshData(userid=str(interaction.user.id))

        await interaction.response.defer(thinking=True) 

        view = userView(interaction.user, timeout=300)

        if search_type == "username":
            gbu = requests.get(f"https://api.roblox.com/users/get-by-username?username={search}").json()

            try:
                if gbu["success"] == False:
                    return await interaction.followup.send(f"I couldn't find the user named **{search}**.")
            except:
                pass

            async def deletesearch(interaction):
                await interaction.response.defer()
                try:
                    await interaction.delete_original_message()
                except:
                    pass

            async def timeout():
                view.remove_item(delete)
                try:
                    await interaction.edit_original_message(view=view)
                except:
                    return

            uid = gbu["Id"]
            info = PyBloxAPI.getInfo(uid)
            status = PyBloxAPI.getOnlineStatus(uid)["status"]
            description = info["description"]

            profile_button = Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
            avatarimage = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={uid}&size=420x420&format=Png&isCircular=false").json()
            delete = Button(label="Delete", style=discord.ButtonStyle.red)

            s = f"{status}"

            if len(description) >= 1001:
                description = "Description could not be displayed since it exceeds more than **1000 characters**."

            if info["banned"] == True:
                embed=discord.Embed(title=info["username"] + f"'s Roblox Profile", description=f"**Banned**\n{description}", color=0xFF6961)
            else:
                if s.startswith("Online"):
                    embed=discord.Embed(title=info["username"] + f"'s Roblox Profile", description=f"**Online**\n{description}", color=0x00A2FF)
                if s.startswith("Playing"):
                    embed=discord.Embed(title=info["username"] + f"'s Roblox Profile", description=f"**Playing**\n{description}", color=0x02B757)
                if s.startswith("Creating"):
                    embed=discord.Embed(title=info["username"] + f"'s Roblox Profile", description=f"**Creating (On Studio)**\n{description}", color=0xF68802)
                if s.startswith("Offline"):
                    embed=discord.Embed(title=info["username"] + f"'s Roblox Profile", description=f"**Offline**\n{description}", color=0x202225)
                view.add_item(profile_button)

            try:
                try:
                    creationdate = datetime.fromisoformat(info["created"][:-1] + '+00:00')
                    embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
                except:
                    creationdate = datetime.strptime(info["created"],"%Y-%m-%dT%H:%M:%S.%fZ")
                    embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
            except:
                creationdate = datetime.fromisoformat(info["created"].split('.')[0])
                embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")

            embed.set_thumbnail(url=avatarimage["data"][0]["imageUrl"]) 
            embed.add_field(name="Roblox Username", value="**" + info["username"] + "**", inline=True)
            embed.add_field(name="Roblox Display Name", value="**" + info["displayname"] + "**", inline=True)
            embed.add_field(name="Roblox ID", value=f"**{uid}**", inline=True)

            if moreinfo == "true":
                count = PyBloxAPI.getCount(uid)
                embed.add_field(name="Friends", value="**" + count["friends"] + "/200**", inline=True)
                embed.add_field(name="Followers", value="**" + count["followers"] + "**", inline=True)
                embed.add_field(name="Following", value="**" + count["following"] + "**", inline=True)

            delete.callback = deletesearch
            view.on_timeout = timeout
            view.add_item(delete)
            await interaction.followup.send(embed=embed, view=view)

        if search_type == "userid":
            async def deletesearch(interaction):
                await interaction.response.defer()
                try:
                    await interaction.delete_original_message()
                except:
                    pass
                
            async def timeout():
                view.remove_item(delete)
                try:
                    await interaction.edit_original_message(view=view)
                except:
                    return

            info = PyBloxAPI.getInfo(int(search))
            status = PyBloxAPI.getOnlineStatus(int(search))["status"]
            description = info["description"]

            profile_button = Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{int(search)}/profile")
            try:
                avatarimage = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={int(search)}&size=420x420&format=Png&isCircular=false").json()
            except:
                pass
            delete = Button(label="Delete", style=discord.ButtonStyle.red)

            s = f"{status}"

            if len(description) >= 1001:
                description = "Description could not be displayed since it exceeds more than **1000 characters**."

            if info["banned"] == True:
                embed=discord.Embed(title=info["username"] + f"'s Roblox Profile", description=f"**Banned**\n{description}", color=0xFF6961)
            else:
                if s.startswith("Online"):
                    embed=discord.Embed(title=info["username"] + f"'s Roblox Profile", description=f"**Online**\n{description}", color=0x00A2FF)
                if s.startswith("Playing"):
                    embed=discord.Embed(title=info["username"] + f"'s Roblox Profile", description=f"**Playing**\n{description}", color=0x02B757)
                if s.startswith("Creating"):
                    embed=discord.Embed(title=info["username"] + f"'s Roblox Profile", description=f"**Creating (On Studio)**\n{description}", color=0xF68802)
                if s.startswith("Offline"):
                    embed=discord.Embed(title=info["username"] + f"'s Roblox Profile", description=f"**Offline**\n{description}", color=0x202225)
                view.add_item(profile_button)

            try:
                try:
                    creationdate = datetime.fromisoformat(info["created"][:-1] + '+00:00')
                    embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
                except:
                    creationdate = datetime.strptime(info["created"],"%Y-%m-%dT%H:%M:%S.%fZ")
                    embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
            except:
                creationdate = datetime.fromisoformat(info["created"].split('.')[0])
                embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")

            try:
                embed.set_thumbnail(url=avatarimage["data"][0]["imageUrl"]) 
            except:
                pass

            embed.add_field(name="Roblox Username", value="**" + info["username"] + "**", inline=True)
            embed.add_field(name="Roblox Display Name", value="**" + info["displayname"] + "**", inline=True)
            embed.add_field(name="Player ID", value=f"**{search}**", inline=True)

            if moreinfo == "true":
                count = PyBloxAPI.getCount(int(search))
                embed.add_field(name="Friends", value="**" + count["friends"] + "/200**", inline=True)
                embed.add_field(name="Followers", value="**" + count["followers"] + "**", inline=True)
                embed.add_field(name="Following", value="**" + count["following"] + "**", inline=True)

            delete.callback = deletesearch
            view.on_timeout = timeout
            view.add_item(delete)
            await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="invite", description="Gives the Invite Link for VeriBlox")
    async def invite(self, interaction : Interaction):
        self.refreshData(userid=str(interaction.user.id))
        view = View()

        vb_invite  = Button(label="Invite VeriBlox", style=discord.ButtonStyle.url, url="https://discord.com/api/oauth2/authorize?client_id=872081372162973736&permissions=1377007119382&scope=bot%20applications.commands")
        vb_support = Button(label="VeriBlox Support Server", style=discord.ButtonStyle.url, url="https://discord.gg/EHNtECJRKA")
        vb_topgg   = Button(label="VeriBlox Top.gg", style=discord.ButtonStyle.url, url="https://top.gg/bot/872081372162973736")

        embed = discord.Embed(title="VeriBlox Invite", description="Click the **Invite VeriBlox** button below to invite VeriBlox to your server!\n\nIf you want to support the development of **VeriBlox**, visit Veriblox's Top.gg page below by clicking the **VeriBlox Top.gg** button and vote!")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/872738889272537118/988339351807197254/dendy3.png")
        view.add_item(vb_invite)
        view.add_item(vb_support)
        view.add_item(vb_topgg)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="deletedata", description="Deletes all of your data from VeriBlox")
    async def deletedata(self, interaction : Interaction):
        data = self.vs_Read_Data()

        if not str(interaction.user.id) in data:
            return await interaction.response.send_message("Looks like you aren't verified to VeriBlox. Please verify to use this command!", ephemeral=True)

        view = View(timeout=60)

        delete_confirm = Button(label="Confirm Deletion", style=discord.ButtonStyle.red)
        delete_deny    = Button(label="Cancel Deletion", style=discord.ButtonStyle.gray)

        async def confirm(interaction):
            await interaction.response.defer()
            try:
                del data[str(interaction.user.id)]
                self.vs_Append_Data(data=data)
            except:
                return await interaction.edit_original_message(content="Failed to delete your data from VeriBlox.", view=None)

            await interaction.edit_original_message(content="Successfully deleted your data from VeriBlox!", view=None)

        async def deny(interaction):
            await interaction.response.defer()
            await interaction.edit_original_message(content="Data Deletion Cancelled.", view=None)
        
        async def timeout():
            await interaction.edit_original_message(view=None)

        delete_confirm.callback = confirm
        delete_deny.callback = deny
        view.on_timeout = timeout
        view.add_item(delete_confirm)
        view.add_item(delete_deny)
        await interaction.response.send_message(content="Are you sure you want to delete **all** of your data from VeriBlox?", view=view, ephemeral=True)

async def setup(bot) -> None:
  await bot.add_cog(usercommands(bot))