from discord.ext import commands

import json
import os
import random

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
        if 'welcome' in message.content.lower():
            emoji_list = [737970174975541248, 737969852261597265]
            emoji_object_list = []

            for emoji in emoji_list:
                emoji_object = self.bot.get_emoji(emoji)
                emoji_object_list.append(emoji_object)

            choosen_emoji = random.choice(emoji_object_list)

            await message.add_reaction(str(choosen_emoji))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        print('Member updated')
        print(f'Before: {before.roles}')
        print(f'After: {after.roles}')

        channel = after.guild.get_channel(630244103397048333)

        new_roles = [x for x in after.roles if x not in before.roles]
        removed_roles = [x for x in before.roles if x not in after.roles]

        nicknames = read_json('assets/nicknames.json')

        if len(before.roles) < len(after.roles):
            await channel.send(f'Role added to the user {after.name}')
            await channel.send(f'New roles: {new_roles}')

            role_id = new_roles[0].id

            if str(role_id) in nicknames:
                await channel.send(nicknames[str(role_id)])
                await channel.send('Found role in json data')

                role = nicknames[str(role_id)]

                if 'nickname' in role:

                    formatted_nickname = format_nickname(role['nickname'], {'name': after.name})

                    await after.edit(nick=formatted_nickname)
                    await channel.send(f'Nickname changed to {formatted_nickname}')


        elif len(before.roles) > len(after.roles):
            await channel.send(f'Role remove from the user {after.name}')
            await channel.send(f'Roles removed: {removed_roles}')

            role_id = removed_roles[0].id

            if str(role_id) in nicknames:
                await channel.send(nicknames[str(role_id)])
                await channel.send('Found role in json data')

                role = nicknames[str(role_id)]

                if 'nickname' in role:
                    await after.edit(nick='')
                    await channel.send(f'Nickname removed')

def setup(bot):
    bot.add_cog(Events(bot))
