from discord.ext import commands

import json
import os
import random
import discord


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


def write_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)


def format_nickname(string, data):
    return string.format(**data)


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user.name}')

    @commands.Cog.listener()
    async def on_message(self, message):

        emojis = read_json('assets/emojis.json')

        for word in message.content.split():
            if word.lower() in emojis:
                print('Word found in emoji json')
                emoji_list = emojis[word.lower()]['emojis']
                print(emoji_list)

                emoji_object_list = []

                for emoji in emoji_list:
                    try:
                        emoji_object = self.bot.get_emoji(int(emoji))
                    except ValueError:
                        emoji_object = emoji
                    emoji_object_list.append(emoji_object)

                choosen_emoji = random.choice(emoji_object_list)

                await message.add_reaction(str(choosen_emoji))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        channel = after.guild.get_channel(630244103397048333)

        new_roles = [x for x in after.roles if x not in before.roles]
        removed_roles = [x for x in before.roles if x not in after.roles]

        nicknames = read_json('assets/nicknames.json')

        role_before = None

        for role in before.roles:
            if role.id in nicknames:
                role_before = role

        if len(before.roles) < len(after.roles):

            role_id = new_roles[0].id

            if str(role_id) in nicknames:

                role = nicknames[str(role_id)]

                if 'nickname' in role:

                    formatted_nickname = format_nickname(
                        role['nickname'], {'name': after.name})

                    await after.edit(nick=formatted_nickname)

        elif len(before.roles) > len(after.roles):

            role_id = removed_roles[0].id

            if str(role_id) in nicknames:

                role = nicknames[str(role_id)]

                if 'nickname' in role:
                    await after.edit(nick='')

                    if role_before:
                        nickname = nicknames[role_before.id]['nickname']
                        await after.edit(nick=nickname)


def setup(bot):
    bot.add_cog(Events(bot))
