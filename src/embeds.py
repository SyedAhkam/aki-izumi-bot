import discord

colors = {
    'normal': 0xb5fffd,
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
