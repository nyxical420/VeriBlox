import discord
import discord.ui as ui
import discord.app_commands as app_commands
import discord.ext.commands as commands

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
        cmds = discord.Embed(title="VeriBlox Commands", color=0x2F3136)
        cmds.add_field(name="User Commands", value="`/verify` - Starts Verification from VeriBlox\n"
                                                   "`/whois` - Shows the Member's Roblox Profile\n"
                                                   "`/search user` - Searches for a Roblox User by Name\n"
                                                   "`/search userid` - Searches for a Roblox User by ID\n"
                                                   "`/search game` - Searches for a Roblox Game by Name\n"
                                                   "`/avatar` - Shows the Member's Roblox Avatar\n"
                                                   "`/invite` - Gives an Invite Link for VeriBlox\n"
                                                   "`/stats` - Shows Current VeriBlox Stats\n"
                                                   "`/data` - Shows a Preview of your current VeriBlox Data", inline=False)
        
        cmds.add_field(name="Tools", value="`/devex robux` - Converts Robux to a Certain Type of Currency\n"
                                           "`/devex currency` - Converts USD to Robux\n"
                                           "`/taxcalc` - Calculates how many Robux you need to cover Roblox Tax")

        cmds.add_field(name="Server Moderation", value="`/ban member` - Bans a Member from the Server\n"
                                                       "`/ban roblox` - Bans a Roblox Account from the Server by Name\n"
                                                       "`/kick member` - Kicks a Member from the Server\n"
                                                       "`/kick roblox` - Kicks a Roblox Account from the Server by Name\n"
                                                       "`/unban user` - Unbans a User from the Server by Name and Discriminator\n"
                                                       "`/unban id` - Unbans a User from the Server by User ID\n"
                                                       "`/unban roblox` - Unbans a Roblox Account from this Server by Name\n"
                                                       "`/malblock` - Enables VeriBlox MaLBlock", inline=False)

        cmds.add_field(name="Server Configuration", value="`/config accagereq` - Changes the Age Requirement for Roblox Accounts\n"
                                                          "`/config verifiedrole` - Changes the Verified Role from this Server\n"
                                                          "`/config premiumrole` - Changes the Premium Role from this Server\n"
                                                          "`/config premiumonly` - Enables or Disables Premium-Only Verification\n"
                                                          "`/config welcomemessage` - Changes the Welcome Message from this Server\n"
                                                          "`/config autoverify` - Enables or Disables Auto-Verification", inline=False)

        cmds.add_field(name="VeriBlox Server", value="If you want to hear new Updates from **VeriBlox**. or if you need help with something, you can [Join my Discord Server](https://discord.gg/EHNtECJRKA)!")

        await interaction.response.send_message(embed=cmds)

async def setup(bot) -> None:
    await bot.add_cog(helpmenu(bot))