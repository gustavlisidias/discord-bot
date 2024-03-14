import os
import yt_dlp
import discord

from dotenv import load_dotenv
from discord.ext import commands
from google.generativeai.types.safety_types import HarmCategory, HarmBlockThreshold


load_dotenv()

token = os.getenv('TOKEN')
gkey = os.getenv('GOOGLE_KEY')

pguser = os.getenv('USER_PG')
pgpass = os.getenv('PASS_PG')
pgbase = 'discord'
pghost = 'localhost'

prefix = '?'
help_command = commands.DefaultHelpCommand(no_category='Commands')
bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), help_command=help_command, intents=discord.Intents.all(), allowed_mentions=discord.AllowedMentions.none())

ytdl = yt_dlp.YoutubeDL({'format': 'bestaudio/best'})
ffmpeg_path = 'C:/ffmpeg/ffmpeg.exe'
ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.5"'}

generation_config = {
    'temperature': 0.5,
    'candidate_count': 1,
    'stop_sequences': ['space']
}

safety_config = [
    {
      'category': HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, 
      'threshold': HarmBlockThreshold.BLOCK_NONE
    },
    {
      'category': HarmCategory.HARM_CATEGORY_HATE_SPEECH, 
      'threshold': HarmBlockThreshold.BLOCK_NONE
    },
    {
      'category': HarmCategory.HARM_CATEGORY_HARASSMENT, 
      'threshold': HarmBlockThreshold.BLOCK_NONE
    },
    {
      'category': HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, 
      'threshold': HarmBlockThreshold.BLOCK_NONE
    },
]