from discord.ext import commands

import json
import os
import random
import discord
import embeds
import exceptions


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


def write_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)


def format_nickname(string, data):
    return string.format(**data)


def is_document_exists(collection, id):
    return collection.count_documents({'_id': id}, limit=1)


config_data = read_json('assets/config.json')


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blacklisted_collection = bot.db.blacklisted
        self.auto_react_collection = bot.db.auto_react
        self.config_collection = bot.db.config
        self.nicknames_collection = bot.db.nicknames

    async def bot_check(self, ctx):
        if is_document_exists(self.blacklisted_collection, ctx.author.id):
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
        # auto_react
        for word in message.content.split():
            if is_document_exists(self.auto_react_collection, word.lower()):
                emoji_list = self.auto_react_collection.find_one({'_id': word.lower()})[
                    'emojis']
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
        if message.channel.id == self.config_collection.find_one({'_id': 'counting'})['counting_channel_id']:

            ctx = await self.bot.get_context(message)

            if is_document_exists(self.blacklisted_collection, ctx.author.id):
                embed = embeds.error(
                    f'Sorry you\'ve been blacklisted from using this bot. Ask the bot owner to remove you from blacklist.', 'Blacklisted', ctx)
                await message.channel.send(message.author.mention, embed=embed, delete_after=3)
                await message.delete()
                return

            if len(message.content.split()) >= 1:
                try:
                    num = int(message.content)

                    counting_doc = self.config_collection.find_one(
                        {'_id': 'counting'})
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

                        emoji = self.bot.get_emoji(738498530657828875)
                        await message.add_reaction(str(emoji))

                        embed = embeds.normal(
                            f'Wrong number! Chain breaked by ``{message.author.name}``', 'Chain Breaked!', ctx)

                        await message.channel.send(embed=embed)

                        self.config_collection.find_one_and_update(
                            {'_id': 'counting'},
                            {'$set': {
                                'last_number': 0,
                                'last_msg_author_id': None
                            }}
                        )
                        return

                    # Everything stays good

                    # emoji = self.bot.get_emoji(736091414731030541)
                    emoji = self.bot.get_emoji(737970174975541248)
                    await message.add_reaction(str(emoji))

                    self.config_collection.find_one_and_update(
                        {'_id': 'counting'},
                        {'$set': {
                            'last_number': num,
                            'last_msg_author_id': message.author.id
                        }}
                    )

                except ValueError:
                    return

        if message.channel.id == config_data['verification_channel_id']:
            if message.content == config_data['verification_trigger_word']:

                verified_role = message.guild.get_role(
                    config_data['verified_role_id'])

                await message.author.add_roles(verified_role)

                ctx = await self.bot.get_context(message)

                embed = embeds.normal(
                    config_data['verification_followup_message'], 'You\'ve been verified!', ctx)
                await message.channel.send(content=message.author.mention, embed=embed)

                await message.delete()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        new_roles = [x for x in after.roles if x not in before.roles]
        removed_roles = [x for x in before.roles if x not in after.roles]

        if len(before.roles) < len(after.roles):

            role_id = new_roles[0].id

            if is_document_exists(self.nicknames_collection, role_id):
                doc = self.nicknames_collection.find_one({'_id': role_id})

                formatted_nickname = format_nickname(
                    doc['nickname'], {'name': after.name})

                await after.edit(nick=formatted_nickname)

        elif len(before.roles) > len(after.roles):

            role_id = removed_roles[0].id

            if is_document_exists(self.nicknames_collection, role_id):
                doc = self.nicknames_collection.find_one({'_id': role_id})

                await after.edit(nick='')


def setup(bot):
    bot.add_cog(Events(bot))
