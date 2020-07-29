from discord.ext import commands

import json
import discord
import typing


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


def write_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def isascii(s):
    return len(s) == len(s.encode())


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='add_nickname_role', help='Add roles to follow the nickname system.')
    @commands.has_permissions(administrator=True)
    async def add_nickname_role(self, ctx, role: commands.RoleConverter = None, *, nickname=None):
        if not role:
            await ctx.send('Please provide a role.')
            return
        if not nickname:
            await ctx.send('Please provide a nickname.')
            return

        nicknames = read_json('assets/nicknames.json')

        if str(role.id) in nicknames:
            await ctx.send('This role is already added.')
            return

        with open('assets/nicknames.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[str(role.id)] = {
                'role_id': str(role.id),
                'role_name': role.name,
                'nickname': nickname
            }

            temp.update(data)

        write_json('assets/nicknames.json', temp)
        await ctx.send(f'Added role ``{role.name}`` with nickname ``{nickname}`` successfully')

    @commands.command(name='add_auto_react', help='Add emojis to be reacted by the bot if a user sends the trigger word.')
    @commands.has_permissions(administrator=True)
    async def add_auto_react(self, ctx, trigger_word=None, emojis: commands.Greedy[typing.Union[discord.Emoji, str]] = None):
        if not trigger_word:
            await ctx.send('Please provide a trigger_word.')
            return

        if not emojis:
            await ctx.send('Please provide atleast one emoji.')
            return

        emojis_data = read_json('assets/emojis.json')

        if trigger_word in emojis_data:
            await ctx.send(f'Your trigger word ``{trigger_word}`` is already added.')
            return

        emojis_to_be_saved = []

        for emoji in emojis:
            try:
                if not isascii(emoji):
                    emojis_to_be_saved.append(emoji)
            except TypeError:
                emojis_to_be_saved.append(emoji.id)

        with open('assets/emojis.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[trigger_word] = {
                'emojis': emojis_to_be_saved
            }

            temp.update(data)

        write_json('assets/emojis.json', temp)
        await ctx.send(f'Successfully added ``{len(emojis_to_be_saved)}`` emojis with the trigger word ``{trigger_word}``')

    @commands.command(name='remove_auto_react', help='Stop a trigger word from triggering anymore in auto react system.')
    @commands.has_permissions(administrator=True)
    async def remove_auto_react(self, ctx, trigger_word=None):
        if not trigger_word:
            await ctx.send('Please provide a trigger_word.')
            return

        emojis = read_json('assets/emojis.json')

        if not trigger_word in emojis:
            await ctx.send(f'``{trigger_word}`` is not setup in my db. So there\'s no point in removing it.')
            return

        emojis.pop(trigger_word, None)

        write_json('assets/emojis.json', emojis)
        await ctx.send(f'Successfully removed ``{trigger_word}``')


def setup(bot):
    bot.add_cog(Config(bot))
