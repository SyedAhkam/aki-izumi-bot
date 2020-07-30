from discord.ext import commands

import json
import os
import random
import discord
import embeds


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

        # counting
        if message.channel.id == 735605047907582084:

            if len(message.content.split()) >= 1:
                try:
                    num = int(message.content)

                    counting_data = read_json('assets/counting.json')
                    last_number = counting_data['last_number']

                    # if last_number == num:
                    #     await message.channel.send(f'Wrong number!, Should be {last_number + 1} instead.')
                    #     return

                    if not (last_number + 1) == num:

                        emoji = self.bot.get_emoji(738498530657828875)
                        await message.add_reaction(str(emoji))

                        ctx = await self.bot.get_context(message)

                        embed = embeds.normal(
                            f'Wrong number! Chain breaked by ``{message.author.name}``', 'Chain Breaked!', ctx)

                        await message.channel.send(embed=embed)

                        data_to_be_saved = {
                            "last_number": 0,
                            "last_msg_author_id": None,
                            "chain_count": 0
                        }

                        write_json('assets/counting.json', data_to_be_saved)
                        return

                    # Everything stays good

                    emoji = self.bot.get_emoji(736091414731030541)
                    await message.add_reaction(str(emoji))

                    data_to_be_saved = {
                        "last_number": num,
                        "last_msg_author_id": message.author.id,
                        "chain_count": counting_data['chain_count'] + 1
                    }

                    write_json('assets/counting.json', data_to_be_saved)

                except ValueError:
                    return

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
