from discord.ext import commands
from requests import get
from discord import Embed
from json import load

class malblock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def gs_Read_Data(self):
        with open(r"guildsettings.json", "r") as f:
            return load(f)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        APIs = ["abtesting", "accountinformation", "accountsettings", "adconfiguration", "ads", 
                "api", "assetdelivery", "auth", "avatar", "badges", "billing", "catalog",
                "cdnproviders", "chat", "chatmoderation", "clientsettings", "clientsettingscdn",
                "contacts", "contentstore", "develop", "discussions", "economy", "economycreatorstats",
                "engagementpayouts", "followings", "friends", "gameinternationalization", "gamejoin",
                "gamepersistence", "games", "gamepasses", "groups", "groupsmoderation", "inventory",
                "itemconfiguration", "locale", "localizationtables", "metrics", "midas", "notifications",
                "points", "premiumfeatures", "presence", "privatemessages", "publish", "punishments",
                "search", "share", "textfilter", "thumbnails", "thumbnailsresizer", "trades", "translationroles",
                "translations", "twostepverification", "users", "usermoderation", "voice"]
                
        if message.author == self.bot.user:
            return

        if message.author.bot: 
            return
        
        data = self.gs_Read_Data()
        try:
            data[str(message.guild.id)]
        except:
            return
        
        if data[str(message.guild.id)]["malblock"] == True:
            s = str(message.content).lower().split()
            for x in range(len(s)):
                if "roblox" in s[x]:
                    embed = Embed(title=":warning: Compromised Link Detected", description=f"Looks like {message.author.mention} **({message.author.id})** sent an **Compromised Roblox Link** which could get your roblox account vunerable.\n\n**Link:** ||[{s[x]}](https://www.youtube.com/watch?v=bzXzGMbdQfY)||\n**Note: This link won't direct you to the compromised site to avoid users visiting the site.**")
                    try:
                        get(s[x], timeout=2)
                    except:
                        return
                    
                    # Roblox API Check
                    for api in range(len(APIs)):
                        if s[x].startswith(f"https://{APIs[api]}.roblox.com"):
                            return

                    if s[x].startswith("https://tenor.com"):
                        return
                    if s[x].startswith("http://tenor.com"):
                        return

                    if s[x].startswith("https://cdn.discordapp.com/"):
                        return
                    if s[x].startswith("http://cdn.discordapp.com/"):
                        return
                    
                    if s[x].startswith("https://github.com"):
                        return
                    if s[x].startswith("http://github.com"):
                        return
                    
                    if s[x].startswith("https://devforum.roblox.com"):
                        return
                    elif s[x].startswith("http://devforum.roblox.com"):
                        return

                    if s[x].startswith("https://roblox.com."):
                        await message.delete()
                        await message.channel.send(embed=embed)
                        return
                    elif s[x].startswith("http://roblox.com."):
                        await message.delete()
                        await message.channel.send(embed=embed)
                        return
                    else:
                        pass

                    if s[x].startswith("https://www.roblox.com."):
                        await message.delete()
                        await message.channel.send(embed=embed)
                        return
                    elif s[x].startswith("http://www.roblox.com."):
                        await message.delete()
                        await message.channel.send(embed=embed)
                        return
                    else:
                        pass

                    if s[x].startswith("https://web.roblox.com."):
                        await message.delete()
                        await message.channel.send(embed=embed)
                        return
                    elif s[x].startswith("http://web.roblox.com."):
                        await message.delete()
                        await message.channel.send(embed=embed)
                        return
                    else:
                        pass
                        
                    if s[x].startswith("https://ro.blox.com."):
                        await message.delete()
                        await message.channel.send(embed=embed)
                        return
                    elif s[x].startswith("http://ro.blox.com."):
                        await message.delete()
                        await message.channel.send(embed=embed)
                        return
                    else:
                        pass

                    if s[x].startswith("https://roblox.com"):
                        return
                    elif s[x].startswith("http://roblox.com"):
                        return
                    else:
                        pass

                    if s[x].startswith("https://www.roblox.com"):
                        return
                    elif s[x].startswith("http://www.roblox.com"):
                        return
                    else:
                        pass

                    if s[x].startswith("https://web.roblox.com"):
                        return
                    elif s[x].startswith("http://web.roblox.com"):
                        return 
                    else:
                        pass
                    
                    if s[x].startswith("https://ro.blox.com"):
                        return
                    elif s[x].startswith("http://ro.blox.com"):
                        return 
                    else:
                        await message.delete()
                        await message.channel.send(embed=embed)
                        return

async def setup(bot) -> None:
  await bot.add_cog(malblock(bot))