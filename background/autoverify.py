import discord
import discord.ext.commands as commands

from random import choice, randint

import time as btime
from packages.Logging import log
from datetime import datetime, time
from packages.HookLogging import sendLog
from packages.RobloxAPI import getInfo, getMembership
from packages.DataEdit import getUserData, getUserList, getGuildData, editUserData

def gen():
    words = open(r"conf/verification.txt", "r").read().splitlines()
    code = ""

    for x in range(randint(4, 20)):
        code += choice(words)
        if x != 11: code += " "
    
    return code

class autoverify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.id in getUserList():
            robloxUser = getInfo(int(getUserData(member.id)[1]), True)
            userID = member.id
            guildID = member.guild.id
            guildData = getGuildData(guildID)

            if guildData[6] == 0:
                return await member.send(f"The server you joined, **{member.guild.name}** has VeriBlox Auto-Verification turned off. Please verify manually!")

            try:
                try:
                    creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                except:
                    creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            except:
                creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

            if guildData[5] != 0:
                if round(btime.time()) - creationDate < guildData[5]:
                    embed = discord.Embed(title="Verification Failed")
                    embed.description = "Your Roblox Account is not old enough to be Verified in this server. please Retry Verification by using an older account!"
                    return await member.send(embed=embed)

            try:
                role = discord.utils.get(member.guild.roles, id=guildData[1])
            except:
                embed = discord.Embed(title="Verification Failed")
                embed.description = "There was an unexpected error while getting the Verified Role for this Server. please Retry Verification!"
                return await member.send(embed=embed)

            try:
                await member.add_roles(role)
            except discord.Forbidden:
                embed = discord.Embed(title="Verification Failed")
                embed.description = "I couldn't Verify you in the Server since i don't have the proper permission to give you one. Please contact a Server Moderator who can fix this issue and Retry Verification!"
                return await member.send(embed=embed)
            except discord.HTTPException:
                embed = discord.Embed(title="Verification Failed")
                embed.description = "There was an error that wouldn't allow me to give you the Verified Role. please Retry Verification!"
                return await member.send(embed=embed)
            except:
                embed = discord.Embed(title="Verification Failed")
                embed.description = "There was an unexpected error while giving you the Verified Role for this server. please Retry Verification!"
                return await member.send(embed=embed)

            if guildData[7] != 0:
                if getMembership(robloxUser):
                    if guildData[8] != 0:
                        try: role = discord.utils.get(member.guild.roles, id=guildData[8])
                        except: pass

                        try: await member.add_roles(role)
                        except: pass

            if member.guild.me.guild_permissions.manage_nicknames:
                nameFormat = getGuildData(member.guild.id)[9]
                robloxUserName = robloxUser["username"]
                robloxDisplayName = robloxUser["displayname"]
                robloxUserId = robloxUser["id"]

                nameFormat = nameFormat.replace("<robloxUsername>", robloxUserName)
                nameFormat = nameFormat.replace("<robloxDisplay>", robloxDisplayName)
                nameFormat = str(nameFormat).replace("<robloxId>", str(robloxUserId))
                nameFormat = nameFormat.replace("<discordUsername>", member.name)

                if member.id == member.guild.owner_id: pass
                
                try:
                    if len(nameFormat) >= 33: await member.edit(nick=robloxUserName)
                    else: await member.edit(nick=nameFormat)
                except: pass

                if guildData[2] != "":
                    await member.send(f"Message from **{member.guild.name}**\n" + guildData[2])

                if member.id == member.guild.owner_id:
                    embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                    await member.send(content=None, embed=embed, view=None)
                else:
                    embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!")
                    await member.send(content=None, embed=embed, view=None)
            
            log(f"Automatically verified {member} to VeriBlox!")
            sendLog(f"Automatically verified {member} to VeriBlox!")

async def setup(bot) -> None:
    await bot.add_cog(autoverify(bot))
