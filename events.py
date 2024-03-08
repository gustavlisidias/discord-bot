import discord
import io

from settings import bot, prefix
from gemini import chat_gemini
from PIL import Image


@bot.event
async def on_ready():
    print("Estou conectado como {0.user}".format(bot))


@bot.event
async def on_member_join(member):
    channel = bot.get_channel("7dgxRjT8")
    if channel:
        await channel.send(f"Olá {member.mention}, seja bem-vindo ao servidor!")
    else:
        print("Canal não encontrado.")


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