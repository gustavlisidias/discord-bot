import os
import yt_dlp

from dotenv import load_dotenv
from discord import Intents
from discord.ext import commands


load_dotenv()

token = os.getenv('TOKEN')

intents = Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

prefix = '?'
bot = commands.Bot(command_prefix=prefix, intents=intents)

ytdl = yt_dlp.YoutubeDL({'format': 'bestaudio/best'})
ffmpeg_path = 'C:/ffmpeg/ffmpeg.exe'
ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.5"'}