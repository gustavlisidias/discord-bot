import commands  # noqa: F401

from settings import bot, prefix, token


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

    else:
        if message.content.lower() in ["olá", "ola", "oi"]:
            await message.channel.send("Olá! Tudo bem?")


bot.run(token)