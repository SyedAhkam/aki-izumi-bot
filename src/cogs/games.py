from discord.ext import commands
from igdb.wrapper import IGDBWrapper
from discord.ext.menus import MenuPages, ListPageSource

import embeds
import json
import datetime


def get_category_string(category: int):
    categories = {
        0: "Main Game",
        1: "DLC Addon",
        2: "Expansion",
        3: "Bundle",
        4: "Standalone Expansion",
        5: "Mod",
        6: "Episode"
    }

    return categories[category]


class ComingSoonMenu(ListPageSource):
    def __init__(self, data, ctx):
        super().__init__(data, per_page=1)
        self.ctx = ctx

    async def write_page(self, data, offset):
        len_data = len(self.entries)

        if not 'summary' in data:
            data['summary'] = 'No summary about the game.'
        if not 'category' in data:
            data['category'] = 'None'
        if not 'popularity' in data:
            data['popularity'] = 'None'

        menu_embed = embeds.normal(data['summary'], 'Coming soon!', self.ctx)

        menu_embed.add_field(name='Name:', value=data['name'], inline=True)
        menu_embed.add_field(name='Category:', value=get_category_string(
            data['category']), inline=True)

        if not 'rating' in data:
            menu_embed.add_field(name='Rating:', value='None', inline=True)
        else:
            menu_embed.add_field(name='Rating:', value=round(
                data['rating'], 2), inline=True)

        menu_embed.add_field(name='Popularity:',
                             value=round(data['popularity'], 2), inline=True)

        if 'url' in data:
            url = data['url']
            menu_embed.add_field(name='URL:', value=f'[Click me!]({url})')

        menu_embed.set_footer(
            text=f"Showing {offset + 1} of {len_data:,} games. | Powered by IGDB API")

        return menu_embed

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        return await self.write_page(entries, offset)


class NewGamesMenu(ListPageSource):
    def __init__(self, data, ctx):
        super().__init__(data, per_page=1)
        self.ctx = ctx

    async def write_page(self, data, offset):
        len_data = len(self.entries)

        if not 'summary' in data:
            data['summary'] = 'No summary about the game.'
        if not 'category' in data:
            data['category'] = 'None'
        if not 'popularity' in data:
            data['popularity'] = 'None'

        menu_embed = embeds.normal(data['summary'], 'New!', self.ctx)

        menu_embed.add_field(name='Name:', value=data['name'], inline=True)
        menu_embed.add_field(name='Category:', value=get_category_string(
            data['category']), inline=True)

        if not 'rating' in data:
            menu_embed.add_field(name='Rating:', value='None', inline=True)
        else:
            menu_embed.add_field(name='Rating:', value=round(
                data['rating'], 2), inline=True)

        menu_embed.add_field(name='Popularity:',
                             value=round(data['popularity'], 2), inline=True)

        if 'url' in data:
            url = data['url']
            menu_embed.add_field(name='URL:', value=f'[Click me!]({url})')

        menu_embed.set_footer(
            text=f"Showing {offset + 1} of {len_data:,} games. | Powered by IGDB API")

        return menu_embed

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        return await self.write_page(entries, offset)


class PopularGamesList(ListPageSource):
    def __init__(self, data, ctx):
        super().__init__(data, per_page=1)
        self.ctx = ctx

    async def write_page(self, data, offset):
        len_data = len(self.entries)

        if not 'summary' in data:
            data['summary'] = 'No summary about the game.'
        if not 'category' in data:
            data['category'] = 'None'
        if not 'popularity' in data:
            data['popularity'] = 'None'

        menu_embed = embeds.normal(data['summary'], 'Popular!', self.ctx)

        menu_embed.add_field(name='Name:', value=data['name'], inline=True)
        menu_embed.add_field(name='Category:', value=get_category_string(
            data['category']), inline=True)

        if not 'rating' in data:
            menu_embed.add_field(name='Rating:', value='None', inline=True)
        else:
            menu_embed.add_field(name='Rating:', value=round(
                data['rating'], 2), inline=True)

        menu_embed.add_field(name='Popularity:',
                             value=round(data['popularity'], 2), inline=True)

        if 'url' in data:
            url = data['url']
            menu_embed.add_field(name='URL:', value=f'[Click me!]({url})')

        menu_embed.set_footer(
            text=f"Showing {offset + 1} of {len_data:,} games. | Powered by IGDB API")

        return menu_embed

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        return await self.write_page(entries, offset)


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.igdb = IGDBWrapper(bot.igdb_api_key)

    @commands.group(name='games', help='Group of commands for all types of gaming info.', invoke_without_command=True)
    async def games(self, ctx):
        commands = self.games.commands
        emoji = self.bot.get_emoji(740571420203024496)

        embed = embeds.list_commands_in_group(commands, emoji, ctx)

        await ctx.send(embed=embed)

    @games.command(name='game', help='Get info about a specific game.')
    async def game(self, ctx, *, game_name=None):
        if not game_name:
            return await ctx.send('Please provide a game name.')

        response = self.igdb.api_request(
            'games', f'search "{game_name}"; fields *; limit 1;')
        str_response = response.decode('utf-8')
        data = json.loads(str_response)

        try:
            data = data[0]
        except IndexError:
            return await ctx.send(f'No game with name ``{game_name}`` found, Try again later.')

        if not 'summary' in data:
            data['summary'] = 'No summary about the game.'
        if not 'category' in data:
            data['category'] = 'None'
        if not 'popularity' in data:
            data['popularity'] = 'None'

        try:
            platforms_list = [str(x) for x in data['platforms']]
            response2 = self.igdb.api_request(
                'platforms', f'where id = ({", ".join(platforms_list)}); fields name; limit 1;')
            str_response = response2.decode('utf-8')
            platforms = json.loads(str_response)

            platforms_names = [x['name'] for x in platforms]
        except KeyError:
            platforms_names = 'Not specified'

        embed = embeds.normal(data['summary'], 'Game info', ctx)

        if 'cover' in data:
            cover = data['cover']
            response3 = self.igdb.api_request(
                'covers', f'where id = {cover}; fields *; limit 1;')
            str_response = response3.decode('utf-8')
            cover = json.loads(str_response)[0]

            embed.set_thumbnail(url='https:' + cover['url'])

        embed.add_field(name='Name:', value=data['name'], inline=True)
        embed.add_field(name='Category:', value=get_category_string(
            data['category']), inline=True)
        embed.add_field(name='Platforms:',
                        value=", ".join(platforms_names), inline=True)

        if not 'rating' in data:
            embed.add_field(name='Rating:', value='None', inline=True)
        else:
            embed.add_field(name='Rating:', value=round(
                data['rating'], 2), inline=True)
        embed.add_field(name='Popularity:',
                        value=round(data['popularity'], 2), inline=True)
        if 'url' in data:
            url = data['url']
            embed.add_field(name='URL:', value=f'[Click me!]({url})')

        embed.set_footer(text='Powered by IGDB API',
                         icon_url=ctx.bot.user.avatar_url)

        await ctx.send(embed=embed)

    @games.command(name='coming_soon', help='Get information about upcoming games.')
    async def coming_soon(self, ctx, platform=None):
        if not platform:
            return await ctx.send('Please provide a platform name.')

        timestamp = round(datetime.datetime.utcnow().timestamp())

        response = self.igdb.api_request(
            'platforms',
            f'fields *; limit 1; search "{platform}";'
        )
        str_response = response.decode('utf-8')
        platform = json.loads(str_response)
        platform = platform[0] if platform else None

        if not platform:
            return await ctx.send('This platform doesn\'t exist.')

        platform_id = platform['id']

        response2 = self.igdb.api_request(
            'release_dates',
            f'fields *; where game.platforms = {platform_id} & date > {timestamp}; sort date asc;'
        )
        str_response = response2.decode('utf-8')
        games = json.loads(str_response)

        if not games:
            return await ctx.send('No games found for this platform.')

        games_id_list = [str(x['game']) for x in games]

        response2 = self.igdb.api_request(
            'games', f'where id = ({", ".join(games_id_list)}); fields *;')
        str_response = response2.decode('utf-8')
        games_list = json.loads(str_response)

        pages = MenuPages(source=ComingSoonMenu(games_list, ctx),
                          timeout=60.0, clear_reactions_after=True)
        await pages.start(ctx)

    @games.command(name='new', help='Get information about newly released games.')
    async def new(self, ctx, platform=None):
        if not platform:
            return await ctx.send('Please provide a platform name.')

        timestamp = round(datetime.datetime.utcnow().timestamp())

        response = self.igdb.api_request(
            'platforms',
            f'fields *; limit 1; search "{platform}";'
        )
        str_response = response.decode('utf-8')
        platform = json.loads(str_response)
        platform = platform[0] if platform else None

        if not platform:
            return await ctx.send('This platform doesn\'t exist.')

        platform_id = platform['id']

        response2 = self.igdb.api_request(
            'release_dates',
            f'fields *; where game.platforms = {platform_id} & date < {timestamp}; sort date desc;'
        )
        str_response = response2.decode('utf-8')
        games = json.loads(str_response)

        if not games:
            return await ctx.send('No games found for this platform.')

        games_id_list = [str(x['game']) for x in games]

        response2 = self.igdb.api_request(
            'games', f'where id = ({", ".join(games_id_list)}); fields *;')
        str_response = response2.decode('utf-8')
        games_list = json.loads(str_response)

        pages = MenuPages(source=NewGamesMenu(games_list, ctx),
                          timeout=60.0, clear_reactions_after=True)
        await pages.start(ctx)

    @games.command(name='popular', help='Get info about popular games.')
    async def popular(self, ctx):

        response = self.igdb.api_request(
            'games',
            f'fields *; sort popularity desc;'
        )
        str_response = response.decode('utf-8')
        games_list = json.loads(str_response)

        pages = MenuPages(source=PopularGamesList(games_list, ctx),
                          timeout=60.0, clear_reactions_after=True)
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(Games(bot))
