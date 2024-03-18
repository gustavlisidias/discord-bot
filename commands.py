import random
import discord
import asyncio
import io

from discord.ext import commands
from discordify import Spotify
from youtube_search import YoutubeSearch
from PIL import Image

from settings import bot, ytdl, ffmpeg_path, ffmpeg_options
from gemini import question_gemini, vision_gemini
from models import Sala, Comando


voice_clients = {}
queue_clients = {}


@bot.command(name='test', help='Command to test parameters of a function')
async def test(ctx, *args):
    try:
        arguments = ', '.join(args)
        if arguments:
            sala = await Sala(servidor=ctx.guild.id).get()
            await Comando(sala=sala, autor=ctx.author.id, comando=f'?test {arguments}').save()
            await ctx.send(f'{len(args)} parametro: {arguments}')
        else:
            await ctx.send('Por favor envie parametros para a função de teste')

    except Exception as e:
        await ctx.send(f'Erro ao testar função com argumentos: {e}')


@bot.command(name='ping', help='Ping-Pong')
async def ping(ctx):
    try:
        sala = await Sala(servidor=ctx.guild.id).get()
        await Comando(sala=sala, autor=ctx.author.id, comando='?ping').save()
        await ctx.send('pong!')

    except Exception as e:
        await ctx.send(f'Erro ao pingar: {e}')


@bot.command(name='roll', help='Simulates rolling dice. Two args: number of dice and number of sides (f.e: ?roll 1 6)')
async def roll(ctx, *args):
    try:
        if len(args) == 2:
            sala = await Sala(servidor=ctx.guild.id).get()
            dice = [str(random.choice(range(1, int(args[0]) + 1))) for _ in range(int(args[1]))]

            await Comando(sala=sala, autor=ctx.author.id, comando='?roll').save()
            await ctx.send(', '.join(dice))            

        else:
            await ctx.send('Por favor envie 2 parametros: número de dados e número de lados (ambos números inteiros)')

    except Exception as e:
                await ctx.send(f'Erro ao rolar o dado: {e}')

                
@bot.command(name="spotify")
async def spotify(ctx: commands.Context, member: discord.Member = None):
    member = member or ctx.author
    client = Spotify(bot=bot, member=member)
    content, image, view = await client.get()
    await ctx.reply(content=content, file=image, view=view)


@bot.command(name='join', help='Connect to the current channel')
async def join(ctx):
    if ctx.guild.id not in voice_clients:
        try:
            if not ctx.message.author.voice:
                await ctx.send('Você precisa estar em um canal de voz!')
                return

            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[ctx.guild.id] = voice_client

            sala = await Sala(servidor=ctx.guild.id).get()
            await Comando(sala=sala, autor=ctx.author.id, comando='?join').save()

            return voice_client

        except Exception as e:
            await ctx.send(f'Erro ao entrar no canal de voz: {e}')

    else:
        return voice_clients[ctx.guild.id]


@bot.command(name='leave', help='Disconnect from the current channel')
async def leave(ctx):
    if ctx.guild.id in voice_clients:
        try:
            sala = await Sala(servidor=ctx.guild.id).get()
            await Comando(sala=sala, autor=ctx.author.id, comando='?leave').save()
            await voice_clients[ctx.guild.id].disconnect()
            del voice_clients[ctx.guild.id]

            if ctx.guild.id in queue_clients:
                del queue_clients[ctx.guild.id]
            
        except Exception as e:
            await ctx.send(f'Erro ao tentar sair do canal: {e}')
            
    else:
        await ctx.send('Não estou conectado em nenhum canal de voz')


@bot.command(name='play', help='Play a song from URL or search for your music')
async def play(ctx, *args):
    if not args:
        await ctx.send('Por favor, forneça uma URL ou o título da música para pesquisar')
        return
    
    voice_client = await join(ctx)
    if voice_client:
        arguments = ' '.join(args)
        results = YoutubeSearch(arguments, max_results=10).to_dict()

        if results:
            url = f"https://www.youtube.com{results[0]['url_suffix']}"
            title = f"{results[0]['title']}"
            
            sala = await Sala(servidor=ctx.guild.id).get()
            await Comando(sala=sala, autor=ctx.author.id, comando=f'?play {arguments}').save()

            try:
                # Se a fila não existe OU se ela está vazia e não está tocando uma musica
                if (ctx.guild.id not in queue_clients) or (len(queue_clients[ctx.guild.id]) == 0 and not voice_clients[ctx.guild.id].is_playing()):
                    queue_clients[ctx.guild.id] = [{'url': url, 'title': title}]
                    await skip(ctx)
                else:
                    queue_clients[ctx.guild.id].append({'url': url, 'title': title})
                    await ctx.send(f'A música {title} foi adicionada à fila')

            except Exception as e:
                await ctx.send(f'Ocorreu um erro ao reproduzir a música: {e}')
                return
        
        else:
            await ctx.send('Nenhuma música encontrada')
            return


@bot.command(name='pause', help='Pause the current song')
async def pause(ctx):
    if ctx.guild.id in voice_clients:
        try:
            sala = await Sala(servidor=ctx.guild.id).get()
            await Comando(sala=sala, autor=ctx.author.id, comando='?pause').save()

            if voice_clients[ctx.guild.id].is_playing():
                voice_clients[ctx.guild.id].pause()

            else:
                await ctx.send('Não estou reproduzindo nenhuma música')

        except Exception as e:
            await ctx.send(f'Erro ao tentar pausar: {e}')

    else:
        await ctx.send('Não estou conectado em nenhum canal de voz')


@bot.command(name='resume', help='Resume paused song')
async def resume(ctx):
    if ctx.guild.id in voice_clients:
        try:
            sala = await Sala(servidor=ctx.guild.id).get()
            await Comando(sala=sala, autor=ctx.author.id, comando='?resume').save()

            if voice_clients[ctx.guild.id].is_paused():
                voice_clients[ctx.guild.id].resume()
                return

            if not voice_clients[ctx.guild.id].is_playing():
                await ctx.send('Não estou reproduzindo nenhuma música')
                return

        except Exception as e:
            await ctx.send(f'Erro ao tentar voltar a reproduzir: {e}')
    else:
        await ctx.send('Não estou conectado em nenhum canal de voz')


@bot.command(name='stop', help='Stop the current song')
async def stop(ctx):
    if ctx.guild.id in voice_clients:
        try:
            sala = await Sala(servidor=ctx.guild.id).get()
            await Comando(sala=sala, autor=ctx.author.id, comando='?stop').save()

            if voice_clients[ctx.guild.id].is_playing():
                voice_clients[ctx.guild.id].stop()

            else:
                await ctx.send('Não estou reproduzindo nenhuma música')

        except Exception as e:
            await ctx.send(f'Erro ao tentar parar música: {e}')

    else:
        await ctx.send('Não estou conectado em nenhum canal de voz')


@bot.command(name='queue', help='Display the current music queue')
async def queue(ctx):
    if ctx.guild.id in voice_clients:
        try:
            if ctx.guild.id in queue_clients:
                sala = await Sala(servidor=ctx.guild.id).get()
                queue = queue_clients[ctx.guild.id]

                await Comando(sala=sala, autor=ctx.author.id, comando='?queue').save()

                if queue:
                    queue_list = '\n'.join([f"{index+1}. {item['title']}" for index, item in enumerate(queue)])
                    await ctx.send(f"Fila de Reprodução:\n{queue_list}")
                else:
                    await ctx.send('A fila está vazia')

            else:
                await ctx.send('A fila está vazia')

        except Exception as e:
            await ctx.send(f'Erro ao tentar visualizar a fila: {e}')

    else:
        await ctx.send('Não estou conectado em nenhum canal de voz')


@bot.command(name='skip', help='Next song in queue')
async def skip(ctx):
    if ctx.guild.id in voice_clients:
        try:
            if ctx.guild.id in queue_clients:
                if len(queue_clients[ctx.guild.id]) >= 1:
                    if voice_clients[ctx.guild.id].is_playing():
                        voice_clients[ctx.guild.id].stop()

                    queue = queue_clients[ctx.guild.id].pop(0)
                    url = queue['url']
                    title = queue['title']

                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                    song = data['url']
                    player = discord.FFmpegPCMAudio(song, executable=ffmpeg_path, **ffmpeg_options)
                    player = discord.PCMVolumeTransformer(original=player, volume=0.8)
                    voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(skip(ctx), bot.loop))
                    await ctx.send(f'Tocando agora: {title}')

                else:
                    return

            else:
                await ctx.send('A fila está vazia')

        except Exception as e:
            await ctx.send(f'Ocorreu um erro ao tocar a próxima música: {e}')

    else:
        await ctx.send('Não estou conectado em nenhum canal de voz')


@bot.command(name='question', help='Make a question for Gemini IA')
async def question(ctx, *args):
    if args:
        try:
            arguments = ' '.join(args)
            sala = await Sala(servidor=ctx.guild.id).get()
            resposta = await question_gemini(ctx, arguments)

            await Comando(sala=sala, autor=ctx.author.id, comando=f'?question {arguments}').save()                
            await ctx.send(resposta)

        except Exception as e:
            await ctx.send(f'Ocorreu um erro ao realizar a pergunta: {e}')

    else:
        await ctx.send('Por favor envie uma pergunta')


@bot.command(name='vision', help='Generate text from image and text inputs from Gemini Vision IA')
async def vision(ctx, *args):
    if args:
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if attachment.width is not None and attachment.height is not None:
                    try:
                        arguments = ' '.join(args)
                        sala = await Sala(servidor=ctx.guild.id).get()
                        img_content = await attachment.read()
                        img = Image.open(io.BytesIO(img_content))
                        resposta = await vision_gemini(ctx, arguments, img)

                        await ctx.send(resposta)
                        await Comando(sala=sala, autor=ctx.author.id, comando=f'?vision {arguments}').save()
                        
                    except Exception as e:
                        await ctx.send(f'Erro ao abrir a imagem: {e}')
                        return
                    
                else:
                    await ctx.send('A mensagem não possui uma imagem')

    else:
        await ctx.send('Por favor envie uma mensagem que possua uma imagem')