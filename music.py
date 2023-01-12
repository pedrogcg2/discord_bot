
import discord
import pafy
import asyncio
from discord.ext import commands
from youtubesearchpython import VideosSearch


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False
        self.channel_connected = None
        self.music_queue = []
        self.music_channel = bot.get_channel(957076453390962698)
        
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}
     

    def search(self, music):
        response = VideosSearch(music, limit=1)
        url = response.result()
        return url.get("result")[0]["link"]

    
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            loop = asyncio.get_running_loop()
            
            self.is_playing = True
            video = self.music_queue[0][0]

            if self.channel_connected == None:
                self.channel_connected = await self.music_queue[0][1].connect()     
            else:
                await self.channel_connected.move_to(self.music_queue[0][1])

            song = video.getbestaudio()
            source = discord.FFmpegPCMAudio(song.url, **self.ffmpeg_options)
            
            await ctx.send(f">>> Tocando: {video.title}")    
            self.channel_connected.play(source, after= lambda e: self.play_next(ctx, loop))

            self.music_queue.pop(0)
            
    
        else: 
            self.is_playing = False
            await asyncio.sleep(300)
            if not self.channel_connected.is_playing():
                await ctx.send(">>> Bot desconectado devido a inatividade")
                await self.quit(ctx)
                return 0
        return -1
    

    def play_next(self, ctx, loop):
        asyncio.run_coroutine_threadsafe(self.play_music(ctx), loop) 


    @commands.command(name="play", aliases=['p'], help="tocar a musica selecionada")
    async def play(self, ctx, *args):
        song_name = " ".join(args)
        
        channel = ctx.author.voice.channel

        if channel is None:
            await ctx.send(">>> Você tem que estar conectado em um canal")
            return
        
        song_search = self.search(song_name)
        song = pafy.new(song_search)
        
        
        self.music_queue.append([song, channel])
        await ctx.send(f">>> Entrou na fila :D")
            
        if self.is_playing == False:
            await self.play_music(ctx)
            return 0
        
       

    @commands.command(name="pause", help="pausar a musica tocando no momento")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.channel_connected.pause()

    @commands.command(name="resume", help="despausar a música tocando")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.channel_connected.resume()

    @commands.command(name="skip", aliases=["s", "pula"], help="pular a musica")
    async def skip(self, ctx, *args):
        if self.channel_connected != None and self.channel_connected.is_connected():
            self.channel_connected.stop()
            await ctx.send(">>> Pulando")

    @commands.command(name="quit", aliases=["disconnect", 'q'], help="sair fora")
    async def quit(self, ctx, *args):
        self.is_playing = False
        self.is_paused = False
        await self.channel_connected.disconnect()
        self.channel_connected = None

    @commands.command(name="playlist", aliases=["pl"],help="listar as musicas na playlist")
    async def playlist(self, ctx, *args):
        c = 1
        song_list = ""
        await ctx.send("Musicas na fila: \n")
        for music in self.music_queue:
            song = music[0]
            title = song.title
            text = f'{c}. {title} \n'
            song_list = song_list + text
            c += 1
        await ctx.send(f">>> {song_list}")


 
 