import discord
import discord.ui as ui
from discord import app_commands
from discord.ext import commands

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

class helpmenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Shows commands for VeriBlox")
    async def help(self, interaction : discord.Interaction):
        cmds = discord.Embed(title="VeriBlox Commands")
        cmds.add_field(name="User Commands", value="`/verify` - Verifies or updates your Discord Account with your Roblox Account!\n`/whois` - Views the member's Roblox Profile\n`/avatar` - Shows the member's Roblox Avatar\n`/search` - Search for a Roblox User\n`/invite` - Gives the Invite Link for VeriBlox\n`/deletedata`- Deletes all of your data to VeriBlox", inline=False)
        cmds.add_field(name="Moderator Commands", value="`/kick` - Kicks the user from this server\n`/ban` - Bans the user from this server\n`/unban` - Unbans a Roblox Account from this server", inline=False)
        cmds.add_field(name="Server Configuration Commands", value="`/setup` - Creates a verification channel\n`/verifiedrole` - Sets the verified role to this the server\n`/welcomemessage` - Sets the welcome message to the server\n`/malblock` - Enables or Disables **VeriBlox Malicious Roblox Link Blocking**", inline=False)

        await interaction.response.send_message(embed=cmds)

async def setup(bot) -> None:
  await bot.add_cog(helpmenu(bot))