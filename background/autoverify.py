import discord
import discord.ext.commands as commands

from packages.Logging import log
from packages.vCodeGen import gen
from datetime import datetime, time
from packages.RobloxAPI import getInfo
from packages.HookLogging import sendLog
from packages.DataTools import readUserData, readGuildData, appendUserData

class autoverify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = await readUserData()

        if str(member.id) in data:
            robloxUser = getInfo(int(data[str(member.id)]["robloxid"]))
            userID = str(member.id)
            guildID = str(member.guild.id)
            vs, gs = await readUserData(), await readGuildData()

            if gs[guildID]["auto"] == False:
                return await member.send(f"The server you joined, **{member.guild.name}** has VeriBlox Auto-Verification turned off. Please verify manually!")

            try:
                try:
                    creationDate = datetime.fromisoformat(robloxUser["created"][:-1] + "+00:00").timestamp()
                except:
                    creationDate = datetime.strptime(robloxUser["created"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            except:
                creationDate = datetime.fromisoformat(robloxUser["created"].split('.')[0]).timestamp()

            if gs[guildID]["agereq"] != 0:
                if time() - creationDate < gs[guildID]["agereq"]:
                    return await member.send(content="**🚫 | This Roblox Account is not Elegible to be in this server. Please use another Roblox Account that's older than this Roblox Account!**")

            try:
                role = discord.utils.get(member.guild.roles, id=gs[guildID]["verifiedrole"])
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

                vs[userID]["verified"] = True
                vs[userID]["displayname"] = robloxDisplayName
                vs[userID]["verifykey"] = gen()
                await appendUserData(vs)

                if gs[guildID]["welcomemessage"] != "":
                    await member.send(gs[guildID]["welcomemessage"])

                if member.id == member.guild.owner_id:
                    embed = discord.Embed(description=f"Successfully Verified as {robloxUserName} ({robloxDisplayName})**!\nSince your the **Server Owner**, I am unable to edit your nickname since this is a restriction by **Discord**. This will still work to server members.")
                    await member.send(embed=embed)
                else:
                    embed = discord.Embed(description=f"Successfully Verified as **{robloxUserName} ({robloxDisplayName})**!")
                    await member.send(embed=embed)
            
            log(f"Automatically verified {member} to VeriBlox!")
            sendLog(f"Automatically verified {member} to VeriBlox!")

async def setup(bot) -> None:
    await bot.add_cog(autoverify(bot))