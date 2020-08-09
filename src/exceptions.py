from discord.ext import commands


class UserBlacklisted(commands.CommandError):
    def __init__(self, ctx):
        self.ctx = ctx

    def __str__(self):
        return f'{ctx.author.name} is blacklisted.'
