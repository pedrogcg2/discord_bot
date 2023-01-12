import discord
from discord.ext import commands
from music import MusicCog
import asyncio
from help import HelpCog


intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix='pg!', intents=intents)


async def setup():
    await bot.add_cog(MusicCog(bot))
    await bot.add_cog(HelpCog(bot))
    

async def main():
    await setup()
    await bot.start(TOKEN)

@bot.event
async def on_ready():
    print("logged in sucessfully")

@bot.event
async def on_disconnect():
    print("disconnected sucessfully")


file = open("token.txt", mode="r")
TOKEN = file.readline()
file.close()


asyncio.run(main())
