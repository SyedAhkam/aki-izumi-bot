import discord

from discord.ext import commands

import embeds


class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embeds_collection = bot.db.embeds

    @commands.command(name='hello', help='Says back hello to the user.')
    async def hello(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}.')

    @commands.command(name='ping', help='Get the bot\'s ping')
    async def ping(self, ctx):
        ping = round(ctx.bot.latency * 1000)
        await ctx.send(f'Pong!\n{ping}ms')

    @commands.command()
    async def thanksies(self, ctx, channel: discord.TextChannel=None):
        channel = channel or ctx.channel

        for embed_name in ['thanksies', 'thanksies2', 'thanksies3']:
            embed_doc = await self.embeds_collection.find_one({'_id': embed_name})
            embed = embeds.get_embed_from_dict(embed_doc['embed'])

            await channel.send(content="@everyone", embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))
