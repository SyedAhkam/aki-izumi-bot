from discord.ext import commands
from jikanpy import AioJikan

import discord
import os
import datetime
import aiohttp

jikan = AioJikan()


async def fetch(session, url):
    async with session.get(url) as response:
        if not response.status == 200:
            return None
        return await response.json()


class Utilities(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='anime', help='Get information about a specific anime.')
    async def anime(self, ctx, *, anime_name=None):
        if not anime_name:
            await ctx.send('Please provide an anime name to search.')
            return

        search_response = await jikan.search(search_type='anime', query=anime_name)

        if not search_response:
            await ctx.send('Something went wrong with the api, Please try again later.')
            return

        first_result = search_response['results'][0]

        url = first_result['url']
        image_url = first_result['image_url']
        title = first_result['title']
        airing = first_result['airing']
        synopsis = first_result['synopsis']
        type = first_result['type']
        episodes = first_result['episodes']
        score = first_result['score']

        start_date = first_result['start_date']
        start_date_only = start_date.split('T')[0]
        start_datetime_object = datetime.datetime.strptime(
            start_date_only, '%Y-%m-%d')
        start_datetime_string = start_datetime_object.ctime()

        end_date = first_result['end_date']

        if end_date:
            end_date_only = end_date.split('T')[0]
            end_datetime_object = datetime.datetime.strptime(
                end_date_only, '%Y-%m-%d')
            end_datetime_string = end_datetime_object.ctime()
        else:
            end_datetime_string = 'Not ended'

        members = first_result['members']
        rated = first_result['rated']

        embed = discord.Embed(title='My Anime List', description=synopsis,
                              color=0xFFFFFF, timestamp=datetime.datetime.utcnow())

        embed.set_footer(text='Powered by JikanAPI')

        embed.set_thumbnail(url=image_url)

        embed.add_field(name='Title:', value=f'[{title}]({url})', inline=True)
        embed.add_field(name='Airing:', value=airing, inline=True)
        embed.add_field(name='Type:', value=type, inline=True)

        embed.add_field(name='Episodes:', value=episodes, inline=True)
        embed.add_field(name='Rated:', value=rated, inline=True)
        embed.add_field(name='Score:', value=score, inline=True)

        embed.add_field(name='Members:', value=members, inline=True)
        embed.add_field(name='StartDate:',
                        value=start_datetime_string, inline=True)
        embed.add_field(name='EndDate:',
                        value=end_datetime_string, inline=True)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utilities(bot))
