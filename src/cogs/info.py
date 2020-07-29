from discord.ext import commands

class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hello', help='Says back hello to the user.')
    async def hello(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}.')


    @commands.command(name='ping', help='Get the bot\'s ping')
    async def ping(self, ctx):
        ping = round(ctx.bot.latency * 1000)
        await ctx.send(f'Pong!\n{ping}ms')

def setup(bot):
    bot.add_cog(Info(bot))
