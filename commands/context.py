import discord
import discord.ui as ui
import discord.ext.commands as commands
import discord.app_commands as app_commands

from packages.ImageGen import createRobloxInfo
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
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.followup.send(embed=embed)

        member = interaction.user if not user else user

        view = userView(interaction.user, timeout=300)

        try:
            data = getUserData(member.id)
            if data[3] == "False":
                return await interaction.followup.send(content=f"{member.mention} doesn't seem to be verified.")
        except:
            return await interaction.followup.send(content=f"{member.mention} doesn't seem to be verified.")

        uid = int(data[1])
        info = getInfo(uid)
        profile_button = ui.Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
        description = ui.Button(label="Show Description", style=discord.ButtonStyle.grey)
        delete = ui.Button(label="Delete", style=discord.ButtonStyle.red)

        async def deletewhois(interaction: discord.Interaction):
            await interaction.response.defer()
            try: await interaction.delete_original_message()
            except: pass
        
        async def showDescription(interaction: discord.Interaction):
            view.remove_item(profile_button)
            view.remove_item(description)
            view.remove_item(delete)
            await interaction.response.defer()
            await interaction.followup.send(content=info["description"], view=view, ephemeral=True)

        async def timeout():
            view.remove_item(delete)
            view.remove_item(description)
            try: await interaction.edit_original_response(view=view)
            except: return
                
        avatar = getAvatar("fullbody", uid, 3)
        id = createRobloxInfo(avatar, info)

        description.callback = showDescription
        delete.callback = deletewhois
        view.on_timeout = timeout
        view.add_item(profile_button)
        view.add_item(description)
        view.add_item(delete)
        await interaction.followup.send(file=discord.File(f"./assets/robloxImages/users/{id}/info.png"), view=view)

async def setup(bot) -> None:
    await bot.add_cog(Whois(bot))
