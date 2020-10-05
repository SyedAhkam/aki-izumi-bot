from discord.ext import commands
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

import logging
import os
import discord

logging.basicConfig(level=logging.INFO)

load_dotenv()


def is_env_dev():
    return os.getenv('DEV') == 'True'


if is_env_dev():
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN_BETA')
else:
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')
CAT_API_KEY = os.getenv('CAT_API_KEY')
DOG_API_KEY = os.getenv('DOG_API_KEY')
IGDB_API_KEY = os.getenv('IGDB_API_KEY')

# annoying intents
intents = discord.Intents.default()
intents.members = True

if is_env_dev():
    bot = commands.Bot(
        command_prefix=['ab!', 'Ab!'], case_insensitive=True, intents=intents)
else:
    bot = commands.Bot(
        command_prefix=['a!', 'A!'], case_insensitive=True, intents=intents)

bot.owner_ids = [342545053169877006, 674432715088592915]
bot.cat_api_key = CAT_API_KEY
bot.dog_api_key = DOG_API_KEY
bot.igdb_api_key = IGDB_API_KEY

if is_env_dev():
    bot.db = AsyncIOMotorClient(MONGODB_URI).bot_beta
else:
    bot.db = AsyncIOMotorClient(MONGODB_URI).bot

# jishaku
bot.load_extension('jishaku')

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
