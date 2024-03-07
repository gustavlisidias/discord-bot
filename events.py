from settings import bot, prefix
from providers import chat_gemini

import discord


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
        resposta, erro = await chat_gemini(message.content, message.author.id)
        if erro:
            await message.channel.send(erro)
        else:
            if isinstance(resposta, list):
                for frase in resposta:
                    if frase:
                        await message.channel.send(frase)
            else:
                await message.channel.send(resposta)