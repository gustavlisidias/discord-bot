# ruff: noqa: F401
# add to discord: https://discord.com/oauth2/authorize?client_id=1214640841344290876&permissions=8&scope=bot
import commands
import events

from settings import bot, token


if __name__ == "__main__":
    bot.run(token)