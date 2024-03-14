import discord
import io

from settings import bot, prefix
from models import Log, Sala
from gemini import chat_gemini
from PIL import Image


@bot.event
async def on_ready():
    await Log(funcao='on_ready', mensagem='conectado como {0.user}'.format(bot)).save()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Spotify"))
    print('Estou conectado como {0.user}'.format(bot))


@bot.event
async def on_guild_join(guild):
    sala = await Sala(servidor=guild.id).get()
    if sala:
        await Sala(sala=guild.id, status=True).update()
        await Log(funcao='on_guild_join', mensagem=f'servidor {guild.id} reconectado').save()
    else:
        await Sala(sala=guild.id, status=True).save()
        await Log(funcao='on_guild_join', mensagem=f'servidor {guild.id} conectado').save()

    channel = guild.system_channel
    if channel.permissions_for(guild.me).send_messages:
        await channel.send('Olá, alguem me chamou?')


@bot.event
async def on_guild_remove(guild):
    try:
        await Sala(sala=guild.id, status=False).update()
        await Log(funcao='on_guild_remove', mensagem=f'servidor {guild.id} removido').save()

    except Exception as e:
        print(f'Ocorreu um erro ao alterar status do servidor: {e}')


@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await Log(funcao='on_member_join', mensagem=f'usuario {member.id} conectado no servidor {member.guild.id}').save()
        await channel.send(f'Olá {member.mention}, seja bem-vindo ao servidor!')
    else:
        print('Canal não encontrado.')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith(prefix):
        await bot.process_commands(message)

    if isinstance(message.channel, discord.DMChannel):
        image = None
        if message.attachments:
            for attachment in message.attachments:
                if attachment.width is not None and attachment.height is not None:
                    try:
                        img_content = await attachment.read()
                        image = Image.open(io.BytesIO(img_content))
                        
                    except Exception as e:
                        await message.channel.send(f'Erro ao abrir a imagem: {e}')
                        return
                else:
                    await message.channel.send('Desculpe. Tenho permissão para responder apenas mensagens de texto e imagens.')
                    return
            

        resposta, erro = await chat_gemini(message.content, message.author.id, image)
        if erro:
            await message.channel.send(erro)
        else:
            if isinstance(resposta, list):
                for frase in resposta:
                    if frase:
                        await message.channel.send(frase)
            else:
                await message.channel.send(resposta)