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

        self.music_queue = []
        self.youtubedl_options = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.channel_connected = None

    def search(self, music):
        response = VideosSearch(music, limit=1)
        url = response.result()
        return url.get("result")[0]["link"]

    
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            loop = asyncio.get_running_loop()
            
            self.is_playing = True
            url = self.music_queue[0][0]

            if self.channel_connected == None:
                self.channel_connected = await self.music_queue[0][1].connect()

                if self.channel_connected is None:
                    await ctx.send("to fraquinho nao consegui entrar")
                    return
            else:
                await self.channel_connected.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)
            video = pafy.new(url)
            song = video.getbestaudio()
            source = discord.FFmpegPCMAudio(song.url, **self.ffmpeg_options)
            
            await ctx.send(f"Tocando: {video.title}")
            self.channel_connected.play(source, after= lambda e: self.play_next(ctx, loop))
            
    
        else:
            self.is_playing = False
            if self.channel_connected != None:
                await self.channel_connected.disconnect()   
                self.channel_connected = None
            return
    

    def play_next(self, ctx, loop):
        asyncio.run_coroutine_threadsafe(self.play_music(ctx), loop)


    @commands.command(name="play", aliases=['p'], help="toca umas musiquinha")
    async def play(self, ctx, *args):
        song_name = " ".join(args)
        
        channel = ctx.author.voice.channel

        if channel is None:
            return
        
        song = self.search(song_name)
        if type(song) != str:
            await ctx.send("Sou burro e nao achei :/")
        else:
            self.music_queue.append([song, channel])
            await ctx.send("Entrou na fila :D")
            if self.is_playing == False:
                await self.play_music(ctx)

    @commands.command(name="pause", help="pausa as musiquinha")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.channel_connected.pause()

    @commands.command(name="resume", help="retorna as musiquinha")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.channel_connected.resume()

    @commands.command(name="skip", aliases=["s", "pula"], help="pula as musiquinha")
    async def skip(self, ctx, *args):
        if self.channel_connected != None and self.channel_connected.is_connected():
            self.channel_connected.stop()
            await ctx.send("Pulando")
            await self.play_music(ctx)

    @commands.command(name="quit", aliases=["disconnect", 'q'], help="saio fora")
    async def quit(self, ctx, *args):
        self.is_playing = False
        self.is_paused = False
        await self.channel_connected.disconnect()


    @commands.command(name="playlist", aliases=["pl"],help="Diz as musicas na playlist")
    async def playlist(self, ctx, *args):
        c = 1
        await ctx.send("Musicas na fila: \n")
        for music in self.music_queue:
            song = pafy.new(music[0])
            title = song.title
            await ctx.send(f'{c}. {title} \n')
            c += 1
