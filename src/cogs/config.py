from discord.ext import commands

import json
import discord
import typing
import embeds


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

    @commands.command(name='placeholders', help='See the list of placeholders available for use in other commands.')
    @commands.has_role(697877262737080391)
    async def placeholders(self, ctx):

        placeholders = [
            {"name": "user", "help": "Gives the user's name."},
            {"name": "user_mention", "help": "Gives the user's tag as a mention."},
            {"name": "user_id", "help": "Gives the user's id."},
            {"name": "user_tag", "help": "Gives the user's tag."},
            {"name": "user_color", "help": "Gives the user's color."},
            {"name": "user_avatar_url", "help": "Gives the user's avatar url."},
            {"name": "server", "help": "Gives the server's name"},
            {"name": "server_members", "help": "Gives the server's total members."},
            {"name": "server_icon_url", "help": "Gives the server's icon url."}
        ]

        emoji = self.bot.get_emoji(740571420203024496)

        description = ''
        for placeholder in placeholders:
            name = '{' + placeholder['name'] + '}'
            help = placeholder['help']
            to_be_added = f'{str(emoji)}``{name}`` - {help}\n'
            description += to_be_added

        embed = embeds.normal(description, 'Placeholders', ctx)

        await ctx.send(embed=embed)

    @commands.command(name='set_verification_trigger_word', help='Set the word to be triggered for verification.')
    async def set_verification_trigger_word(self, ctx, *, trigger_word=None):
        if not trigger_word:
            return await ctx.send('Please provide a trigger_word.')

        config_data = read_json('assets/config.json')

        with open('assets/config.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data['verification_trigger_word'] = trigger_word

            temp.update(data)

        write_json('assets/config.json', temp)

        # for some reason i gotta do this
        ctx.bot.unload_extension(f'cogs.events')
        ctx.bot.load_extension(f'cogs.events')

        await ctx.send('All done!')

    @commands.command(name='set_verification_followup_message', help='Set a message to be sent after a user is verified.')
    async def set_verification_followup_message(self, ctx, *, message=None):
        if not message:
            return await ctx.send('Please provide a message.')

        config_data = read_json('assets/config.json')

        with open('assets/config.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data['verification_followup_message'] = message

            temp.update(data)

        write_json('assets/config.json', temp)

        # for some reason i gotta do this
        ctx.bot.unload_extension(f'cogs.events')
        ctx.bot.load_extension(f'cogs.events')

        await ctx.send('All done!')

    @commands.command(name='set_verification_channel', help='Set the channel to be used for verification.')
    async def set_verification_channel(self, ctx, *, channel: commands.TextChannelConverter = None):
        if not channel:
            return await ctx.send('Please provide a channel.')

        config_data = read_json('assets/config.json')

        with open('assets/config.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data['verification_channel_id'] = channel.id

            temp.update(data)

        write_json('assets/config.json', temp)

        # for some reason i gotta do this
        ctx.bot.unload_extension(f'cogs.events')
        ctx.bot.load_extension(f'cogs.events')

        await ctx.send('All done!')


def setup(bot):
    bot.add_cog(Config(bot))
