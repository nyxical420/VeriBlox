from this import d
import discord
import discord.ui as ui
import discord.app_commands as app_commands
import discord.ext.commands as commands
from discord.ext.commands import GroupCog

from typing import Optional
from datetime import datetime
from packages.DataTools import readUserData, appendUserData
from packages.RobloxAPI import getInfo, getAvatar

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
    def __init__(self, bot):
        self.bot = bot
        self.colors = {"Online": 0x00A2FF, "Playing": 0x02B757, "Creating": 0xF68802, "Offline": 0x2F3136, "Banned": 0xFF6961}
    
    @app_commands.command(name="whois", description="Views the mebmer's Roblox Profile")
    @app_commands.describe(member="The member you want to view their Roblox Profile")
    async def whois(self, interaction : discord.Interaction, member : Optional[discord.Member] = None):
        await interaction.response.defer(thinking=True)
        data = await readUserData()
        
        if not str(interaction.user.id) in data:
            return await interaction.followup.send("Looks like you aren't verified to VeriBlox. Please verify to use this command!")
            
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**")
            return await interaction.followup.send(embed=embed)

        member = interaction.user if not member else member
        member_id = str(member.id)
        view = userView(interaction.user, timeout=300)
        
        try:
            if data[member_id]["verified"] == False:
                return await interaction.followup.send(content=f"{member.mention} doesn't seem to be verified.")
        except:
            return await interaction.followup.send(content=f"{member.mention} doesn't seem to be verified.")

        async def deletewhois(interaction):
            await interaction.response.defer()
            try: await interaction.delete_original_message()
            except: pass
        
        async def timeout():
            view.remove_item(delete)
            try: await interaction.edit_original_message(view=view)
            except: return
                
        uid = int(data[member_id]["robloxid"])
        info = await getInfo(uid)
        status = info["status"]
        description = info["description"]

        profile_button = ui.Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
        avatarimage = await getAvatar("fullbody", uid, 4)
        delete = ui.Button(label="Delete", style=discord.ButtonStyle.red)
        
        if len(description) >= 1001:
            description = "Description could not be displayed since it exceeds more than **1000 characters**."

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
        member_id = str(member.id)
        data = await readUserData()

        if not str(interaction.user.id) in data:
            return await interaction.response.send_message("Looks like you aren't verified to VeriBlox. Please verify to use this command!")
            
        if not interaction.guild:
            embed = discord.Embed(description="**⚠️ | You can't run this command on DMs!**")
            return await interaction.response.send_message(embed=embed)
        
        if viewtype == "bustshot":
            if imageres == 4:
                imageres = 3

        uid = data[member_id]["robloxid"]
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

        embed.set_image(url=await getAvatar(type=viewtype, userid=int(uid), size=imageres))

        await interaction.response.send_message(embed=embed)

    #@app_commands.command(name="archive", description="Creates an Archive of your Roblox Account")
    #@app_commands.checks.cooldown(1, 172800, key=lambda i: i.user.id)
    #async def archive(self, interaction: discord.Interaction):
    #    ...

    @app_commands.command(name="taxcalc", description="Calculates how many Robux you need to cover Roblox Tax")
    @app_commands.describe(amount="Amount of Robux to add Tax", ingame="Whenever the purchase is made inside a Roblox Game")
    @app_commands.choices(ingame=[app_commands.Choice(name='False', value="False"), app_commands.Choice(name='True', value="True")])
    async def taxcalc(self, interaction: discord.Interaction, amount: int, ingame: str = "False"):
        embed = discord.Embed(title="Robux Tax Calculator", color=0x02B757)
        tax = 30 / 100
        earnings = 70 / 100

        if ingame == "True":
            tax = 40 / 100
            earnings = 60 / 100
            embed.set_footer(text="This is In-Game Purchase Tax!")

        embed.description = f"You will need **{amount + round(amount / earnings * tax):,} R$** to get **{amount:,} R$**.\nYou get **{round(amount * earnings):,} R$** without adding tax."
        await interaction.response.send_message(embed=embed)

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

    @app_commands.command(name="deletedata", description="Deletes all of your data from VeriBlox")
    async def deletedata(self, interaction : discord.Interaction):
        data = await readUserData()

        if not str(interaction.user.id) in data:
            return await interaction.response.send_message("Looks like you aren't verified to VeriBlox. Please verify to use this command!", ephemeral=True)

        view = ui.View(timeout=60)

        delete_confirm = ui.Button(label="Confirm Deletion", style=discord.ButtonStyle.red)
        delete_deny    = ui.Button(label="Cancel Deletion", style=discord.ButtonStyle.gray)

        async def confirm(interaction):
            await interaction.response.defer()
            try:
                del data[str(interaction.user.id)]
                await appendUserData(data=data)
            except:
                return await interaction.edit_original_message(content="Failed to delete your data from VeriBlox.", view=None)

            await interaction.edit_original_message(content="Successfully deleted your data from VeriBlox!", view=None)

        async def deny(interaction):
            await interaction.response.defer()
            await interaction.edit_original_message(content="Data Deletion Cancelled.", view=None)
        
        async def timeout():
            await interaction.edit_original_message(view=None)

        delete_confirm.callback = confirm
        delete_deny.callback = deny
        view.on_timeout = timeout
        view.add_item(delete_confirm)
        view.add_item(delete_deny)
        await interaction.response.send_message(content="Are you sure you want to delete **all** of your data from VeriBlox?", view=view, ephemeral=True)

class search(GroupCog, name="search"):
    def __init__(self, bot):
        self.bot = bot
        self.colors = {"Online": 0x00A2FF, "Playing": 0x02B757, "Creating": 0xF68802, "Offline": 0x2F3136, "Banned": 0xFF6961}

    @app_commands.command(name="username", description="Searches for a Roblox User by Username")
    @app_commands.describe(username="The name of the Roblox User you want to search")
    async def search_username(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(thinking=True)
        view = userView(interaction.user, timeout=120)
        robloxUser = await getInfo(username)

        if robloxUser["success"] == False:
            return await interaction.followup.send(f"I couldn't find the user with the Roblox Name **{username}**.")
        
        else:
            async def deletesearch(interaction):
                await interaction.response.defer()
                try:
                    await interaction.delete_original_message()
                except:
                    pass

            async def timeout():
                view.remove_item(delete)
                try:
                    await interaction.edit_original_message(view=view)
                except:
                    return

            uid = robloxUser["id"]
            info = await getInfo(uid)
            status = robloxUser["status"]
            description = info["description"]
            
            profile_button = ui.Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
            avatarimage = await getAvatar("fullbody", uid, 4)
            delete = ui.Button(label="Delete", style=discord.ButtonStyle.red)

            if len(description) >= 1001:
                description = "Description could not be displayed since it exceeds more than **1,000 characters**."
            
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
    
    @app_commands.command(name="id", description="Searches for a Roblox User by Id")
    @app_commands.describe(id="The Id of the Roblox User you want to search")
    async def search_id(self, interaction: discord.Interaction, id: int):
        await interaction.response.defer(thinking=True)
        view = userView(interaction.user, timeout=120)
        robloxUser = await getInfo(id)

        if robloxUser["success"] == False:
            return await interaction.followup.send(f"I couldn't find the user with the Roblox ID **{id}**.")
        
        else:
            async def deletesearch(interaction):
                await interaction.response.defer()
                try:
                    await interaction.delete_original_message()
                except:
                    pass

            async def timeout():
                view.remove_item(delete)
                try:
                    await interaction.edit_original_message(view=view)
                except:
                    return

            uid = robloxUser["id"]
            info = await getInfo(uid)
            status = robloxUser["status"]
            description = info["description"]
            
            profile_button = ui.Button(label="Visit Roblox Profile", style=discord.ButtonStyle.url, url=f"https://www.roblox.com/users/{uid}/profile")
            avatarimage = await getAvatar("fullbody", uid, 4)
            delete = ui.Button(label="Delete", style=discord.ButtonStyle.red)

            if len(description) >= 1001:
                description = "Description could not be displayed since it exceeds more than **1,000 characters**."
            
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
        embed = discord.Embed(title="Roblox DevEx", color=0x02B757)
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
        embed = discord.Embed(title="Roblox DevEx", color=0x02B757)

        embed.description = f"**{amount:,} USD** converts to **{robuxAmount:,} R$**."
        embed.set_footer(text="Other currencies are currently not supported.")
        await interaction.response.send_message(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(commands(bot))
    await bot.add_cog(search(bot))
    await bot.add_cog(devex(bot))