from discord.ext import commands

import embeds
import typing
import discord


async def is_document_exists(collection, id):
    return await collection.count_documents({'_id': id}, limit=1)


def isascii(s):
    return len(s) == len(s.encode())


def get_xp_values(xp_gain):
    lower_limit = round(xp_gain * 0.5)
    lower_limit_half = round(lower_limit * 0.5)
    upper_limit = xp_gain + lower_limit_half
    return lower_limit, upper_limit


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_collection = bot.db.config
        self.nicknames_collection = bot.db.nicknames
        self.auto_react_collection = bot.db.auto_react

    @commands.group(name='set', help='Group of commands to set some values required by bot.', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def _set(self, ctx):
        commands = self._set.commands
        command_names = [x.name for x in commands]

        emoji = self.bot.get_emoji(740571420203024496)

        description = ''
        for command in command_names:
            to_be_added = f'{str(emoji)} {command}\n'
            description += to_be_added

        embed = embeds.normal(description, 'Available commands', ctx)

        await ctx.send(embed=embed)

    @_set.command(name='verification_trigger_word', help='Set the word to be triggered for verification.')
    @commands.has_permissions(administrator=True)
    async def verification_trigger_word(self, ctx, *, trigger_word=None):
        if not trigger_word:
            return await ctx.send('Please provide a trigger word.')

        await self.config_collection.find_one_and_update(
            {'_id': 'verification'},
            {'$set': {'verification_trigger_word': trigger_word}}
        )

        await ctx.send(f'Successfully set the ``verifcation_trigger_word`` as ``{trigger_word}``')

    @_set.command(name='verification_followup_message', help='Set the message to be sent after a user is verified.')
    @commands.has_permissions(administrator=True)
    async def verification_followup_message(self, ctx, *, message=None):
        if not message:
            return await ctx.send('Please provide a message.')

        await self.config_collection.find_one_and_update(
            {'_id': 'verification'},
            {'$set': {'verification_followup_message': message}}
        )

        await ctx.send(f'Successfully set the ``verification_followup_message`` as ``{message}``')

    @_set.command(name='verification_channel', help='Set the channel to be used for verification.')
    @commands.has_permissions(administrator=True)
    async def verification_channel(self, ctx, *, channel: commands.TextChannelConverter = None):
        if not channel:
            return await ctx.send('Please provide a channel.')

        await self.config_collection.find_one_and_update(
            {'_id': 'verification'},
            {'$set': {'verification_channel_id': channel.id}}
        )

        await ctx.send(f'Successfully set the ``verification_channel_id`` as ``{channel.name}``')

    @_set.command(name='counting_channel', help='Set the channel to be used for counting.')
    @commands.has_permissions(administrator=True)
    async def counting_channel(self, ctx, *, channel: commands.TextChannelConverter = None):
        if not channel:
            return await ctx.send('Please provide a channel.')

        await self.config_collection.find_one_and_update(
            {'_id': 'counting'},
            {'$set': {'counting_channel_id': channel.id}}
        )

        await ctx.send(f'Successfully set the ``counting_channel`` as ``{channel.name}``')

    @_set.command(name='counting_count', help='Set the counting count.')
    @commands.has_permissions(administrator=True)
    async def counting_count(self, ctx, count=None, last_msg_author: commands.MemberConverter = None):
        if not count:
            return await ctx.send('Please provide a count.')
        if not last_msg_author:
            return await ctx.send('Please provide last_msg_author.')

        await self.config_collection.find_one_and_update(
            {'_id': 'counting'},
            {'$set':
                {'last_msg_author_id': last_msg_author.id,
                    'last_number': int(count)}
             }
        )

        await ctx.send(f'Successfully set the ``counting_count`` as ``{count}``')

    @_set.command(name='verified_role', help='Set the role to be given to a user after verification.')
    @commands.has_permissions(administrator=True)
    async def verified_role(self, ctx, *, role: commands.RoleConverter = None):
        if not role:
            return await ctx.send('Please provide a role.')

        await self.config_collection.find_one_and_update(
            {'_id': 'verification'},
            {'$set': {'verified_role_id': role.id}}
        )

        await ctx.send(f'Successfully set the ``verified_role`` as ``{role.name}``')

    @_set.command(name='xp_gain', help='Set the xp gain for leveling system.')
    @commands.has_permissions(administrator=True)
    async def xp_gain(self, ctx, xp_gain=None):
        if not xp_gain:
            return await ctx.send('Please provide xp gain argument.')

        lower_limit, upper_limit = get_xp_values(int(xp_gain))

        await self.config_collection.find_one_and_update(
            {'_id': 'levels'},
            {'$set': {
                'xp_gain': int(xp_gain)
            }}
        )

        await ctx.send(f'Xp gain set to be ``7``XP/min\nUsers will now gain ``{lower_limit}``-``{upper_limit}`` XP per message.')

    @_set.command(name='pm_requests_role', help='Set the role to be pinged in pm commands.')
    @commands.has_permissions(administrator=True)
    async def pm_requests_role(self, ctx, role: commands.RoleConverter = None):
        if not role:
            return await ctx.send('Please provide a role.')

        await self.config_collection.find_one_and_update(
            {'_id': 'partnership'},
            {'$set': {
                'pm_requests_role': role.id
            }}
        )

        await ctx.send(f'Successfully set ``pm_requests_role`` to ``{role.name}``')

    @_set.command(name='leveling_channel', help='Set the channel to be used for leveling.')
    @commands.has_permissions(administrator=True)
    async def leveling_channel(self, ctx, channel: commands.TextChannelConverter = None):
        if not channel:
            return await ctx.send('Please provide a channel.')

        await self.config_collection.find_one_and_update(
            {'_id': 'levels'},
            {'$set': {
                'leveling_channel': channel.id
            }}
        )

        await ctx.send(f'Successfully set the ``leveling_channel`` as ``{channel.name}``')

    @commands.group(name='add', help='Group of commands for adding some config values.', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def add(self, ctx):
        commands = self.add.commands
        command_names = [x.name for x in commands]

        emoji = self.bot.get_emoji(740571420203024496)

        description = ''
        for command in command_names:
            to_be_added = f'{str(emoji)} {command}\n'
            description += to_be_added

        embed = embeds.normal(description, 'Available commands', ctx)

        await ctx.send(embed=embed)

    @add.command(name='nickname_role', help='Add roles to follow the nickname system.')
    @commands.has_permissions(administrator=True)
    async def nickname_role(self, ctx, role: commands.RoleConverter = None, *, nickname=None):
        if not role:
            await ctx.send('Please provide a role.')
            return
        if not nickname:
            await ctx.send('Please provide a nickname.')
            return

        is_already_exists = await is_document_exists(self.nicknames_collection, role.id)

        if is_already_exists:
            return await ctx.send('Already exists')

        await self.nicknames_collection.insert_one({
            '_id': role.id,
            'role_name': role.name,
            'nickname': nickname
        })

        await ctx.send(f'Successfully added ``{role.name}`` to ``nickname_role`` list.')

    @add.command(name='auto_react', help='Add emojis to be reacted by the bot if a user sends the trigger word.')
    @commands.has_permissions(administrator=True)
    async def auto_react(self, ctx, trigger_word=None, emojis: commands.Greedy[typing.Union[discord.Emoji, str]] = None):
        if not trigger_word:
            await ctx.send('Please provide a trigger_word.')
            return

        if not emojis:
            await ctx.send('Please provide atleast one emoji.')
            return

        emojis_to_be_saved = []

        for emoji in emojis:
            try:
                if not isascii(emoji):
                    emojis_to_be_saved.append(emoji)
            except TypeError:
                emojis_to_be_saved.append(emoji.id)

        is_already_exists = await is_document_exists(self.auto_react_collection, trigger_word)
        if is_already_exists:
            await self.auto_react_collection.find_one_and_update(
                {'_id': trigger_word.lower()},
                {'$push': {'emojis': {'$each': emojis_to_be_saved}}}
            )

            return await ctx.send(f'Successfully added `{len(emojis_to_be_saved)}` emojis for trigger word `{trigger_word}`.')

        await self.auto_react_collection.insert_one({
            '_id': trigger_word.lower(),
            'emojis': emojis_to_be_saved
        })

        await ctx.send(f'Successfully added ``{trigger_word}`` with ``{len(emojis)}`` emojis to ``auto_react`` list.')

    @add.command(name='level_msg', help='Add a level message to be sent along with their coresponding levelup.')
    @commands.has_permissions(administrator=True)
    async def level_msg(self, ctx, level: int = None, *, message=None):
        if not level:
            return await ctx.send('Please provide a level.')
        if not message:
            return await ctx.send('Please provide a message.')

        self.config_collection.find_one_and_update(
            {'_id': 'levels'},
            {'$push': {
                'level_messages': {
                    'level': level,
                    'message': message
                }
            }}
        )

        await ctx.send(f'Successfully added message for level``{level}``: ```\n{message}\n```')

    @add.command(name='level_role', help='Add a level role to be added to the user when they reach a certain level.')
    @commands.has_permissions(administrator=True)
    async def level_role(self, ctx, level: int = None, role: commands.RoleConverter = None):
        if not level:
            return await ctx.send('Please provide a level.')
        if not role:
            return await ctx.send('Please provide a role.')
        self.config_collection.find_one_and_update(
            {'_id': 'levels'},
            {'$push': {
                'level_roles': {
                    'level': level,
                    'role_id': role.id
                }
            }}
        )

        await ctx.send(f'Successfully added the role ``{role.name}`` to be given on level ``{level}``')

    @commands.group(name='remove', help='Remove config values from db.', invoke_without_command=True)
    async def remove(self, ctx):
        commands = self.remove.commands
        command_names = [x.name for x in commands]

        emoji = self.bot.get_emoji(740571420203024496)

        description = ''
        for command in command_names:
            to_be_added = f'{str(emoji)} {command}\n'
            description += to_be_added

        embed = embeds.normal(description, 'Available commands', ctx)

        await ctx.send(embed=embed)

    @remove.command(name='auto_react', help='Stop a trigger word from triggering anymore in auto react system.')
    @commands.has_permissions(administrator=True)
    async def _auto_react(self, ctx, trigger_word=None):
        if not trigger_word:
            await ctx.send('Please provide a trigger_word.')
            return

        is_already_exists = await is_document_exists(self.auto_react_collection, trigger_word)
        if not is_already_exists:
            return await ctx.send('Doesn\'t exist')

        await self.auto_react_collection.delete_one({'_id': trigger_word})

        await ctx.send(f'Successfully removed ``{trigger_word}`` from ``auto_react`` list.')

    @remove.command(name='nickname_role', help='Remove a nickname role.')
    @commands.has_permissions(administrator=True)
    async def _nickname_role(self, ctx, role: commands.RoleConverter = None):
        if not role:
            await ctx.send('Please provide a role.')
            return

        is_already_exists = await is_document_exists(self.nicknames_collection, role.id)
        if not is_already_exists:
            return await ctx.send('Doesn\'t exist')

        await self.nicknames_collection.delete_one({'_id': role.id})

        await ctx.send(f'Successfully removed ``{role.name}`` from ``nickname_role`` list.')

    @commands.command(name='placeholders', help='See the list of placeholders available for use in other commands.')
    @commands.has_permissions(administrator=True)
    async def placeholders(self, ctx):
        placeholders_doc = await self.config_collection.find_one(
            {'_id': 'placeholders'})
        placeholders = placeholders_doc['placeholders']

        emoji = self.bot.get_emoji(740571420203024496)

        description = ''
        for placeholder in placeholders:
            name = '{' + placeholder['name'] + '}'
            help = placeholder['help']
            to_be_added = f'{str(emoji)}``{name}`` - {help}\n'
            description += to_be_added

        embed = embeds.normal(description, 'Placeholders', ctx)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Config(bot))
