from typing import Optional
from discord import app_commands, Interaction
from discord.ext import commands
import discord
import discord
import json
import requests

class modcommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def vs_Read_Data(self):
        with open(r"verifystatus.json", "r") as f:
            return json.load(f)
    
    def vs_Append_Data(self, data : object):
        with open(r"verifystatus.json", "w") as f:
            json.dump(data, f, indent=4)

    def gs_Read_Data(self):
        with open(r"guildsettings.json", "r") as f:
            return json.load(f)
    
    def gs_Append_Data(self, data : object):
        with open(r"guildsettings.json", "w") as f:
            json.dump(data, f, indent=4)
    
    @app_commands.command(name="ban", description="Bans a member from the server")
    @app_commands.describe(member = "The memeber to ban", ban_rblxaccount = "Ban the roblox account from the server", reason="The reasaon of the ban")
    @app_commands.choices(ban_rblxaccount = [app_commands.Choice(name='Yes', value="Yes"), app_commands.Choice(name='No', value="No")])
    async def ban(self, interaction: Interaction, member : discord.Member, ban_rblxaccount : str, reason : Optional[str] = "No reason provided."):
        try:
            str(interaction.guild.id)
        except:
            embed = discord.Embed(description="**You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.ban_members:
            return await interaction.response.send_message(content="You do not have proper permissions to do that!\nPermission Needed: ``ban_members``", ephemeral=True)

        if member.guild_permissions.ban_members:
            return await interaction.response.send_message(content=F"Unable to ban {member.mention} since they are an **Moderator / Admin** on this server.", ephemeral=True)

        banMessage = discord.Embed(title=f"You have been banned from {interaction.guild.name}", description=f"Reason: {reason}")
        data = self.gs_Read_Data()
        userdata = self.vs_Read_Data()

        if ban_rblxaccount == "No":
            try:
                await member.ban(reason=reason)
            except:
                return await interaction.response.send_message(f"Failed to ban {member.mention}. Make sure that i have proper permissions to ban members! or that my role is higher than the user's role.")
                
            try:
                await member.send(embed=banMessage)
            except:
                pass

            await interaction.response.send_message(f"Successfully banned **{member.name} ({member.id})** from this server!\n> Reason: {reason}")

        if ban_rblxaccount == "Yes":
            try:
                await member.ban(reason=reason)
            except:
                return await interaction.response.send_message(f"Failed to ban {member.mention}. Make sure that i have proper permissions to ban members! or that my role is higher than the user's role.")

            try:
                await member.send(embed=banMessage)
            except:
                pass

            data[str(interaction.guild.id)]["bannedIds"].append(int(userdata[str(member.id)]["robloxid"]))
            await interaction.response.send_message(f"Successfully banned **{member.name} ({member.id})** and their roblox account from this server!\n> Reason: {reason}")
        self.gs_Append_Data(data=data)

    @app_commands.command(name="kick", description="Kicks a member from the server")
    @app_commands.describe(member = "The memeber to kick", ban_rblxaccount = "Ban the roblox account from the server", reason="The reasaon of the kick")
    @app_commands.choices(ban_rblxaccount = [app_commands.Choice(name='Yes', value="Yes"), app_commands.Choice(name='No', value="No")])
    async def kick(self, interaction: Interaction, member : discord.Member, ban_rblxaccount : str, reason : Optional[str] = "No reason provided."):
        try:
            str(interaction.guild.id)
        except:
            embed = discord.Embed(description="**You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.kick_members:
            return await interaction.response.send_message(content="You do not have proper permissions to do that!\nPermission Needed: ``kick_members``", ephemeral=True)

        if member.guild_permissions.kick_members:
            return await interaction.response.send_message(content=f"Unable to kick {member.mention} since they are an **Moderator / Admin** on this server.", ephemeral=True)

        kickMessage = discord.Embed(title=f"You have been kicked from {interaction.guild.name}", description=f"Reason: {reason}")
        data = self.gs_Read_Data()
        userdata = self.vs_Read_Data()

        if ban_rblxaccount == "No":
            try: 
                await member.kick(reason=reason)
            except: 
                return await interaction.response.send_message(f"Failed to kick {member.mention}. Make sure that i have proper permissions to kick members! or that my role is higher than the user's role.")

            try: 
                await member.send(embed=kickMessage)
            except: 
                pass

            await interaction.response.send_message(f"Successfully kicked **{member.name} ({member.id})** from this server!\n> Reason: {reason}")

        if ban_rblxaccount == "Yes":
            try:
                await member.kick(reason=reason)
            except:
                return await interaction.response.send_message(f"Failed to kick {member.mention}. Make sure that i have proper permissions to kick members! or that my role is higher than the user's role.")
            
            try:
                await member.send(embed=kickMessage)
            except:
                pass

            data[str(interaction.guild.id)]["bannedIds"].append(int(userdata[str(member.id)]["robloxid"]))
            await interaction.response.send_message(f"Successfully kicked **{member.name} ({member.id})** and banned their roblox account from this server!\n> Reason: {reason}")
        
        self.gs_Append_Data(data=data)

    @app_commands.command(name="unban", description="Unbans a roblox account from this server")
    @app_commands.describe(username="The username of the banned roblox account")
    async def unban(self, interaction: Interaction, username: str):
        try:
            str(interaction.guild.id)
        except:
            embed = discord.Embed(description="**You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.moderate_members:
            return await interaction.response.send_message(content="You do not have proper permissions to do that!\nPermission Needed: ``moderate_members``", ephemeral=True)

        gbu = requests.get(f"https://api.roblox.com/users/get-by-username?username={username}").json()

        try:
            if gbu["success"] == False:
                await interaction.response.send_message(f"I couldn't find the user named **{username}**. Please check if there is any typo!")
        except:
            data = self.gs_Read_Data()
            if gbu["Id"] in data[str(interaction.guild.id)]["bannedIds"]:
                data[str(interaction.guild.id)]["bannedIds"].remove(int(gbu["Id"]))
            else:
                return await interaction.response.send_message("This roblox account doesn't look like it's banned from this server.")
            self.gs_Append_Data(data=data)
            u = gbu["Username"]
            await interaction.response.send_message(f"Successfully unbanned roblox user **{u}**, from this server!")
        

async def setup(bot) -> None:
  await bot.add_cog(modcommands(bot))