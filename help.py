import discord
import asyncio
from discord.ext import commands


#BEM RUDIMENTAR
class HelpCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "comandos", help="Mostra os comandos disponíveis")
    async def help(self, ctx, *args):
        cogs = [self.bot.get_cog(name) for name in self.bot.cogs]
        
        for cog in cogs:
            commands = cog.get_commands()
            for command in commands:
                	await ctx.send(f'Digite pg!{command.name} para {command.help}')
            
