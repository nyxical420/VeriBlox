import discord
from discord import app_commands
from discord.ext import commands

from requests import get
from typing import Optional
from packages.DataTools import readGuildData, readUserData, appendGuildData

class server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Bans a member from the server")
    @app_commands.describe(member = "The memeber to ban", ban_rblxaccount = "Ban the roblox account from the server", reason="The reasaon of the ban")
    @app_commands.choices(ban_rblxaccount = [app_commands.Choice(name='Yes', value="Yes"), app_commands.Choice(name='No', value="No")])
    async def ban(self, interaction: discord.Interaction, member : discord.Member, ban_rblxaccount : str, reason : Optional[str] = "No reason provided."):
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.guild.me.guild_permissions.ban_members:
            embed = discord.Embed(description="**⚠️ | VeriBlox is missing the following permission:**\n`ban_members`")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.ban_members:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`ban_members`")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if member.guild_permissions.ban_members:
            embed = discord.Embed(description=f"**🚫 | Unable to ban {member.mention} since they are a **Moderator / Admin** in this server.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.defer()
        kickMessage = discord.Embed(title=f"You have been banned from {interaction.guild.name}", description=f"Reason: {reason}")
        data = readGuildData()
        userdata = readUserData()

        try: await member.send(embed=kickMessage)
        except: pass

        await member.kick(reason=reason)

        if ban_rblxaccount == "No":
            embed = discord.Embed(description=f"**✅ | Successfully banned {member.name} ({member.id}) from this server!**\nReason:\n```\n{reason}\n```")
            await interaction.response.send_message(embed=embed)

        if ban_rblxaccount == "Yes":
            data[str(interaction.guild.id)]["bannedIds"].append(int(userdata[str(member.id)]["robloxid"]))
            embed = discord.Embed(description=f"**✅ | Successfully banned {member.name} ({member.id}) and their Roblox Account from this server!**\nReason:\n```\n{reason}\n```")
            appendGuildData(data=data)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kick", description="Kicks a member from the server")
    @app_commands.describe(member = "The memeber to kick", ban_rblxaccount = "Ban the roblox account from the server", reason="The reasaon of the kick")
    @app_commands.choices(ban_rblxaccount = [app_commands.Choice(name='Yes', value="Yes"), app_commands.Choice(name='No', value="No")])
    async def kick(self, interaction: discord.Interaction, member : discord.Member, ban_rblxaccount : str, reason : Optional[str] = "No reason provided."):
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.guild.me.guild_permissions.kick_members:
            embed = discord.Embed(description="**⚠️ | VeriBlox is missing the following permission:**\n`kick_members`")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.kick_members:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`kick_members`")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if member.guild_permissions.kick_members:
            embed = discord.Embed(description=f"**🚫 | Unable to kick {member.mention} since they are a **Moderator / Admin** in this server.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.defer()
        kickMessage = discord.Embed(title=f"You have been kicked from {interaction.guild.name}", description=f"Reason: {reason}")
        data = readGuildData()
        userdata = readUserData()

        try: await member.send(embed=kickMessage)
        except: pass

        await member.kick(reason=reason)
        if ban_rblxaccount == "No":
            embed = discord.Embed(description=f"**✅ | Successfully kicked {member.name} ({member.id}) from this server!**\nReason:\n```\n{reason}\n```")
            await interaction.followup.send(embed=embed)

        if ban_rblxaccount == "Yes":
            data[str(interaction.guild.id)]["bannedIds"].append(int(userdata[str(member.id)]["robloxid"]))
            embed = discord.Embed(description=f"**✅ | Successfully kicked {member.name} ({member.id}) and their Roblox Account from this server!**\nReason:\n```\n{reason}\n```")
            appendGuildData(data=data)
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="unban", description="Unbans a roblox account from this server")
    @app_commands.describe(username="The username of the banned roblox account")
    async def unban(self, interaction: discord.Interaction, username: str):
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(description="**⚠️ | You are missing the following permission:**\n`moderate_members`")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        gbu = get(f"https://api.roblox.com/users/get-by-username?username={username}").json()

        try:
            if gbu["success"] == False:
                embed = discord.Embed(description="**🚫 | This roblox account doesn't look like it's registered from Roblox.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            data = readGuildData()

            if gbu["Id"] in data[str(interaction.guild.id)]["bannedIds"]:
                data[str(interaction.guild.id)]["bannedIds"].remove(int(gbu["Id"]))
            else:
                embed = discord.Embed(description="**🚫 | This roblox account doesn't look like it's banned from this server.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            appendGuildData(data=data)
            u = gbu["Username"]
            embed = discord.Embed(description=f"**✅ | Successfully unbanned {u} from this server!")
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot) -> None:
    await bot.add_cog(server(bot))