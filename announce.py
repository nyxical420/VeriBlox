import discord
import discord.ext.commands as commands

from os import getenv
from asyncio import sleep
from dotenv import load_dotenv

from packages.Logging import log

load_dotenv("./conf/.env")


class VeriBlox(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=[], intents=intents)

    async def on_ready(self):
        for guild in bot.guilds:
            embed = discord.Embed()
            embed.title = "VeriBlox Announcement"
            embed.set_footer(text="This is an Important Message by the VeriBlox Developer.")
            embed.description = f"Hello **{guild.owner.name}**!\nYou are getting this message since you have **VeriBlox** added in your server, **{guild.name}**.\n\nYour Verification Channel needs to be updated for an Instruction Update. Please use the command </setup:994793996012486747> to update!"
            owner = bot.get_user(guild.owner.id)
            try:
                await owner.send(embed=embed)
                log(f"Sent message to {guild.owner} ({guild.owner.id})!")
            except: log(f"Failed to send message to {guild.owner} ({guild.owner.id})", 1)
        log("VeriBlox Started!")

bot = VeriBlox()

token = getenv("token")
bot.run(token)
