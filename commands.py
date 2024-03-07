import random
import discord
import asyncio
import validators

from settings import bot, ytdl, ffmpeg_path, ffmpeg_options
from providers import question_gemini
from youtube_search import YoutubeSearch


voice_clients = {}
queue_clients = {}

@bot.command(name='test', help='Command to test parameters of a function')
async def test(ctx, *args):
    arguments = ', '.join(args)
    await ctx.send(f'{len(args)} arguments: {arguments}')


@bot.command(name='ping', help='Ping-Pong')
async def ping(ctx):
    await ctx.send('pong!')


@bot.command(name='roll', help='Simulates rolling dice')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [str(random.choice(range(1, number_of_sides + 1))) for _ in range(number_of_dice)]
    await ctx.send(', '.join(dice))


@bot.command(name='join', help='Connect to the current channel')
async def join(ctx):
    try:
        voice_channel = ctx.author.voice.channel

        if not voice_channel:
            await ctx.send('Você precisa estar em um canal de voz!')
            return

        voice_client = await voice_channel.connect()
        voice_clients[ctx.guild.id] = voice_client
        return voice_client

    except discord.ClientException:
        return


@bot.command(name='leave', help='Disconnect from the current channel')
async def leave(ctx):
    try:
        await voice_clients[ctx.guild.id].disconnect()
    except KeyError:
        await ctx.send('Não estou conectado em nenhum canal de voz')
    except Exception as e:
        await ctx.send(f'Erro ao tentar sair do canal: {e}')


@bot.command(name='play', help='Play a song from URL or search for your music')
async def play(ctx, *args):
    await join(ctx)

    if not args:
        await ctx.send('Por favor, forneça uma URL ou o título da música para pesquisar')
        return
    
    query = ' '.join(args)
    if validators.url(query):
        url = query
    else:
        results = YoutubeSearch(query, max_results=10).to_dict()
        if results:
            url = f'https://www.youtube.com{results[0]["url_suffix"]}'
        else:
            await ctx.send('Nenhuma música encontrada')
            return
    
    try:
        if ctx.guild.id not in queue_clients:
            queue_clients[ctx.guild.id] = [url]
            await skip(ctx)
        else:
            queue_clients[ctx.guild.id].append(url)
            await ctx.send(f'A música {url} foi adicionada à fila')

    except Exception as e:
        await ctx.send(f'Ocorreu um erro ao reproduzir a música: {e}')


@bot.command(name='pause', help='Pause the current song')
async def pause(ctx):
    try:
        voice_clients[ctx.guild.id].pause()
    except KeyError:
        await ctx.send('Não estou reproduzindo nenhuma música')
    except Exception as e:
        await ctx.send(f'Erro ao tentar pausar: {e}')


@bot.command(name='resume', help='Resume paused song')
async def resume(ctx):
    try:
        voice_clients[ctx.guild.id].resume()
    except KeyError:
        await ctx.send('Não estou reproduzindo nenhuma música')
    except Exception as e:
        await ctx.send(f'Erro ao tentar voltar a reproduzir: {e}')


@bot.command(name='stop', help='Stop the current song')
async def stop(ctx):
    try:
        voice_clients[ctx.guild.id].stop()
    except KeyError:
        await ctx.send('Não estou reproduzindo nenhuma música')
    except Exception as e:
        await ctx.send(f'Erro ao tentar parar: {e}')


@bot.command(name='queue', help='Display the current music queue')
async def queue(ctx):
    try:
        queue = voice_clients[ctx.guild.id]['queue']
        if not queue:
            await ctx.send('A fila está vazia')
        else:
            await ctx.send(f'Music Queue: {", ".join(queue)}')
    except KeyError:
        await ctx.send('Não estou conectado em nenhum canal de voz')


@bot.command(name='skip', help='Next song in queue')
async def skip(ctx):
    try:
        queue = queue_clients[ctx.guild.id]        
        if len(queue) >= 1:

            if voice_clients[ctx.guild.id].is_playing():
                await stop(ctx)

            url = queue_clients[ctx.guild.id].pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            song = data['url']
            player = discord.FFmpegPCMAudio(song, executable=ffmpeg_path, **ffmpeg_options)
            player = discord.PCMVolumeTransformer(original=player, volume=0.8)
            voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(skip(ctx), bot.loop))

        else:
            await ctx.send('A lista está vazia')
            await stop(ctx)
            del queue_clients[ctx.guild.id]
            return

    except Exception as e:
        await ctx.send(f'Ocorreu um erro ao tocar a próxima música: {e}')


@bot.command(name='question', help='Make a question for Gemini IA')
async def question(ctx, *args):
    query = ' '.join(args)
    try:
        resposta = await question_gemini(query)
        await ctx.send(resposta)

    except Exception as e:
        await ctx.send(f'Ocorreu um erro ao realizar a pergunta: {e}')