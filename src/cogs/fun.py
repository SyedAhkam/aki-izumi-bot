from discord.ext import commands
from discord.ext.menus import MenuPages, ListPageSource

import aiohttp
import embeds
import random


async def fetch(session, url, headers={}):
    async with session.get(url, headers=headers) as response:
        if not response.status == 200:
            return None
        return await response.json()


def remove_duplicates(initial_list):
    return list(dict.fromkeys(initial_list))


class ListMenu(ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def write_page(self, url, offset):
        len_data = len(self.entries)

        menu_embed = embeds.blank()
        menu_embed.set_image(url=url)

        menu_embed.set_footer(
            text=f"Showing {offset + 1} of {len_data:,} cats.")

        return menu_embed

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        return await self.write_page(entries, offset)


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cats', help='Get pictures of cute cats.')
    async def cats(self, ctx, images=10, page=random.randint(0, 100)):
        async with aiohttp.ClientSession() as session:
            response = await fetch(session, f"https://api.thecatapi.com/v1/images/search?limit={images}&page={page}&order=Desc", headers={'x-api-key': ctx.bot.cat_api_key})
        if not response:
            return await ctx.send('Something went wrong with the api, Please try again later.')

        urls = [x['url'] for x in response]

        pages = MenuPages(source=ListMenu(urls), timeout=60.0)
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(Fun(bot))
