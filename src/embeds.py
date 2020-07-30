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
