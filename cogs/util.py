from DataTools import readGuildData, appendGuildData
from discord import app_commands, Interaction
from discord import User, Embed, Role, utils
from discord.ext import commands
from discord.ui import View

class userView(View):
    def __init__(self, user: User, timeout: int = 600):
        super().__init__(timeout=timeout)
        self.user = user

    async def interaction_check(self, interaction: Interaction):
        if interaction.user and interaction.user.id == self.user.id:
            return interaction.user and interaction.user.id == self.user.id
        else:
            await interaction.response.defer()
    
    async def on_timeout(self):
        return await super().on_timeout()

class utilitycommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="welcomemessage", description="Sets the welcome message to this server")
    @app_commands.describe(message="The message you want to say to the new member in their DMs")
    async def welcomemessage(self, interaction: Interaction, message: str):
        try:
            guild = str(interaction.guild.id)
        except:
            embed = Embed(description="**You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(content="You do not have proper permissions to do that!\nPermission Needed: ``manage_guild``", ephemeral=True)

        data = readGuildData()

        data[guild]["welcomemessage"] = message
        appendGuildData(data=data)
         
        await interaction.response.send_message(content=f"Successfully set welcome message!\nHere's an preview of this server's welcome message.\n> {message}", ephemeral=True)

    @app_commands.command(name="verifiedrole", description="Sets the verified role to this server")
    @app_commands.describe(verifiedrole="The role you want to set as the Verified Role")
    async def verifiedrole(self, interaction: Interaction, verifiedrole : Role):    
        try:
            guild = str(interaction.guild.id)
        except:
            embed = Embed(description="**You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message(content="You do not have proper permissions to do that!\nPermission Needed: ``manage_roles``", ephemeral=True)
        
        if verifiedrole == interaction.guild.default_role:
            return await interaction.response.send_message(content="You can't set the Verified Role as the default role! (@everyone)", ephemeral=True)

        data = readGuildData()
        
        if not utils.get(interaction.guild.roles, name=verifiedrole.name):
            return await interaction.response.send_message(content=f"There was an error while finding the role {verifiedrole}.", ephemeral=True)

        data[guild]["verifiedrole"] = verifiedrole.name
        appendGuildData(data=data)
 
        await interaction.response.send_message(content=f"Set verified role to **{verifiedrole}**!", ephemeral=True)

    @app_commands.command(name="malblock", description="Enables or Disables VeriBlox Malicious Roblox Link Blocking")
    async def malblock(self, interaction: Interaction):    
        try:
            guild = str(interaction.guild.id)
        except:
            embed = Embed(description="**You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(content="You do not have proper permissions to do that!\nPermission Needed: ``manage_guild``", ephemeral=True)
        
        data = readGuildData()

        if data[guild]["malblock"] == True:
            data[guild]["malblock"] = False
            await interaction.response.send_message(content=f"Disabled **VeriBlox Malicious Roblox Link Blocking**.", ephemeral=True)
        else:
            data[guild]["malblock"] = True
            await interaction.response.send_message(content=f"Enabled **VeriBlox Malicious Roblox Link Blocking**!", ephemeral=True)

        appendGuildData(data=data)
 
    @app_commands.command(name="accagereq", description="Changes the account age requirement to be fully verified on this server")
    @app_commands.describe(agereq="How many days does the roblox account needs to be fully verified.")
    @app_commands.choices(agereq=[
        app_commands.Choice(name='Disable', value=0), 
        app_commands.Choice(name='3 days', value=1), 
        app_commands.Choice(name='1 week', value=2), 
        app_commands.Choice(name='2 weeks', value=3), 
        app_commands.Choice(name='3 weeks', value=4), 
        app_commands.Choice(name='1 month (Recommended)', value=5),
        app_commands.Choice(name='2 months', value=6),
        app_commands.Choice(name='3 months', value=7),
        app_commands.Choice(name='4 months', value=8),
        app_commands.Choice(name='5 months', value=9),
        app_commands.Choice(name='1 year', value=10)
        ])
    async def accagereq(self, interaction: Interaction, agereq: int):
        try:
            str(interaction.guild.id)
        except:
            embed = Embed(description="**You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(content="You do not have proper permissions to do that!\nPermission Needed: ``manage_guild``", ephemeral=True)

        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(content="You do not have proper permissions to do that!\nPermission Needed: ``manage_guild``", ephemeral=True)

        data = readGuildData()

        if agereq == 0:
            data[str(interaction.guild.id)]["agereq"] = 0
            appendGuildData(data=data)
            await interaction.response.send_message("Successfully disabled age requirement.", ephemeral=True)

        if agereq == 1:
            data[str(interaction.guild.id)]["agereq"] = 259200
            appendGuildData(data=data)
            await interaction.response.send_message("Successfully set account age requirement to **3 Days**!", ephemeral=True)
            
        if agereq == 2:
            data[str(interaction.guild.id)]["agereq"] = 604800
            appendGuildData(data=data)
            await interaction.response.send_message("Successfully set account age requirement to **1 week**!", ephemeral=True)
            
        if agereq == 3:
            data[str(interaction.guild.id)]["agereq"] = 1209600
            appendGuildData(data=data)
            await interaction.response.send_message("Successfully set account age requirement to **2 Weeks**!", ephemeral=True)
            
        if agereq == 4:
            data[str(interaction.guild.id)]["agereq"] = 1814400
            appendGuildData(data=data)
            await interaction.response.send_message("Successfully set account age requirement to **3 Weeks**!", ephemeral=True)

        if agereq == 5:
            data[str(interaction.guild.id)]["agereq"] = 2678400
            appendGuildData(data=data)
            await interaction.response.send_message("Successfully set account age requirement to **1 Month**!", ephemeral=True)

        if agereq == 6:
            data[str(interaction.guild.id)]["agereq"] = 5356800
            appendGuildData(data=data)
            await interaction.response.send_message("Successfully set account age requirement to **2 Months**!", ephemeral=True)
            
        if agereq == 7:
            data[str(interaction.guild.id)]["agereq"] = 8035200
            appendGuildData(data=data)
            await interaction.response.send_message("Successfully set account age requirement to **3 Months**!", ephemeral=True)
            
        if agereq == 8:
            data[str(interaction.guild.id)]["agereq"] = 10713600
            appendGuildData(data=data)
            await interaction.response.send_message("Successfully set account age requirement to **4 Months**!", ephemeral=True)
            
        if agereq == 9:
            data[str(interaction.guild.id)]["agereq"] = 13392000
            appendGuildData(data=data)
            await interaction.response.send_message("Successfully set account age requirement to **5 Months**!", ephemeral=True)

        if agereq == 10:
            data[str(interaction.guild.id)]["agereq"] = 31536000
            appendGuildData(data=data)
            await interaction.response.send_message("Successfully set account age requirement to **1 Year**!", ephemeral=True)

    @app_commands.command(name="permissioncheck", description="Checks VeriBlox's Server Permissions")
    async def permissioncheck(self, interaction: Interaction):
        ...

async def setup(bot) -> None:
  await bot.add_cog(utilitycommands(bot))