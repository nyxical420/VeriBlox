import discord
import discord.ext.commands as commands
from discord.ext.commands import GroupCog
import discord.app_commands as app_commands

from typing import Optional
from packages.RobloxAPI import getInfo
from packages.DataEdit import getGuildData, getUserData, editGuildData

@app_commands.guild_only()
@app_commands.default_permissions(ban_members=True)
class ban(GroupCog, name="ban"):

    @app_commands.command(name="member", description="Bans a Member from the server")
    @app_commands.describe(member = "The member to ban", reason = "The reasaon of the ban")
    async def ban_member(self, interaction: discord.Interaction, member : discord.Member, reason : Optional[str] = "No reason provided."):
        if not interaction.guild.me.guild_permissions.ban_members:
            embed = discord.Embed(description="**⚠️ | VeriBlox is missing the following permission:**\n`ban_members`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.ban_members:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`ban_members`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if member.guild_permissions.ban_members:
            embed = discord.Embed(description=f"**🚫 | Unable to ban {member.mention} since they are a Moderator in this server.**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.defer(thinking=True, ephemeral=True)
        banMessage = discord.Embed(title=f"You have been banned from {interaction.guild.name}", description=f"Reason: {reason}", color=0x2F3136)

        try: await member.send(embed=banMessage)
        except: pass

        await member.ban(reason=reason)
        await interaction.followup.send(f"**✅ | Successfully banned {member.mention} ({member.id}) from this server!**")

    @app_commands.command(name="roblox", description="Bans a Member including their Roblox Account from the server")
    @app_commands.describe(member = "The member to ban", reason = "The reasaon of the ban")
    async def ban_roblox(self, interaction: discord.Interaction, member : discord.Member, reason : Optional[str] = "No reason provided."):
        if not interaction.guild.me.guild_permissions.ban_members:
            embed = discord.Embed(description="**⚠️ | VeriBlox is missing the following permission:**\n`ban_members`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.ban_members:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`ban_members`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if member.guild_permissions.ban_members:
            embed = discord.Embed(description=f"**🚫 | Unable to ban {member.mention} since they are a Moderator in this server.**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.defer(thinking=True, ephemeral=True)
        banMessage = discord.Embed(title=f"You have been banned from {interaction.guild.name}", description=f"Reason: {reason}", color=0x2F3136)

        try: await member.send(embed=banMessage)
        except: pass

        editGuildData(interaction.guild.id, '"BannedIDS"', f'"{getGuildData(interaction.user.id) + " " + str(getUserData(member.id)[1])}"')
        await member.ban(reason=reason)
        await interaction.followup.send(f"**✅ | Successfully banned {member.mention} ({member.id}) and their Roblox Account from this server!**")

@app_commands.guild_only()
@app_commands.default_permissions(kick_members=True)
class kick(GroupCog, name="kick"):

    @app_commands.command(name="member", description="Kicks a Member from the server")
    @app_commands.describe(member = "The member to kick", reason = "The reasaon of the kick")
    async def kick_member(self, interaction: discord.Interaction, member : discord.Member, reason : Optional[str] = "No reason provided."):
        if not interaction.guild.me.guild_permissions.kick_members:
            embed = discord.Embed(description="**⚠️ | VeriBlox is missing the following permission:**\n`kick_members`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.kick_members:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`kick_members`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if member.guild_permissions.kick_members:
            embed = discord.Embed(description=f"**🚫 | Unable to kick {member.mention} since they are a Moderator in this server.**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.defer(thinking=True, ephemeral=True)
        kickMessage = discord.Embed(title=f"You have been kicked from {interaction.guild.name}", description=f"Reason: {reason}", color=0x2F3136)

        try: await member.send(embed=kickMessage)
        except: pass

        await member.kick(reason=reason)
        await interaction.followup.send(f"**✅ | Successfully kicked {member.mention} ({member.id}) from this server!**")

    @app_commands.command(name="roblox", description="Kicks a Member and bans their Roblox Account from the server")
    @app_commands.describe(member = "The member to kick", reason = "The reasaon of the kick")
    async def kick_roblox(self, interaction: discord.Interaction, member : discord.Member, reason : Optional[str] = "No reason provided."):
        if not interaction.guild.me.guild_permissions.kick_members:
            embed = discord.Embed(description="**⚠️ | VeriBlox is missing the following permission:**\n`kick_members`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.kick_members:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`kick_members`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if member.guild_permissions.kick_members:
            embed = discord.Embed(description=f"**🚫 | Unable to kick {member.mention} since they are a Moderator in this server.**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.defer(thinking=True, ephemeral=True)
        kickMessage = discord.Embed(title=f"You have been kicked from {interaction.guild.name}", description=f"Reason: {reason}", color=0x2F3136)

        try: await member.send(embed=kickMessage)
        except: pass

        editGuildData(interaction.guild.id, '"BannedIDS"', f'"{getGuildData(interaction.guild.id) + " " + str(getUserData(member.id)[1])}"')
        await member.kick(reason=reason)
        await interaction.followup.send(f"**✅ | Successfully kicked {member.mention} ({member.id}) and banned their Roblox Account from this server!**")

@app_commands.guild_only()
@app_commands.default_permissions(ban_members=True, kick_members=True)
class unban(GroupCog, name="unban"):

    @app_commands.command(name="id", description="Unbans a User from the server")
    @app_commands.describe(id = "The ID of the user to unban", reason = "The reason of the unban")
    async def unban_id(self, interaction: discord.Interaction, id: str, reason: Optional[str] = "No reason provided."):
        await interaction.response.defer(thinking=True)

        try:
            id = int(id)
        except:
            return await interaction.followup.send(f"**🚫 | Invalid Discord ID Passed**")

        banEntry = [entry async for entry in interaction.guild.bans(limit=5000)]
        
        for users in banEntry:
            print(users.user.id)
            if users.user.id == id:
                await interaction.guild.unban(user=users.user, reason=reason)
                return await interaction.followup.send(f"**✅ | Successfully unbanned {users.user} ({users.user.id}) from this server!**")

        await interaction.followup.send(f"**🚫 | Could not unban user with ID {id}**")

    @app_commands.command(name="user", description="Unbans a User from the server")
    @app_commands.describe(user = "The Name and Discriminator of the user to unban", reason = "The reason of the unban")
    async def unban_user(self, interaction: discord.Interaction, user: str, reason: Optional[str] = "No reason provided."):
        await interaction.response.defer(thinking=True)
        banEntry = [entry async for entry in interaction.guild.bans(limit=5000)]
        user_name, user_discriminator = user.split('#')

        for users in banEntry:
            if (users.user.name, users.user.discriminator) == (user_name, user_discriminator):
                await interaction.guild.unban(user=users.user, reason=reason)
                return await interaction.followup.send(f"**✅ | Successfully unbanned {users.user} ({users.user.id}) from this server!**")

        await interaction.followup.send(f"**🚫 | Could not unban user with Name and Discriminator {user}**")

    @app_commands.command(name="roblox", description="Unbans a Roblox Account from this server")
    @app_commands.describe(username="The username of the banned Roblox Account")
    async def unban_roblox(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(thinking=True)
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.followup.send(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`moderate_members`", color=0x2F3136)
            return await interaction.followup.send(embed=embed, ephemeral=True)

        gbu = getInfo(username)

        if gbu["success"] == False:
            embed = discord.Embed(description="**🚫 | This roblox account doesn't look like it's registered from Roblox.", color=0x2F3136)
            return await interaction.followup.send(embed=embed, ephemeral=True)

        if str(gbu["id"]) in getGuildData(interaction.guild.id)[3]:
            str(getGuildData(interaction.user.id)[3]).replace(str(gbu["id"]), "")
        else:
            embed = discord.Embed(description="**🚫 | This roblox account doesn't look like it's banned from this server.**", color=0x2F3136)
            return await interaction.followup.send(embed=embed, ephemeral=True)

        u = gbu["username"]
        embed = discord.Embed(description=f"**✅ | Successfully unbanned {u} from this server!", color=0x2F3136)
        await interaction.followup.send(embed=embed, ephemeral=True)

@app_commands.guild_only()
@app_commands.default_permissions(manage_guild=True, manage_roles=True)
class configuration(GroupCog, name="config"):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="welcomemessage", description="Sets the welcome message to this server")
    @app_commands.describe(message="The message you want to say to the new member in their DMs")
    async def welcomemessage(self, interaction: discord.Interaction, message: str):
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`manage_guild`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        editGuildData(interaction.guild.id, '"WelcomeMessage"', f'"{message}"')
        await interaction.response.send_message(content=f"Successfully set welcome message!\nHere's an preview of this server's welcome message.\n> {message}", ephemeral=True)

    @app_commands.command(name="verifiedrole", description="Sets the Verified Role to this server")
    @app_commands.describe(verifiedrole="The role you want to set as the Verified Role")
    async def verifiedrole(self, interaction: discord.Interaction, verifiedrole : discord.Role):    
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not interaction.user.guild_permissions.manage_roles:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`manage_roles`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if verifiedrole == interaction.guild.default_role:
            return await interaction.response.send_message(content="You can't set the Verified Role as the default role! (@everyone)", ephemeral=True)
        
        if not discord.utils.get(interaction.guild.roles, id=verifiedrole.id):
            return await interaction.response.send_message(content=f"There was an error while finding the role {verifiedrole}.", ephemeral=True)

        editGuildData(interaction.guild.id, '"VerifiedRole"', f'{verifiedrole.id}')
        await interaction.response.send_message(content=f"Set verified role to **{verifiedrole}**!", ephemeral=True)
    
    @app_commands.command(name="premiumrole", description="Sets the Premium Role to this server")
    @app_commands.describe(premiumrole="The role you want to set as the Premium Role")
    async def premiumrole(self, interaction: discord.Interaction, premiumrole : discord.Role):    
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not interaction.user.guild_permissions.manage_roles:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`manage_roles`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if premiumrole == interaction.guild.default_role:
            return await interaction.response.send_message(content="You can't set the Premium Role as the default role! (@everyone)", ephemeral=True)
        
        if not discord.utils.get(interaction.guild.roles, id=premiumrole.id):
            return await interaction.response.send_message(content=f"There was an error while finding the role {premiumrole}.", ephemeral=True)

        editGuildData(interaction.guild.id, '"PremiumRole"', f'{premiumrole.id}')
        await interaction.response.send_message(content=f"Set Premium Role to **{premiumrole}**!", ephemeral=True)
    
    @app_commands.command(name="premiumonly", description="Enables or Disables Premium-Only Verification")
    async def premiumonly(self, interaction: discord.Interaction):
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`manage_guild`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        data = getGuildData(interaction.guild.id)

        if data[7] == 1:
            editGuildData(interaction.guild.id, '"PremiumOnly"', '0')
            await interaction.response.send_message(content=f"Disabled **Premiun-Only Verification**.", ephemeral=True)
        else:
            editGuildData(interaction.guild.id, '"PremiumOnly"', '1')
            await interaction.response.send_message(content=f"Enabled **Premiun-Only Verification**!", ephemeral=True)

    @app_commands.command(name="accagereq", description="Changes the account age requirement to be fully verified on this server")
    @app_commands.describe(agereq="How many days does the roblox account needs to be fully verified.")
    @app_commands.choices(agereq=[
        app_commands.Choice(name='Disable', value=0), 
        app_commands.Choice(name='3 Days', value=1), 
        app_commands.Choice(name='1 Week', value=2), 
        app_commands.Choice(name='2 Weeks', value=3), 
        app_commands.Choice(name='3 Weeks', value=4), 
        app_commands.Choice(name='1 Month', value=5),
        app_commands.Choice(name='2 Months', value=6),
        app_commands.Choice(name='3 Months', value=7),
        app_commands.Choice(name='4 Months', value=8),
        app_commands.Choice(name='5 Months', value=9),
        app_commands.Choice(name='1 Year', value=10)
        ])
    async def accagereq(self, interaction: discord.Interaction, agereq: int):
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(content="You do not have proper permissions to do that!\nPermission Needed: ``manage_guild``", ephemeral=True)

        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(content="You do not have proper permissions to do that!\nPermission Needed: ``manage_guild``", ephemeral=True)

        if agereq == 0:
            editGuildData(interaction.guild.id, '"AgeRequirement"', '0')
            await interaction.response.send_message("Successfully disabled age requirement.", ephemeral=True)

        if agereq == 1:
            editGuildData(interaction.guild.id, '"AgeRequirement"', '259200')
            await interaction.response.send_message("Successfully set account age requirement to **3 Days**!", ephemeral=True)
            
        if agereq == 2:
            editGuildData(interaction.guild.id, '"AgeRequirement"', '604800')
            await interaction.response.send_message("Successfully set account age requirement to **1 week**!", ephemeral=True)
            
        if agereq == 3:
            editGuildData(interaction.guild.id, '"AgeRequirement"', '1209600')
            await interaction.response.send_message("Successfully set account age requirement to **2 Weeks**!", ephemeral=True)
            
        if agereq == 4:
            editGuildData(interaction.guild.id, '"AgeRequirement"', '1814400')
            await interaction.response.send_message("Successfully set account age requirement to **3 Weeks**!", ephemeral=True)

        if agereq == 5:
            editGuildData(interaction.guild.id, '"AgeRequirement"', '2678400')
            await interaction.response.send_message("Successfully set account age requirement to **1 Month**!", ephemeral=True)

        if agereq == 6:
            editGuildData(interaction.guild.id, '"AgeRequirement"', '5356800')
            await interaction.response.send_message("Successfully set account age requirement to **2 Months**!", ephemeral=True)
            
        if agereq == 7:
            editGuildData(interaction.guild.id, '"AgeRequirement"', '8035200')
            await interaction.response.send_message("Successfully set account age requirement to **3 Months**!", ephemeral=True)
            
        if agereq == 8:
            editGuildData(interaction.guild.id, '"AgeRequirement"', '10713600')
            await interaction.response.send_message("Successfully set account age requirement to **4 Months**!", ephemeral=True)
            
        if agereq == 9:
            editGuildData(interaction.guild.id, '"AgeRequirement"', '13392000')
            await interaction.response.send_message("Successfully set account age requirement to **5 Months**!", ephemeral=True)

        if agereq == 10:
            editGuildData(interaction.guild.id, '"AgeRequirement"', '31536000')
            await interaction.response.send_message("Successfully set account age requirement to **1 Year**!", ephemeral=True)

    @app_commands.command(name="autoverify", description="Enables or Disables VeriBlox Auto Verification")
    async def autoverify(self, interaction: discord.Interaction):
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`manage_guild`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        data = getGuildData(interaction.guild.id)

        if data[6] == 1:
            editGuildData(interaction.guild.id, '"AutoVerify"', '0')
            await interaction.response.send_message(content=f"Disabled **VeriBlox Auto-Verification**.", ephemeral=True)
        else:
            editGuildData(interaction.guild.id, '"AutoVerify"', '1')
            await interaction.response.send_message(content=f"Enabled **VeriBlox Auto-Verification**!", ephemeral=True)

@app_commands.guild_only()
@app_commands.default_permissions(manage_guild=True)
class server(commands.Cog):
    @app_commands.command(name="malblock", description="Enables or Disables VeriBlox Malicious Roblox Link Blocking")
    async def malblock(self, interaction: discord.Interaction):    
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`manage_guild`", color=0x2F3136)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        data = getGuildData(interaction.guild.id)

        if data[4] == 1:
            editGuildData(interaction.guild.id, '"MalBlock"', '0')
            await interaction.response.send_message(content=f"Disabled **VeriBlox Malicious Roblox Link Blocking**.", ephemeral=True)
        else:
            editGuildData(interaction.guild.id, '"MalBlock"', '1')
            await interaction.response.send_message(content=f"Enabled **VeriBlox Malicious Roblox Link Blocking**!", ephemeral=True)

async def setup(bot) -> None:
    await bot.add_cog(ban(bot))
    await bot.add_cog(unban(bot))
    await bot.add_cog(kick(bot))
    await bot.add_cog(configuration(bot))
    await bot.add_cog(server(bot))