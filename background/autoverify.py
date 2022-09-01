import discord
import discord.ext.commands as commands

from packages.Logging import log
from packages.vCodeGen import gen
from datetime import datetime, time
from packages.HookLogging import sendLog
from packages.RobloxAPI import getInfo, getMembership
from packages.DataEdit import getUserData, getUserList, getGuildData, editUserData

class autoverify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.id in getUserList():
            robloxUser = getInfo(int(getUserData[1]))
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
                if time() - creationDate < guildData[5]:
                    return await member.send(content="**🚫 | This Roblox Account is not Elegible to be in this server. Please use another Roblox Account that's older than this Roblox Account!**")

            if guildData[7] != 0:
                if getMembership(robloxUser):
                    if guildData[8] != 0:
                        try: role = discord.utils.get(member.guild.roles, id=guildData[8])
                        except: pass
                        
                        try: await member.add_roles(role)
                        except: pass
                else:
                    return await member.send(content=f"**🚫 | You are required to have a Roblox Premium Membership to join {member.guild.name}!**")

            try:
                role = discord.utils.get(member.guild.roles, id=guildData[1])
            except:
                return await member.send(content="**🚫 | There was an Error while finding the Verified Role in this server.**")

            try:
                await member.add_roles(role)
            except:
                return await member.send(content="**🚫 | I couldn't give you the Verified Role since the role is higher than my Role Position. or i don't have the proper permission to give you one.**")

            if member.guild.me.guild_permissions.manage_nicknames:
                robloxUserName = robloxUser["username"]
                robloxDisplayName = robloxUser["displayname"]

                if member.id == member.guild.owner_id:
                    pass
                
                try:
                    if robloxUserName == robloxDisplayName:
                        await member.edit(nick=robloxDisplayName)
                    else:
                        if len(robloxUserName + robloxDisplayName) >= 32:
                            await member.edit(nick=robloxUserName)
                        else:
                            await member.edit(nick=f"{robloxDisplayName} - @{robloxUserName}")
                except: pass

                editUserData(userID, '"isVerified"', '"True"')
                editUserData(userID, '"RobloxID"', f'{robloxUser["id"]}')
                editUserData(userID, '"VerifyCode"', f'"{gen()}"')

                if guildData[2] != "":
                    await member.send(f"Message from **{member.guild.name}**\n" + guildData[2])

                if member.id == member.guild.owner.id:
                    embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                    await member.send(content=None, embed=embed, view=None)
                else:
                    embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!")
                    await member.send(content=None, embed=embed, view=None)
            
            log(f"Automatically verified {member} to VeriBlox!")
            sendLog(f"Automatically verified {member} to VeriBlox!")

async def setup(bot) -> None:
    await bot.add_cog(autoverify(bot))
