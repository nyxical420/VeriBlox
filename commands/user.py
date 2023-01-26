import discord
import discord.ui as ui
import discord.ext.commands as commands
from discord.ext.commands import GroupCog
import discord.app_commands as app_commands

import os
import psutil
from typing import Optional
from packages.HookLogging import sendLog
from packages.ImageGen import createRobloxInfo
from packages.RobloxAPI import getInfo, getAvatar, getGame
from packages.DataEdit import deleteUserData, getUserData, getUserList

class userView(ui.View):
    def __init__(self, user: discord.User, timeout: int = 600):
        super().__init__(timeout=timeout)
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user and interaction.user.id == self.user.id: return interaction.user and interaction.user.id == self.user.id
        else: await interaction.response.send_message(f"<@{self.user.id}> can only interact with this!", ephemeral=True)
    
    async def on_timeout(self):
        return await super().on_timeout()

class commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="stats", description="Displays VeriBlox Stats")
    async def stats(self, interaction: discord.Interaction):
        p = psutil.Process(os.getpid())
        embed = discord.Embed(title="VeriBlox Stats", description="Roblox Verification made Easy and Fast with VeriBlox!", color=0x2F3136)
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds):,} ({len(self.bot.users):,} Users)")
        embed.add_field(name="Latetncy", value=f"{round(self.bot.latency * 1000)}ms")

        mb = str(p.memory_info().rss/1000000).split(".")
        kb = str(p.memory_info().rss/1000).split(".")
        embed.add_field(name="Memory Usage", value=f"**{mb[0]} MB ({kb[0]} KB)**")
        embed.add_field(name="Uptime", value=f"Online <t:{round(p.create_time())}:R>", inline=False)
        embed.add_field(name="Others", value=f"**[Github Repository (PyTsun/VeriBlox)](https://github.com/PyTsun/VeriBlox)\n"
                                              "[VeriBlox Support Server](https://discord.gg/EHNtECJRKA)\n"
                                              "[VeriBlox Top.gg Page](https://top.gg/bot/872081372162973736)\n"
                                              "[Invite VeriBlox](https://discord.com/api/oauth2/authorize?client_id=872081372162973736&permissions=1377007119382&scope=bot%20applications.commands)**", inline=False)
        embed.set_footer(text="VeriBlox Version: v2.5")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="whois", description="Displays the Member's Roblox Profile")
    @app_commands.describe(member="The Roblox Profile of a Member you want to view")
    async def whois(self, interaction : discord.Interaction, member : Optional[discord.Member] = None):
        await interaction.response.defer(thinking=True)  

        if not interaction.user.id in getUserList():
            return await interaction.followup.send("You need your Roblox Account to be Verified on VeriBlox before you can use this Command!")
            
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.followup.send(embed=embed)

        member = interaction.user if not member else member

        view = userView(interaction.user, timeout=300)

        try:
            data = getUserData(member.id)
            if data[3] == "False":
                return await interaction.followup.send(content=f"{member.mention} isn't verified on VeriBlox.")
        except:
            return await interaction.followup.send(content=f"{member.mention} isn't verified on VeriBlox.")

        uid = int(data[1])
        info = getInfo(uid)
        profile_button = ui.Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
        description = ui.Button(label="Show Description", style=discord.ButtonStyle.grey)
        delete = ui.Button(label="Delete", style=discord.ButtonStyle.red)

        async def deletewhois(interaction: discord.Interaction):
            await interaction.response.defer()
            try: await interaction.delete_original_message()
            except: pass
        
        async def showDescription(interaction: discord.Interaction):
            view.remove_item(profile_button)
            view.remove_item(description)
            view.remove_item(delete)
            await interaction.response.defer()
            await interaction.followup.send(content=info["description"], view=view, ephemeral=True)

        async def timeout():
            view.remove_item(delete)
            view.remove_item(description)
            try: await interaction.edit_original_response(view=view)
            except: return
                
        avatar = getAvatar("fullbody", uid, 3)
        id = createRobloxInfo(avatar, info)

        description.callback = showDescription
        delete.callback = deletewhois
        view.on_timeout = timeout
        view.add_item(profile_button)
        view.add_item(description)
        view.add_item(delete)
        await interaction.followup.send(file=discord.File(f"./assets/robloxImages/users/{id}/info.png"), view=view)

    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.command(name="avatar", description="Displays the Member's Roblox Avatar")
    @app_commands.describe(member="The Roblox Avatar of a Member you want to view", viewtype="Type of View you want to Display their Roblox Avatar from", imageres="The Resolution of the Roblox Avatar you want to be displayed")
    @app_commands.choices(viewtype=[app_commands.Choice(name='Headshot', value="headshot"), app_commands.Choice(name='Bustshot', value="bustshot"), app_commands.Choice(name='Fullbody', value="fullbody")])
    @app_commands.choices(imageres=[app_commands.Choice(name='150 x 150', value=0), app_commands.Choice(name='180 x 180', value=1), app_commands.Choice(name='352 x 352', value=2), app_commands.Choice(name='420 x 420', value=3), app_commands.Choice(name='720 x 720', value=4)])
    async def avatar(self, interaction : discord.Interaction, member : Optional[discord.Member], viewtype : str, imageres : int):
        member = interaction.user if not member else member
        data = getUserData(member.id)

        if not interaction.user.id in getUserList():
            return await interaction.response.send_message("You need your Roblox Account to be Verified on VeriBlox before you can use this Command!")

        if not member.id in getUserList():
            return await interaction.response.send_message(f"{member.mention} doesn't look like to be verified on VeriBlox.")

        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**", color=0x2F3136)
            return await interaction.response.send_message(embed=embed)
        
        if viewtype == "bustshot":
            if imageres == 4:
                imageres = 3

        uid = data[1]
        if imageres == 0:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (150 x 150)", color=0x2F3136)
        if imageres == 1:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (180 x 180)", color=0x2F3136)
        if imageres == 2:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (352 x 352)", color=0x2F3136)
        if imageres == 3:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (420 x 420)", color=0x2F3136)
        if imageres == 4:
            embed = discord.Embed(title=f"{member}'s Roblox Avatar (720 x 720)", color=0x2F3136)

        embed.set_image(url=getAvatar(type=viewtype, userid=int(uid), size=imageres))

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="taxcalc", description="Calculates Robux you need to get an Exact Price for an Item")
    @app_commands.describe(amount="Amount of Robux your Item Sells from", ingame="Adds In-Game Tax when the transaction is made inside a Roblox Game")
    @app_commands.choices(ingame=[app_commands.Choice(name='False', value="False"), app_commands.Choice(name='True', value="True")])
    async def taxcalc(self, interaction: discord.Interaction, amount: int, ingame: str = "False"):
        embed = discord.Embed(title="Robux Tax Calculator", color=0x2F3136)
        tax = 30 / 100
        earnings = 70 / 100

        if ingame == "True":
            tax = 40 / 100
            earnings = 60 / 100
            embed.set_footer(text="This tax is In-Game tax.")

        embed.description = f"You will need **{amount + round(amount / earnings * tax):,} R$** to get **{amount:,} R$**.\nYou get **{round(amount * earnings):,} R$** without adding tax."
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite", description="VeriBlox Invite")
    async def invite(self, interaction : discord.Interaction):
        view = ui.View()
        
        vb_invite  = ui.Button(label="Invite VeriBlox", style=discord.ButtonStyle.url, url="https://discord.com/api/oauth2/authorize?client_id=872081372162973736&permissions=1377007119382&scope=bot%20applications.commands")
        vb_support = ui.Button(label="VeriBlox Support Server", style=discord.ButtonStyle.url, url="https://discord.gg/EHNtECJRKA")
        vb_topgg   = ui.Button(label="VeriBlox Top.gg", style=discord.ButtonStyle.url, url="https://top.gg/bot/872081372162973736")

        embed = discord.Embed(title="VeriBlox Invite", description="Click the **Invite VeriBlox** button below to invite VeriBlox to your server!\n\nIf you want to support the development of **VeriBlox**, visit Veriblox's Top.gg page below by clicking the **VeriBlox Top.gg** button and vote!", color=0x2F3136)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/872738889272537118/988339351807197254/dendy3.png")
        view.add_item(vb_invite)
        view.add_item(vb_support)
        view.add_item(vb_topgg)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="data", description="Displays a Preview of your VeriBlox Data")
    async def deletedata(self, interaction : discord.Interaction):
        data = getUserData(interaction.user.id)

        if not interaction.user.id in getUserList():
            return await interaction.response.send_message("You need your Roblox Account to be Verified on VeriBlox before you can use this Command!", ephemeral=True)

        view = ui.View(timeout=60)
        delete = ui.Button(label="Delete Data (No Confirmation)", style=discord.ButtonStyle.red)

        async def confirm(interaction: discord.Interaction):
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

        embed = discord.Embed(title="VeriBlox Data Preview", description=f"**Stored Data**\n```\n > Discord ID: {interaction.user.id}\n --> Roblox ID: {rid}\n --> VeriBlox Verification Code: {vcode}\n --> Verified (on VeriBlox): {verified}\n```", color=0x2F3136)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class search(GroupCog, name="search"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="user", description="Searches for a Roblox User by Username")
    @app_commands.describe(user="The Name of the Roblox User you want to search")
    async def search_user(self, interaction: discord.Interaction, user: str):
        await interaction.response.defer(thinking=True)
        view = userView(interaction.user, timeout=120)
        robloxUser = getInfo(user)

        if robloxUser["success"] == False:
            return await interaction.followup.send(f"I couldn't find the user with the Roblox Name **{user}**.")
        
        else:
            uid = robloxUser["id"]
            info = getInfo(uid)
            profile_button = ui.Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
            description = ui.Button(label="Show Description", style=discord.ButtonStyle.grey)
            delete = ui.Button(label="Delete", style=discord.ButtonStyle.red)

            async def deletesearch(interaction: discord.Interaction):
                await interaction.response.defer()
                try: await interaction.delete_original_message()
                except: pass

            async def showDescription(interaction: discord.Interaction):
                view.remove_item(profile_button)
                view.remove_item(description)
                view.remove_item(delete)
                await interaction.response.defer()
                await interaction.followup.send(content=info["description"], view=view, ephemeral=True)

            async def timeout():
                view.remove_item(delete)
                view.remove_item(description)
                try: await interaction.edit_original_response(view=view)
                except: return

            avatar = getAvatar("fullbody", uid, 3)
            createRobloxInfo(avatar, info)

            description.callback = showDescription
            delete.callback = deletesearch
            view.on_timeout = timeout
            view.add_item(profile_button)
            view.add_item(delete)
            await interaction.followup.send(file=discord.File(f"./assets/robloxImages/users/{uid}/info.png"), view=view)
    
    @app_commands.command(name="userid", description="Searches for a Roblox User by Id")
    @app_commands.describe(userid="The Id of the Roblox User you want to search")
    async def search_userid(self, interaction: discord.Interaction, userid: int):
        await interaction.response.defer(thinking=True)
        view = userView(interaction.user, timeout=120)
        robloxUser = getInfo(userid)

        if robloxUser["success"] == False:
            return await interaction.followup.send(f"I couldn't find the user with the Roblox ID **{userid}**.")
        
        else:
            uid = robloxUser["id"]
            info = getInfo(uid)
            profile_button = ui.Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
            description = ui.Button(label="Show Description", style=discord.ButtonStyle.grey)
            delete = ui.Button(label="Delete", style=discord.ButtonStyle.red)

            async def deletesearch(interaction: discord.Interaction):
                await interaction.response.defer()
                try: await interaction.delete_original_message()
                except: pass

            async def showDescription(interaction: discord.Interaction):
                view.remove_item(profile_button)
                view.remove_item(description)
                view.remove_item(delete)
                await interaction.response.defer()
                await interaction.followup.send(content=info["description"], view=view, ephemeral=True)

            async def timeout():
                view.remove_item(delete)
                view.remove_item(description)
                try: await interaction.edit_original_response(view=view)
                except: return
            
            avatar = getAvatar("fullbody", uid, 3)
            createRobloxInfo(avatar, info)

            description.callback = showDescription
            delete.callback = deletesearch
            view.on_timeout = timeout
            view.add_item(profile_button)
            view.add_item(description)
            view.add_item(delete)
            await interaction.followup.send(file=discord.File(f"./assets/robloxImages/users/{uid}/info.png"), view=view)

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
    @app_commands.command(name="robux", description="Converts Robux to a Real-Life Currency")
    @app_commands.describe(amount="Amount of Robux you want to convert", currency="Type of Currency you want to convert")
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
    
    @app_commands.command(name="currency", description="Converts US Dollars to Robux")
    @app_commands.describe(amount="The amount of US Dollars to Convert to Robux")
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
