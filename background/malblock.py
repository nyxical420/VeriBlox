import discord
import discord.ext.commands as commands

from httpx import get
from json import load

from packages.Logging import log
from packages.HookLogging import sendLog
from packages.DataEdit import getGuildData

class malblock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(r"conf/whitelisted.json", "r") as f:
            data = load(f)

            self.whitelisted = data["whitelisted"]
            self.APIs = data["robloxAPIs"]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if message.author.bot: 
            return
        
        try: data = getGuildData(message.guild.id)
        except: return
        
        try: data[str(message.guild.id)]
        except: return
        
        if data[str(message.guild.id)]["malblock"] == True:
            s = str(message.content).lower().split()
            for x in range(len(s)):
                if "roblox" in s[x]:
                    try:
                        site = get(s[x], timeout=2)
                    except:
                        return
                    
                    malicious_hasperm = discord.Embed(title="⚠️ Malicious Link Detected", description=f"Looks like {message.author.mention} **({message.author.id})** sent an **Malicious Roblox Link** which could get your roblox account vunerable.\n\n**Link:** ||[{s[x]}](https://www.youtube.com/watch?v=bzXzGMbdQfY)|| (Status Code: {site.status_code})\n**Note: This link won't direct you to the malicious site to avoid users visiting the site.**")
                    
                    # Roblox API Check
                    for y in range(len(self.APIs)):
                        if s[x].startswith(f"https://{self.APIs[y]}.roblox.com"):
                            return

                    # Whitelist Check
                    for z in range(len(self.whitelisted)):
                        if s[x].startswith(f"https://{self.whitelisted[z]}"):
                            return log(f"Ignored Whitelisted Site: {s[x]}")

                    if s[x].startswith("https://roblox.com.") or s[x].startswith("http://roblox.com."):
                        try:
                            await message.delete()
                            await message.channel.send(embed=malicious_hasperm)
                            log(f"Link ({s[x]}) has been detected as a Malicious Link! Deleted.")
                            sendLog(f"Link ({s[x]}) has been detected as a Malicious Link! Deleted.")
                        except:
                            log(f"Link ({s[x]}) has been detected as a Malicious Link! Not Deleted. (Missing Permission)")
                            sendLog(f"Link ({s[x]}) has been detected as a Malicious Link! Not Deleted. (Missing Permission)")
                        return
                    else:
                        pass

                    if s[x].startswith("https://www.roblox.com.") or s[x].startswith("http://www.roblox.com."):
                        try:
                            await message.delete()
                            await message.channel.send(embed=malicious_hasperm)
                            log(f"Link ({s[x]}) has been detected as a Malicious Link! Deleted.")
                            sendLog(f"Link ({s[x]}) has been detected as a Malicious Link! Deleted.")
                        except:
                            log(f"Link ({s[x]}) has been detected as a Malicious Link! Not Deleted. (Missing Permission)")
                            sendLog(f"Link ({s[x]}) has been detected as a Malicious Link! Not Deleted. (Missing Permission)")
                        return
                    else:
                        pass

                    if s[x].startswith("https://web.roblox.com.") or s[x].startswith("http://web.roblox.com."):
                        try:
                            await message.delete()
                            await message.channel.send(embed=malicious_hasperm)
                            log(f"Link ({s[x]}) has been detected as a Malicious Link! Deleted.")
                            sendLog(f"Link ({s[x]}) has been detected as a Malicious Link! Deleted.")
                        except:
                            log(f"Link ({s[x]}) has been detected as a Malicious Link! Not Deleted. (Missing Permission)")
                            sendLog(f"Link ({s[x]}) has been detected as a Malicious Link! Not Deleted. (Missing Permission)")
                        return
                    else:
                        pass
                        
                    if s[x].startswith("https://ro.blox.com.") or s[x].startswith("http://ro.blox.com."):
                        try:
                            await message.delete()
                            await message.channel.send(embed=malicious_hasperm)
                            log(f"Link ({s[x]}) has been detected as a Malicious Link! Deleted.")
                            sendLog(f"Link ({s[x]}) has been detected as a Malicious Link! Deleted.")
                        except:
                            log(f"Link ({s[x]}) has been detected as a Malicious Link! Not Deleted. (Missing Permission)")
                            sendLog(f"Link ({s[x]}) has been detected as a Malicious Link! Not Deleted. (Missing Permission)")
                        return
                    else:
                        pass

                    if s[x].startswith("https://roblox.com"):
                        return
                    else:
                        pass

                    if s[x].startswith("https://www.roblox.com"):
                        return
                    else:
                        pass

                    if s[x].startswith("https://web.roblox.com"):
                        return
                    else:
                        pass
                    
                    if s[x].startswith("https://ro.blox.com"):
                        return
                    else:
                        try:
                            await message.delete()
                            await message.channel.send(embed=malicious_hasperm)
                            log(f"Link ({s[x]}) has been detected as a Malicious Link! Deleted.")
                            sendLog(f"Link ({s[x]}) has been detected as a Malicious Link! Deleted.")
                        except:
                            log(f"Link ({s[x]}) has been detected as a Malicious Link! Not Deleted. (Missing Permission)")
                            sendLog(f"Link ({s[x]}) has been detected as a Malicious Link! Not Deleted. (Missing Permission)")
                        return

async def setup(bot) -> None:
    await bot.add_cog(malblock(bot))
