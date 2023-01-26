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
        cmds.add_field(name="User Commands", value="</verify:983662783692414996> - Verifies your Discord Account with your Roblox Account on VeriBlox\n"
                                                   "</whois:969191453987332164> - Displays the Member's Roblox Profile\n"
                                                   "</search user:984021096850403328> - Searches for a Roblox User by Name\n"
                                                   "</search userid:984021096850403328> - Searches for a Roblox User by ID\n"
                                                   "</search game:984021096850403328> - Searches for a Roblox Game by Name\n"
                                                   "</avatar:988404921260994560> - Displays the Member's Roblox Avatar\n"
                                                   "</invite:979342394677927987> - VeriBlox Invite\n"
                                                   "</stats:1014846512150356030> - Displays VeriBlox Stats\n"
                                                   "</data:1007992305686429776> - Displays a Preview of your VeriBlox Data", inline=False)
        
        cmds.add_field(name="Tools", value="</devex robux:1001709293625692260> - Converts Robux to a Real-Life Currency\n"
                                           "</devex currency:1001709293625692260> - Converts US Dollars to Robux\n"
                                           "</taxcalc:1003633887076950127> - Calculates Robux you need to get an Exact Price for an Item")

        cmds.add_field(name="Server Moderation", value="</ban member:997356118860906547> - Bans a Member from the Server\n"
                                                       "</ban roblox:997356118860906547> - Bans a Roblox Account from the Server by Name\n"
                                                       "</kick member:997356118860906549> - Kicks a Member from the Server\n"
                                                       "</kick roblox:997356118860906549> - Kicks a Roblox Account from the Server by Name\n"
                                                       "</unban user:997356118860906548> - Unbans a User from the Server by Name and Discriminator\n"
                                                       "</unban id:997356118860906548> - Unbans a User from the Server by User ID\n"
                                                       "</unban roblox:997356118860906548> - Unbans a Roblox Account from this Server by Name\n"
                                                       "</malblock:997462418563280916> - Enables VeriBlox MaLBlock", inline=False)

        cmds.add_field(name="Server Configuration", value="</config accagereq:997131796309356666> - Changes the Age Requirement for Roblox Accounts\n"
                                                          "</config verifiedrole:997131796309356666> - Changes the Verified Role from this Server\n"
                                                          #"</config premiumrole:997131796309356666> - Changes the Premium Role from this Server\n"
                                                          #"</config premiumonly:997131796309356666> - Enables or Disables Premium-Only Verification\n"
                                                          "</config welcomemessage:997131796309356666> - Changes the Welcome Message from this Server\n"
                                                          "</config autoverify:997131796309356666> - Enables or Disables Auto-Verification\n"
                                                          "</config format:997131796309356666> - Changes the name of a Member's Name in a format", inline=False)

        cmds.add_field(name="VeriBlox Server", value="If you want to hear new Updates from **VeriBlox**. or if you need help with something, you can [Join my Discord Server](https://discord.gg/EHNtECJRKA)!")

        await interaction.response.send_message(embed=cmds)

async def setup(bot) -> None:
    await bot.add_cog(helpmenu(bot))