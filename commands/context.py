import discord
import discord.ui as ui
import discord.ext.commands as commands
import discord.app_commands as app_commands

from datetime import datetime
from packages.RobloxAPI import getInfo, getAvatar
from packages.DataEdit import getUserData, getUserList

class userView(ui.View):
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

class Whois(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.colors = {"Online": 0x00A2FF, "Playing": 0x02B757, "Creating": 0xF68802, "Offline": 0x2F3136, "Banned": 0xFF6961}
        self.ctx_menu = app_commands.ContextMenu(name='Whois', callback=self.whois)
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    async def whois(self, interaction: discord.Interaction, user: discord.User) -> None:
        await interaction.response.defer(thinking=True)  

        if not interaction.user.id in getUserList():
            return await interaction.followup.send("Looks like you aren't verified to VeriBlox. Please verify to use this command!")
            
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**")
            return await interaction.followup.send(embed=embed)

        view = userView(interaction.user, timeout=300)

        try:
            data = getUserData(user.id)
            if data[3] == "False":
                return await interaction.followup.send(content=f"{user.mention} doesn't seem to be verified.")
        except:
            return await interaction.followup.send(content=f"{user.mention} doesn't seem to be verified.")

        async def deletewhois(interaction):
            await interaction.response.defer()
            try: await interaction.delete_original_response()
            except: pass
        
        async def timeout():
            view.remove_item(delete)
            try: await interaction.edit_original_response(view=view)
            except: return
                
        uid = data[1]
        info = getInfo(uid)
        status = info["status"]
        description = info["description"]

        profile_button = ui.Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
        avatarimage = getAvatar("fullbody", uid, 4)
        delete = ui.Button(label="Delete", style=discord.ButtonStyle.red)
        
        if len(description) >= 257:
            description = "Description could not be displayed since it exceeds more than **256 characters**."

        embed = discord.Embed()
        if info["banned"] == True:
            embed.title = info["username"] + "'s Roblox Profile"
            embed.description = f"**Banned**\n{description}"
            embed.color = 0xFF6961
        
        else:
            embed.title = info["username"] + "'s Roblox Profile"
            embed.description = f"**{status}**\n{description}"
            embed.color = self.colors[status]
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

        embed.set_thumbnail(url=avatarimage)
        fr, fo, flw = info["count"][0], info["count"][1], info["count"][2]
        embed.add_field(name="Roblox Username", value="**" + info["username"] + "**", inline=True)
        embed.add_field(name="Roblox Display Name", value="**" + info["displayname"] + "**", inline=True)
        embed.add_field(name="Roblox ID", value=f"**{uid}**", inline=True)
        embed.add_field(name="Friends", value=f"**{fr}/200**", inline=True)
        embed.add_field(name="Followers", value=f"**{fo:,}**", inline=True)
        embed.add_field(name="Following", value=f"**{flw:,}**", inline=True)

        delete.callback = deletewhois
        view.on_timeout = timeout
        view.add_item(delete)
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot) -> None:
    await bot.add_cog(Whois(bot))
