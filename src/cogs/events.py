from discord.ext import commands, tasks
import random
import discord
import embeds
import exceptions
import datetime
import collections
import ago


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
        self.embeds_collection = bot.db.embeds
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

        name = '*₊°🌸オタク│Otaku Akademī ❀°•˚ server | Stay safe uwu'

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

                main_chat_channel = message.guild.get_channel(
                    784563365103403019)

                await message.author.add_roles(verified_role)

                ctx = await self.bot.get_context(message)

                embed = embeds.normal(
                    verification_doc['verification_followup_message'], 'You just got verified!', ctx)
                welcome_role = ctx.guild.get_role(697877262560657517)
                await main_chat_channel.send(content=f'{message.author.mention} {welcome_role.mention}', embed=embed)
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

            # donations
            donations_config = await self.config_collection.find_one({'_id': 'donations'})
            if role_id == donations_config['donation_role']:
                donation_embed_doc = await self.embeds_collection.find_one({'_id': 'donation'})
                donation_embed = embeds.get_embed_from_dict(
                    donation_embed_doc['embed'])

                donation_embed.set_thumbnail(url=after.avatar_url)

                donation_embed_formatted = await format_embed(after, after.guild, donation_embed)

                donation_channel = after.guild.get_channel(
                    donations_config['donation_channel'])
                await donation_channel.send(content=after.mention, embed=donation_embed_formatted)

            # ultimate donations
            ultimate_donations_config = await self.config_collection.find_one({'_id': 'ultimate_donations'})
            if role_id == ultimate_donations_config['ultimate_donation_role']:
                ultimate_donation_embed_doc = await self.embeds_collection.find_one({'_id': 'ultimate_donation'})
                ultimate_donation_embed = embeds.get_embed_from_dict(
                    ultimate_donation_embed_doc['embed'])

                ultimate_donation_embed.set_thumbnail(url=after.avatar_url)

                ultimate_donation_embed_formatted = await format_embed(after, after.guild, ultimate_donation_embed)

                ultimate_donation_channel = after.guild.get_channel(
                    ultimate_donations_config['ultimate_donation_channel'])
                await ultimate_donation_channel.send(content=after.mention, embed=ultimate_donation_embed_formatted)

        elif len(before.roles) > len(after.roles):

            role_id = removed_roles[0].id

            is_nickname_exists = await is_document_exists(self.nicknames_collection, role_id)
            if is_nickname_exists:
                doc = await self.nicknames_collection.find_one({'_id': role_id})

                await after.edit(nick='')

    @commands.Cog.listener()
    async def on_user_update(self, user_before, user_after):
        if not (user_before.name == user_after.name):
            # username update
            bad_names = ['Stalker', 'Stalkers', 'drugs', 'drug', 'droogs', 'drooogs', 'drooog', 'Alcohol', 'slut', 'sluts', 'droog', 'virgin', 'sexy', 'bastard', 'bastards', 'dyke', 'whore', 'whores', 'smexy', 'secy', 'vape', 'vaping', 'rape', 'raped', 'rapes', 'thot', 'thots', 'pussy', 'dick', 'dicks', 'cocks', 'cock', 'Coochie', 'nude', 'nudes', 'virginity', 'pedophile', 'pedo', 'pedophiles', 'hentai', 'porn', 'sex', 'boobs', 'tits', 'titties', 'boob', 'anal', 'anus', 'arse', 'ballsack', 'blowjob', 'bollock', 'bollok', 'boner', 'buttplug', 'clitoris', 'cum',
                         'cunt', 'cunts', 'dildo', 'erection', 'fellate', 'fellatio', 'felching', 'fudgepacker', 'genitals', 'jizz', 'knobend', 'labia', 'masturbate', 'masturbating', 'muff', 'penis', 'pubes', 'scrotum', 'smegma', 'spunk', 'vagina', 'spank', 'spanking', 'titty', 'asshat', 'pu55y', 'pen1s', '卐', 'faggots', 'faggot', 'fag', 'nigga', 'nigger', 'n.i.g.g.e.r', 'niggers', 'niggas', 'Cummies', 'tiddy', 'pp', 'cummy', 'wank', 'boobies', 'boobie', 'booby', 'paedophile', 'paedophiles', 'paedophilia', 'paedo', 'rapist', 'whalecum', 'condom', 'condoms', 'thicc']

            is_name_bad = False

            print(user_after.name)

            for word in user_after.name:
                if word in bad_names:
                    is_name_bad = True
                    print('1')

            if user_after.name in word:
                is_name_bad = True
                print('2')

            if is_name_bad:
                guild = self.bot.get_guild(697877261952483471)
                staff_chat_channel = guild.get_channel(728096716884279357)

                embed = embeds.blank()
                embed.set_author(name='Bad name detected!')
                embed.set_footer(
                    text=f'User ID: {user_after.id}', icon_url=user_after.avatar_url)

                embed.add_field(
                    name='Name:', value=user_after.name, inline=True)
                embed.add_field(name='Mention:',
                                value=user_after.mention, inline=True)
                embed.add_field(name='Created at:', value=ago.human(
                    user_after.created_at), inline=True)

                await staff_chat_channel.send(embed=embed)

                await user_after.send(f'You\'ve been warned in the {guild.name} server because of your username.\nPlease change it.')

    @commands.Cog.listener()
    async def on_member_join(self, member_before, member_after):
        if member_after.bot:
            return

        join_roles_doc = await self.config_collection.find_one({'_id': 'join_roles'})
        roles = []
        for role_id in join_roles_doc['roles']:
            role_obj = await member_after.guild.get_role(role_id)
            roles.append(role_obj)

        await member_after.add_roles(roles, reason='Auto join roles')


def setup(bot):
    bot.add_cog(Events(bot))
