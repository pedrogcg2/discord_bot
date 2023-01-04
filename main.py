import discord
from discord.ext import commands
from music import MusicCog
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='pg!', intents=intents)


async def setup():
    await bot.add_cog(MusicCog(bot))


async def main():
    await setup()


asyncio.run(main())
bot.run("TOKEN")
