from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient

import logging
import os

logging.basicConfig(level=logging.INFO)

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')
CAT_API_KEY = os.getenv('CAT_API_KEY')
DOG_API_KEY = os.getenv('DOG_API_KEY')
IGDB_API_KEY = os.getenv('IGDB_API_KEY')

bot = commands.Bot(command_prefix=['a!', 'A!'], case_insensitive=True)

bot.owner_ids = [342545053169877006, 674432715088592915]
bot.cat_api_key = CAT_API_KEY
bot.dog_api_key = DOG_API_KEY
bot.igdb_api_key = IGDB_API_KEY
bot.db = MongoClient(MONGODB_URI).bot

ignored_cogs = ()
if __name__ == '__main__':
    # Load the cogs in cogs directory
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            if filename[:-3] in ignored_cogs:
                continue
            bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Loaded {filename}')

bot.run(DISCORD_TOKEN)
