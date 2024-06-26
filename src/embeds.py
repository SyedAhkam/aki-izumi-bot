import discord

colors = {
    'normal': 0xdbb8ff,
    'error': 0xff0000,
}


def normal(text, name, ctx):
    embed = discord.Embed(color=colors['normal'], description=text)
    embed.set_author(name=name, icon_url=ctx.bot.user.avatar_url)

    return embed


def error(text, name, ctx):
    embed = discord.Embed(color=colors['error'], description=text)
    embed.set_author(name=name, icon_url=ctx.bot.user.avatar_url)

    return embed


def normal_no_description(name, ctx):
    embed = discord.Embed(color=colors['normal'])
    embed.set_author(name=name, icon_url=ctx.bot.user.avatar_url)

    return embed


def blank():
    embed = discord.Embed(color=colors['normal'])
    return embed


def blank_no_color():
    embed = discord.Embed()
    return embed


def custom(title, color, description, timestamp, url):

    try:
        if not color.startswith('0x'):
            color = int('0x' + color[1:], 16)
    except AttributeError:
        pass

    if not title:
        title = discord.Embed.Empty
    if not description:
        description = discord.Embed.Empty
    if not timestamp:
        timestamp = discord.Embed.Empty
    if not url:
        url = discord.Embed.Empty

    embed = discord.Embed(color=color, title=title,
                          description=description, timestamp=timestamp, url=url)
    return embed


def get_embed_from_dict(dict):
    return discord.Embed.from_dict(dict)


def list_commands_in_group(commands, emoji, ctx):
    command_names = [x.name for x in commands]
    description = ''
    for command in command_names:
        to_be_added = f'{str(emoji)} {command}\n'
        description += to_be_added

    return normal(description, 'Available commands', ctx)


async def get_embed_if_key_exists(string_containing_key, embeds_collection):
    string_splitted = string_containing_key.split()

    for i, word in enumerate(string_splitted):
        if '{embed:' == word:
            embed_name = string_splitted[i + 1][:-1]
            embed_doc = await embeds_collection.find_one({'_id': embed_name})
            if embed_doc:
                return (get_embed_from_dict(embed_doc['embed']), embed_name)
    return None
