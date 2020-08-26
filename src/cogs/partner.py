from discord.ext import commands

import embeds


class Partner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_collection = bot.db.config

    @commands.command(name='partner', help='Request a partnership with the server.')
    async def partner(self, ctx):
        partnership_doc = await self.config_collection.find_one({'_id': 'partnership'})
        pm_requests_role = ctx.guild.get_role(
            partnership_doc['pm_requests_role'])

        msg = 'Hello! I see that you want to partner with us please be patient and wait for the owners or any pm to be available. Please note that it may take awhile as some are sleeping or busy.'
        embed = embeds.normal(msg, 'Partner!', ctx)
        await ctx.send(content=pm_requests_role.mention, embed=embed)

    @commands.command(name='affiliate', help='Request an affiliation with the server.')
    async def affiliate(self, ctx):
        partnership_doc = await self.config_collection.find_one({'_id': 'partnership'})
        pm_requests_role = ctx.guild.get_role(
            partnership_doc['pm_requests_role'])

        msg = 'Hello! I see you want to affiliate with us please be patient and wait for the owner or any am to be available. Please note that it may take awhile  as some are sleeping or busy.'
        embed = embeds.normal(msg, 'Affiliate!', ctx)
        await ctx.send(content=pm_requests_role.mention, embed=embed)


def setup(bot):
    bot.add_cog(Partner(bot))
