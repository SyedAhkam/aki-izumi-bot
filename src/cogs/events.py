from discord.ext import commands, tasks
import random
import discord
import embeds
import exceptions
import datetime
import collections


def format_nickname(string, data):
    return string.format(**data)


async def is_document_exists(collection, id):
    return await collection.count_documents({'_id': id}, limit=1)


def get_xp_values(xp_gain):
    lower_limit = round(xp_gain * 0.5)
    lower_limit_half = round(lower_limit * 0.5)
    upper_limit = xp_gain + lower_limit_half
    return lower_limit, upper_limit


def get_next_level_xp(level):
    xp = 5*(int(level)**2)+50*int(level)+100
    return xp


XpUser = collections.namedtuple('user', ['id', 'last_time_xp_gained'])


def get_keys(user, guild):
    return {
        "user": user.name,
        "user_mention": user.mention,
        "user_id": user.id,
        "user_tag": f'{user.name}#{user.discriminator}',
        "user_color": user.color,
        "user_avatar_url": user.avatar_url,
        "server": guild.name,
        "server_members": len(guild.members),
        "server_icon_url": guild.icon_url
    }


def format_string_with_keys(string, keys):
    return string.format(**keys)


async def format_embed(user, guild, embed):
    keys = get_keys(user, guild)

    if embed.title:
        embed.title = format_string_with_keys(embed.title, keys)

    if embed.description:
        embed.description = format_string_with_keys(embed.description, keys)

    if embed.footer:
        footer_text = format_string_with_keys(embed.footer.text, keys)
        embed.set_footer(text=footer_text, icon_url=embed.footer.icon_url)

    if embed.author:
        author_name = format_string_with_keys(embed.author.name, keys)
        embed.set_author(name=author_name, url=embed.author.url,
                         icon_url=embed.author.icon_url)

    if embed.fields:
        new_fields = []
        for field in embed.fields:
            formatted_field_name = format_string_with_keys(field.name, keys)
            formatted_field_value = format_string_with_keys(field.value, keys)
            new_fields.append((formatted_field_name, formatted_field_value))

        embed.clear_fields()

        for name, value in new_fields:
            embed.add_field(name=name, value=value)

    return embed


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blacklisted_collection = bot.db.blacklisted
        self.auto_react_collection = bot.db.auto_react
        self.config_collection = bot.db.config
        self.nicknames_collection = bot.db.nicknames
        self.levels_collection = bot.db.levels
        self.triggers_collection = bot.db.triggers
        self.recently_leveled_up = []
        self.handle_recently_leveled_up.start()

    @tasks.loop(seconds=60.0, reconnect=True)
    async def handle_recently_leveled_up(self):
        for xp_user in self.recently_leveled_up:
            current_time = datetime.datetime.now().timestamp()

            if current_time - xp_user.last_time_xp_gained >= 60:
                self.recently_leveled_up.remove(xp_user)

    async def bot_check(self, ctx):
        is_blacklisted = await is_document_exists(self.blacklisted_collection, ctx.author.id)
        if is_blacklisted:
            if ctx.message.content.startswith(ctx.prefix):
                raise exceptions.UserBlacklisted(ctx)
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user.name}')

        name = '*₊°🌸オタク│Otaku Akademī │🎮❀°•˚ server | Stay safe uwu'

        activity = discord.Activity(
            type=discord.ActivityType.watching, name=name)

        await self.bot.change_presence(status=discord.Status.online, activity=activity)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # auto_react
        for word in message.content.split():
            is_word_exists = await is_document_exists(self.auto_react_collection, word.lower())
            if is_word_exists:
                emoji_collection = await self.auto_react_collection.find_one({'_id': word.lower()})
                emoji_list = emoji_collection['emojis']
                emoji_object_list = []

                for emoji in emoji_list:
                    try:
                        emoji_object = self.bot.get_emoji(int(emoji))
                    except ValueError:
                        emoji_object = emoji
                    emoji_object_list.append(emoji_object)

                choosen_emoji = random.choice(emoji_object_list)

                await message.add_reaction(str(choosen_emoji))

        # counting
        counting_doc = await self.config_collection.find_one({'_id': 'counting'})
        if message.channel.id == counting_doc['counting_channel_id']:

            ctx = await self.bot.get_context(message)

            is_blacklisted = await is_document_exists(self.blacklisted_collection, ctx.author.id)
            if is_blacklisted:
                embed = embeds.error(
                    f'Sorry you\'ve been blacklisted from using this bot. Ask the bot owner to remove you from blacklist.', 'Blacklisted', ctx)
                await message.channel.send(message.author.mention, embed=embed, delete_after=3)
                await message.delete()
                return

            if len(message.content.split()) >= 1:
                try:
                    num = int(message.content)

                    counting_doc = await self.config_collection.find_one({'_id': 'counting'})
                    last_number = counting_doc['last_number']

                    # if last_number == num:
                    #     await message.channel.send(f'Wrong number!, Should be {last_number + 1} instead.')
                    #     return

                    if message.author.id == counting_doc['last_msg_author_id']:
                        embed = embeds.error(
                            f'Send one message at a time!', 'Error', ctx)
                        # await message.channel.send(f'{message.author.mention}, Send one message at a time!', delete_after=3)
                        await message.channel.send(message.author.mention, embed=embed, delete_after=3)
                        await message.delete()
                        return

                    if not (last_number + 1) == num:

                        emoji = self.bot.get_emoji(746062864665804902)
                        await message.add_reaction(str(emoji))

                        embed = embeds.normal(
                            f'Wrong number! Chain breaked by ``{message.author.name}``', 'Chain Breaked!', ctx)

                        await message.channel.send(embed=embed)

                        await self.config_collection.find_one_and_update(
                            {'_id': 'counting'},
                            {'$set': {
                                'last_number': 0,
                                'last_msg_author_id': None
                            }}
                        )
                        return

                    # Everything stays good

                    emoji = self.bot.get_emoji(746062865496277073)
                    await message.add_reaction(str(emoji))

                    await self.config_collection.find_one_and_update(
                        {'_id': 'counting'},
                        {'$set': {
                            'last_number': num,
                            'last_msg_author_id': message.author.id
                        }}
                    )

                except ValueError:
                    pass

        # verification
        verification_doc = await self.config_collection.find_one(
            {'_id': 'verification'})
        if message.channel.id == verification_doc['verification_channel_id']:
            if message.content == verification_doc['verification_trigger_word']:

                verified_role = message.guild.get_role(
                    verification_doc['verified_role_id'])

                await message.author.add_roles(verified_role)

                ctx = await self.bot.get_context(message)

                embed = embeds.normal(
                    verification_doc['verification_followup_message'], 'You just got verified!', ctx)
                await message.channel.send(content=message.author.mention, embed=embed)
                await message.delete()

        # xp
#         user_exists = await is_document_exists(self.levels_collection, message.author.id)
#         if not user_exists:
#             await self.levels_collection.insert_one({
#                 '_id': message.author.id,
#                 'xp': 0,
#                 'level': 0
#             })

#         # xp cooldown

#         is_recently_leveled_up = [
#             x.id == message.author.id for x in self.recently_leveled_up
#         ]
#         if not is_recently_leveled_up:

#             xp_config_doc = await self.config_collection.find_one({'_id': 'levels'})

#             if not message.channel in xp_config_doc['ignored_channels']:

#                 lower_limit, upper_limit = get_xp_values(
#                     xp_config_doc['xp_gain'])
#                 randomly_selected_xp = random.randint(lower_limit, upper_limit)

#                 await self.levels_collection.find_one_and_update(
#                     {'_id': message.author.id},
#                     {'$inc': {
#                         'xp': randomly_selected_xp
#                     }}
#                 )

#                 tuple_to_be_added = XpUser(
#                     message.author.name, datetime.datetime.now().timestamp())

#                 self.recently_leveled_up.append(tuple_to_be_added)

#         else:
#             pass

#         # check if we need to level them up

#         user_level_doc = await self.levels_collection.find_one({'_id': message.author.id})
#         current_xp = user_level_doc['xp']
#         current_level = user_level_doc['level']
#         ctx = await self.bot.get_context(message)

#         next_level = current_level + 1
#         if current_xp > get_next_level_xp(next_level):

#             await self.levels_collection.find_one_and_update(
#                 {'_id': message.author.id},
#                 {'$set': {
#                     'level': next_level
#                 }}
#             )

#             xp_config_doc = await self.config_collection.find_one({'_id': 'levels'})
#             leveling_channel = message.guild.get_channel(
#                 xp_config_doc['leveling_channel'])

#             # check if a leveling message is set
#             level_messages = xp_config_doc['level_messages']
#             level_msg = [x for x in level_messages if x['level'] == next_level]

#             # check if we need to give them a role

#             level_roles = xp_config_doc['level_roles']
#             level_role = [x for x in level_roles if x['level'] == next_level]

#             if level_role:
#                 role_obj = message.guild.get_role(level_role[0]['role_id'])
#                 await message.author.add_roles(role_obj)

#             embed = embeds.normal(
#                 level_msg[0][
#                     'message'] if level_msg else f'Congrats! You\'ve leveled up to level {next_level}.',
#                 'Level up!',
#                 ctx
#             )

#             embed.set_footer(text=message.guild.name)
#             embed.set_thumbnail(url=message.author.avatar_url)

#             await leveling_channel.send(content=message.author.mention, embed=embed)

        # triggers
        message_splitted = message.content.split()
        triggers_config = await self.config_collection.find_one({'_id': 'triggers'})
        if message_splitted[0] == triggers_config['triggers_prefix']:
            args = message.content.split()[1:]
            try:
                trigger_name = args[0]
                trigger_doc = await self.triggers_collection.find_one({'_id': trigger_name})
                if trigger_doc:
                    formatted_embed = None
                    text = None
                    if trigger_doc['embed']:
                        embed = embeds.get_embed_from_dict(
                            trigger_doc['embed'])
                        formatted_embed = await format_embed(message.author, message.guild, embed)
                    if trigger_doc['text']:
                        text = trigger_doc['text']

                    await message.channel.send(embed=formatted_embed, content=text)

            except KeyError:
                pass
        
        if message.content.startswith('a!'):
            try:
                trigger_name = message.content[2:]
                trigger_doc = await self.triggers_collection.find_one({'_id': trigger_name})
                if trigger_doc:
                    formatted_embed = None
                    text = None
                    if trigger_doc['embed']:
                        embed = embeds.get_embed_from_dict(
                            trigger_doc['embed'])
                        formatted_embed = await format_embed(message.author, message.guild, embed)
                    if trigger_doc['text']:
                        text = trigger_doc['text']

                    await message.channel.send(embed=formatted_embed, content=text)

            except KeyError:
                pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        new_roles = [x for x in after.roles if x not in before.roles]
        removed_roles = [x for x in before.roles if x not in after.roles]

        if len(before.roles) < len(after.roles):

            role_id = new_roles[0].id

            is_nickname_exists = await is_document_exists(self.nicknames_collection, role_id)
            if is_nickname_exists:
                doc = await self.nicknames_collection.find_one({'_id': role_id})

                formatted_nickname = format_nickname(
                    doc['nickname'], {'name': after.name})

                await after.edit(nick=formatted_nickname)

            if role_id == 758838449289035788:
                embed = embeds.blank()
                embed.description = '''
                                ๑‧₊˚<:oa_kannawoah:746059883828215969> AH! A-Arigatō for donating! <:oa_uwu_juuzou:710645176879677488>
                ˗ˏˋ･ﾟ︶︶︶︶︶︶︶︶︶︶︶︶︶︶︶︶︶︶︶︶︶︶︶︶꒷꒦・˙˶

                Thank you so much for donating to the server! <:oa_yay:710715575839752202><:oa_cheer:710645174228877365>

                `The following perks will be given shortly:`

                **__3+ Donation__**
                ʚ`⛩️`・ Donator Role
                ʚ`⛩️`・ Donation chat access (#๑₊꒰🎋。donatorsଓ°。)

                **__5+ Donation__**
                ʚ`⛩️`・ Donation role
                ʚ`⛩️`・ Donation chat access (#๑₊꒰🎋。donatorsଓ°。)
                ʚ`⛩️`・ 10k server currency

                **__10+ Donation__**
                ʚ`⛩️`・ Donation role
                ʚ`⛩️`・ Donation chat access (#๑₊꒰🎋。donatorsଓ°。)
                ʚ`⛩️`・ Ability to post in media chats
                ʚ`⛩️`・ Media Shout out (x how ever many times you donate)
                ʚ`⛩️`・ 20k server currency (x how ever many times you donate)
                ʚ`⛩️`・ 10k server currency daily
                ╰・┄・┄・┄・┄・┄・┄・┄・┄・┄・┄・┄・┄・ ʚĭɞ๑‧₊˚˖˳`⛩️🌸⛩️`꒱˙˶
                '''

                embed.set_image(url='https://media.discordapp.net/attachments/752763445455355925/759913055952830484/Donate-PixTeller.png?width=833&height=437')
                embed.set_thumbnail(url=after.avatar_url)
                embed.timestamp = datetime.datetime.utcnow()

                donation_channel = after.guild.get_channel(697877266260164707)
                await donation_channel.send(content=after.mention, embed=embed)


        elif len(before.roles) > len(after.roles):

            role_id = removed_roles[0].id

            is_nickname_exists = await is_document_exists(self.nicknames_collection, role_id)
            if is_nickname_exists:
                doc = await self.nicknames_collection.find_one({'_id': role_id})

                await after.edit(nick='')

def setup(bot):
    bot.add_cog(Events(bot))
