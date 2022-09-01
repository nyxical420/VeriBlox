import discord
import discord.ui as ui
import discord.ext.commands as commands
from discord.ext.commands import GroupCog
import discord.app_commands as app_commands

import os
import psutil
from typing import Optional
from datetime import datetime
from packages.DataEdit import deleteUserData, getUserData, getUserList
from packages.RobloxAPI import getInfo, getAvatar, getGame, getMembership

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

class commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.colors = {"Online": 0x00A2FF, "Playing": 0x02B757, "Creating": 0xF68802, "Offline": 0x2F3136, "Banned": 0xFF6961}
    
    @app_commands.command(name="stats", description="Shows Current VeriBlox Stats")
    async def stats(self, interaction: discord.Interaction):
        p = psutil.Process(os.getpid())
        embed = discord.Embed(title="VeriBlox Stats", description="Roblox Verification made Easy with VeriBlox!", color=0x2F3136)
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds):,} ({len(self.bot.users):,})")
        embed.add_field(name="Latetncy", value=f"{round(self.bot.latency * 1000)}ms")
        embed.add_field(name="Memory Usage", value=f"{str(p.memory_info().rss)[:2]}.{str(p.memory_info().rss)[2:-4]} MB | {p.memory_info().rss:,} KB")
        embed.add_field(name="Uptime", value=f"Online <t:{round(p.create_time())}:R>", inline=False)
        embed.add_field(name="Others", value=f"[**VeriBlox Discord Server**](https://discord.gg/EHNtECJRKA)\n[**Invite VeriBlox**](https://discord.com/api/oauth2/authorize?client_id=872081372162973736&permissions=1377007119382&scope=bot%20applications.commands)\n[**Github Repository (PyTsun/VeriBlox)**](https://github.com/PyTsun/VeriBlox)\n[**Top.gg Page**](https://top.gg/bot/872081372162973736)", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="whois", description="Views the mebmer's Roblox Profile")
    @app_commands.describe(member="The member you want to view their Roblox Profile")
    async def whois(self, interaction : discord.Interaction, member : Optional[discord.Member] = None):
        await interaction.response.defer(thinking=True)  

        if not interaction.user.id in getUserList():
            return await interaction.followup.send("Looks like you aren't verified to VeriBlox. Please verify to use this command!")
            
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.followup.send(embed=embed)

        member = interaction.user if not member else member

        view = userView(interaction.user, timeout=300)

        try:
            data = getUserData(member.id)
            if data[3] == "False":
                return await interaction.followup.send(content=f"{member.mention} doesn't seem to be verified.")
        except:
            return await interaction.followup.send(content=f"{member.mention} doesn't seem to be verified.")

        async def deletewhois(interaction):
            await interaction.response.defer()
            try: await interaction.delete_original_response()
            except: pass
        
        async def timeout():
            view.remove_item(delete)
            try: await interaction.edit_original_response(view=view)
            except: return
                
        uid = int(data[1])
        info = getInfo(uid)
        membership = getMembership(uid)
        status = info["status"]
        description = info["description"]

        profile_button = ui.Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
        avatarimage = getAvatar("fullbody", uid, 4)
        delete = ui.Button(label="Delete", style=discord.ButtonStyle.red)
        
        if len(description) >= 257:
            description = "Description could not be displayed since it exceeds more than **256 characters**."

        embed = discord.Embed()
        if info["banned"] == True:
            embed.title = info["username"] + "'s Roblox Profile"
            embed.description = f"**Banned**\n{description}"
            embed.color = 0xFF6961
        
        else:
            embed.title = info["username"] + "'s Roblox Profile"
            embed.description = f"**{status}**\n{description}"
            embed.color = self.colors[status]
            view.add_item(profile_button)

        if membership:
            embed.description = f"**{status} | Premium Member**\n{description}"

        try:
            try:
                creationdate = datetime.fromisoformat(info["created"][:-1] + '+00:00')
                embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
            except:
                creationdate = datetime.strptime(info["created"],"%Y-%m-%dT%H:%M:%S.%fZ")
                embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
        except:
            creationdate = datetime.fromisoformat(info["created"].split('.')[0])
            embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")

        embed.set_thumbnail(url=avatarimage)
        fr, fo, flw = info["count"][0], info["count"][1], info["count"][2]
        embed.add_field(name="Roblox Username", value="**" + info["username"] + "**", inline=True)
        embed.add_field(name="Roblox Display Name", value="**" + info["displayname"] + "**", inline=True)
        embed.add_field(name="Roblox ID", value=f"**{uid}**", inline=True)
        embed.add_field(name="Friends", value=f"**{fr}/200**", inline=True)
        embed.add_field(name="Followers", value=f"**{fo:,}**", inline=True)
        embed.add_field(name="Following", value=f"**{flw:,}**", inline=True)

        delete.callback = deletewhois
        view.on_timeout = timeout
        view.add_item(delete)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="avatar", description="Shows the member's Roblox Avatar")
    @app_commands.describe(member="The member you want to view their Roblox Avatar", viewtype="Type of view the camera you want to show", imageres="The resolution of the image")
    @app_commands.choices(viewtype=[app_commands.Choice(name='Headshot', value="headshot"), app_commands.Choice(name='Bustshot', value="bustshot"), app_commands.Choice(name='Fullbody', value="fullbody")])
    @app_commands.choices(imageres=[app_commands.Choice(name='150 x 150', value=0), app_commands.Choice(name='180 x 180', value=1), app_commands.Choice(name='352 x 352', value=2), app_commands.Choice(name='420 x 420', value=3), app_commands.Choice(name='720 x 720', value=4)])
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def avatar(self, interaction : discord.Interaction, member : Optional[discord.Member], viewtype : str, imageres : int):
        member = interaction.user if not member else member
        data = getUserData(member.id)

        if not interaction.user.id in getUserList():
            return await interaction.response.send_message("Looks like your not verified to VeriBlox. Please verify to use this command!")

        if not member.id in getUserList():
            return await interaction.response.send_message(f"{member.mention} doesn't seem to be verified on VeriBlox.")

        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed)
        
        if viewtype == "bustshot":
            if imageres == 4:
                imageres = 3

        uid = data[1]
        if imageres == 0:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (150 x 150)")
        if imageres == 1:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (180 x 180)")
        if imageres == 2:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (352 x 352)")
        if imageres == 3:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (420 x 420)")
        if imageres == 4:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (720 x 720)")

        embed.set_image(url=getAvatar(type=viewtype, userid=int(uid), size=imageres))

        await interaction.response.send_message(embed=embed)

    #@app_commands.command(name="archive", description="Creates an Archive of your Roblox Account")
    #@app_commands.checks.cooldown(1, 172800, key=lambda i: i.user.id)
    #async def archive(self, interaction: discord.Interaction):
    #    ...

    @app_commands.command(name="taxcalc", description="Calculates how many Robux you need to cover Roblox Tax")
    @app_commands.describe(amount="Amount of Robux to add Tax", ingame="Whenever the purchase is made inside a Roblox Game")
    @app_commands.choices(ingame=[app_commands.Choice(name='False', value="False"), app_commands.Choice(name='True', value="True")])
    async def taxcalc(self, interaction: discord.Interaction, amount: int, ingame: str = "False"):
        embed = discord.Embed(title="Robux Tax Calculator", color=0x2F3136)
        tax = 30 / 100
        earnings = 70 / 100

        if ingame == "True":
            tax = 40 / 100
            earnings = 60 / 100
            embed.set_footer(text="This is In-Game Purchase Tax!")

        embed.description = f"You will need **{amount + round(amount / earnings * tax):,} R$** to get **{amount:,} R$**.\nYou get **{round(amount * earnings):,} R$** without adding tax."
        await interaction.response.send_message(embed=embed)

    #@app_commands.command(name="status", description="Shows Roblox Status")

    @app_commands.command(name="invite", description="Gives the Invite Link for VeriBlox")
    async def invite(self, interaction : discord.Interaction):
        view = ui.View()
        
        vb_invite  = ui.Button(label="Invite VeriBlox", style=discord.ButtonStyle.url, url="https://discord.com/api/oauth2/authorize?client_id=872081372162973736&permissions=1377007119382&scope=bot%20applications.commands")
        vb_support = ui.Button(label="VeriBlox Support Server", style=discord.ButtonStyle.url, url="https://discord.gg/EHNtECJRKA")
        vb_topgg   = ui.Button(label="VeriBlox Top.gg", style=discord.ButtonStyle.url, url="https://top.gg/bot/872081372162973736")

        embed = discord.Embed(title="VeriBlox Invite", description="Click the **Invite VeriBlox** button below to invite VeriBlox to your server!\n\nIf you want to support the development of **VeriBlox**, visit Veriblox's Top.gg page below by clicking the **VeriBlox Top.gg** button and vote!")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/872738889272537118/988339351807197254/dendy3.png")
        view.add_item(vb_invite)
        view.add_item(vb_support)
        view.add_item(vb_topgg)
        await interaction.response.send_message(embed=embed, view=view)

    #@app_commands.command(name="devmode", description="Shows hidden VeriBlox Features")
    #async def devmode(interaction: discord.Interaction):
    #    embed = discord.Embed(title="VeriBlox DevMode")
    #    await interaction.response.send_message("")

    @app_commands.command(name="data", description="Shows a Preview of your current VeriBlox Data")
    async def deletedata(self, interaction : discord.Interaction):
        data = getUserData(interaction.user.id)

        if not interaction.user.id in data:
            return await interaction.response.send_message("Looks like you aren't verified to VeriBlox. Please verify to use this command!", ephemeral=True)

        view = ui.View(timeout=60)

        delete = ui.Button(label="Delete Data (No Confirmation)", style=discord.ButtonStyle.red)

        async def confirm(interaction):
            await interaction.response.defer()

            try:
                deleteUserData(interaction.user.id)
                await interaction.edit_original_response(content="Successfully deleted your data from VeriBlox!", view=None, embed=None)
            except:
                return await interaction.edit_original_response(content="Failed to delete your data from VeriBlox.", view=None, embed=None)
        
        async def timeout():
            await interaction.edit_original_response(view=None)

        delete.callback = confirm
        view.on_timeout = timeout
        view.add_item(delete)

        data = getUserData(interaction.user.id)
        rid = data[1]
        vcode = data[2]
        verified = data[3]
        exp = data[4]

        embed = discord.Embed(title="VeriBlox Data Preview", description=f"**Stored Data**\n```\n > Discord ID: {interaction.user.id}\n --> Roblox ID: {rid}\n --> VeriBlox Verification Code: {vcode}\n --> Verified (on VeriBlox): {verified}\n --> Data Expiration (Days): {exp}\n```")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class search(GroupCog, name="search"):
    def __init__(self, bot):
        self.bot = bot
        self.colors = {"Online": 0x00A2FF, "Playing": 0x02B757, "Creating": 0xF68802, "Offline": 0x2F3136, "Banned": 0xFF6961}

    @app_commands.command(name="user", description="Searches for a Roblox User by Username")
    @app_commands.describe(user="The Name of the Roblox User you want to search")
    async def search_user(self, interaction: discord.Interaction, user: str):
        await interaction.response.defer(thinking=True)
        view = userView(interaction.user, timeout=120)
        robloxUser = getInfo(user)

        if robloxUser["success"] == False:
            return await interaction.followup.send(f"I couldn't find the user with the Roblox Name **{user}**.")
        
        else:
            async def deletesearch(interaction):
                await interaction.response.defer()
                try:
                    await interaction.delete_original_response()
                except:
                    pass

            async def timeout():
                view.remove_item(delete)
                try:
                    await interaction.edit_original_response(view=view)
                except:
                    return

            uid = robloxUser["id"]
            info = getInfo(uid)
            membership = getMembership(uid)
            status = robloxUser["status"]
            description = info["description"]
            
            profile_button = ui.Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
            avatarimage = getAvatar("fullbody", uid, 4)
            delete = ui.Button(label="Delete", style=discord.ButtonStyle.red)

            if len(description) >= 257:
                description = "Description could not be displayed since it exceeds more than **256 characters**."
            
            embed = discord.Embed()
            if info["banned"] == True:
                embed.title = info["username"] + "'s Roblox Profile"
                embed.description = f"**Banned**\n{description}"
                embed.color = 0xFF6961
            
            else:
                embed.title = info["username"] + "'s Roblox Profile"
                embed.description = f"**{status}**\n{description}"
                embed.color = self.colors[status]
                view.add_item(profile_button)
            
            if membership:
                embed.description = f"**{status} | Premium Member**\n{description}"

            try:
                try:
                    creationdate = datetime.fromisoformat(info["created"][:-1] + '+00:00')
                    embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
                except:
                    creationdate = datetime.strptime(info["created"],"%Y-%m-%dT%H:%M:%S.%fZ")
                    embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
            except:
                creationdate = datetime.fromisoformat(info["created"].split('.')[0])
                embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")

            embed.set_thumbnail(url=avatarimage) 
            fr, fo, flw = info["count"][0], info["count"][1], info["count"][2]
            embed.add_field(name="Roblox Username", value="**" + info["username"] + "**", inline=True)
            embed.add_field(name="Roblox Display Name", value="**" + info["displayname"] + "**", inline=True)
            embed.add_field(name="Roblox ID", value=f"**{uid}**", inline=True)
            embed.add_field(name="Friends", value=f"**{fr}/200**", inline=True)
            embed.add_field(name="Followers", value=f"**{fo:,}**", inline=True)
            embed.add_field(name="Following", value=f"**{flw:,}**", inline=True)

            delete.callback = deletesearch
            view.on_timeout = timeout
            view.add_item(delete)
            await interaction.followup.send(embed=embed, view=view)
    
    @app_commands.command(name="userid", description="Searches for a Roblox User by Id")
    @app_commands.describe(userid="The Id of the Roblox User you want to search")
    async def search_userid(self, interaction: discord.Interaction, userid: int):
        await interaction.response.defer(thinking=True)
        view = userView(interaction.user, timeout=120)
        robloxUser = getInfo(userid)

        if robloxUser["success"] == False:
            return await interaction.followup.send(f"I couldn't find the user with the Roblox ID **{userid}**.")
        
        else:
            async def deletesearch(interaction):
                await interaction.response.defer()
                try:
                    await interaction.delete_original_response()
                except:
                    pass

            async def timeout():
                view.remove_item(delete)
                try:
                    await interaction.edit_original_response(view=view)
                except:
                    return

            uid = robloxUser["id"]
            info = getInfo(uid)
            membership = getMembership(uid)
            status = robloxUser["status"]
            description = info["description"]
            
            profile_button = ui.Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
            avatarimage = getAvatar("fullbody", uid, 4)
            delete = ui.Button(label="Delete", style=discord.ButtonStyle.red)

            if len(description) >= 257:
                description = "Description could not be displayed since it exceeds more than **256 characters**."
            
            embed = discord.Embed()
            if info["banned"] == True:
                embed.title = info["username"] + "'s Roblox Profile"
                embed.description = f"**Banned**\n{description}"
                embed.color = 0xFF6961
            
            else:
                embed.title = info["username"] + "'s Roblox Profile"
                embed.description = f"**{status}**\n{description}"
                embed.color = self.colors[status]
                view.add_item(profile_button)
            
            if membership:
                embed.description = f"**{status} | Premium Member**\n{description}"

            try:
                try:
                    creationdate = datetime.fromisoformat(info["created"][:-1] + '+00:00')
                    embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
                except:
                    creationdate = datetime.strptime(info["created"],"%Y-%m-%dT%H:%M:%S.%fZ")
                    embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")
            except:
                creationdate = datetime.fromisoformat(info["created"].split('.')[0])
                embed.set_footer(text=f"Account Created on {creationdate.strftime('%d %B, %Y')}")

            embed.set_thumbnail(url=avatarimage) 
            fr, fo, flw = info["count"][0], info["count"][1], info["count"][2]
            embed.add_field(name="Roblox Username", value="**" + info["username"] + "**", inline=True)
            embed.add_field(name="Roblox Display Name", value="**" + info["displayname"] + "**", inline=True)
            embed.add_field(name="Roblox ID", value=f"**{uid}**", inline=True)
            embed.add_field(name="Friends", value=f"**{fr}/200**", inline=True)
            embed.add_field(name="Followers", value=f"**{fo:,}**", inline=True)
            embed.add_field(name="Following", value=f"**{flw:,}**", inline=True)

            delete.callback = deletesearch
            view.on_timeout = timeout
            view.add_item(delete)
            await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="game", description="Searches for a Roblox Game by Name")
    @app_commands.describe(game="The Name of the Roblox Game you want to search")
    async def search_game(self, interaction: discord.Interaction, game: str):
        await interaction.response.defer(thinking=True)
        view = userView(interaction.user, timeout=120)
        game_ = getGame(game)
        
        if game_["success"] == False:
            return await interaction.followup.send(f"I couldn't find the Game with the Roblox Game Name **{game}**")

        embed = discord.Embed(title=game_["name"], description=game_["description"], color=0x2F3136)
        playing = game_["playing"]
        l, d = game_["l"], game_["d"]
        owner = game_["owner"]

        embed.add_field(name="Playing", value=f"**{playing:,}**")
        embed.add_field(name="Likes", value=f"**{l:,}**")
        embed.add_field(name="Dislikes", value=f"**{d:,}**")
        embed.set_thumbnail(url=game_["imageURL"])
        embed.set_footer(text=f"Game Owner: {owner}")

        await interaction.followup.send(embed=embed, view=view)
    
   #@app_commands.command(name="gameid", description="Searches for a Roblox Game by Id")
   #@app_commands.describe(gameid="The Id of the Roblox Game you want to search")
   #async def search_gameid(self, interaction: discord.Interaction, gameid: int):
   #    await interaction.response.defer(thinking=True)
   #    view = userView(interaction.user, timeout=120)
   #    game_ = getGame(gameid)
   #    
   #    if game_["success"] == False:
   #        return await interaction.followup.send(f"I couldn't find the Game with the Roblox Game ID **{gameid}**")

   #    embed = discord.Embed(title=game_["name"], description=game_["description"], color=0x2F3136)
   #    playing = game_["playing"]
   #    l, d = game_["l"], game_["d"]
   #    owner = game_["owner"]

   #    embed.add_field(name="Playing", value=f"**{playing:,}**")
   #    embed.add_field(name="Likes", value=f"**{l:,}**")
   #    embed.add_field(name="Dislikes", value=f"**{d:,}**")
   #    embed.set_thumbnail(url=game_["imageURL"])
   #    embed.set_footer(text=f"Game Owner: {owner}")

   #    await interaction.followup.send(embed=embed, view=view)

class devex(GroupCog, name="devex"):
    @app_commands.command(name="robux", description="Converts Robux to a Certain Type of Currency")
    @app_commands.describe(amount="Amount of Robux to Convert", currency="Type of Currency you want to convert")
    @app_commands.choices(currency=[
        app_commands.Choice(name="US Dollar", value="USD"),
        app_commands.Choice(name="Japanese Yen", value="YEN"),
        app_commands.Choice(name="Canadian Dollar", value="CAD"),
        app_commands.Choice(name="European Dollar", value="EUR"),
        app_commands.Choice(name="Philippine Peso", value="PHP")
        ])
    async def devex_robux(self, interaction: discord.Interaction, amount: int, currency: str = "USD"):
        robuxRate = 0.0035
        rates = {"YEN": 103.2426, "CAD": 1.2880, "EUR": 0.82268, "PHP": 48.3389}
        symb  = {"USD": "$", "YEN": "¥", "CAD": "$", "EUR": "€", "PHP": "₱"}
        
        currencyAmount = round(amount * robuxRate, 2)
        embed = discord.Embed(title="Roblox DevEx", color=0x2F3136)
        embed.set_footer(text=f"Current DevEx Rate: {robuxRate}")

        if currency != "USD":
            currencyAmount = round(currencyAmount * rates[currency], 2)

        if amount >= 999999999:
            embed.color = 0xFF6961
        
        currency = symb[currency]
        embed.description = f"**{amount:,} R$** converts to **{currencyAmount:,} {currency}**."

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="currency", description="Converts USD to Robux")
    @app_commands.describe(amount="Amount of USD to Convert")
    async def devex_currency(self, interaction: discord.Interaction, amount: int):
        robuxAmount = round(amount * 285.7143, 2)
        embed = discord.Embed(title="Roblox DevEx", color=0x2F3136)

        embed.description = f"**{amount:,} USD** converts to **{robuxAmount:,} R$**."
        embed.set_footer(text="Other currencies are currently not supported.")
        await interaction.response.send_message(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(commands(bot))
    await bot.add_cog(search(bot))
    await bot.add_cog(devex(bot))
