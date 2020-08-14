from discord.ext import commands
from discord.ext.menus import MenuPages, ListPageSource
from ago import human

import embeds
import json
import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


def write_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, cls=DateTimeEncoder)


class HistoryMenu(ListPageSource):
    def __init__(self, data, ctx, user):
        super().__init__(data, per_page=1)
        self.ctx = ctx
        self.user = user

    async def write_page(self, data, offset):
        len_data = len(self.entries)

        menu_embed = embeds.normal_no_description('History!', self.ctx)

        menu_embed.add_field(name='User:', value=self.user.name, inline=True)
        menu_embed.add_field(name='Action:', value=data['action'], inline=True)
        menu_embed.add_field(name='Created At:',
                             value=human(data['created_at']), inline=True)

        menu_embed.add_field(
            name='Reason:', value=data['reason'], inline=False)

        menu_embed.set_footer(
            text=f"Showing {offset + 1} of {len_data:,} cases")

        return menu_embed

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        return await self.write_page(entries, offset)


class Points(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='points', help='Group of commands to manage the point system for staff.', invoke_without_command=True)
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def points(self, ctx):
        commands = self.points.commands
        command_names = [x.name for x in commands]

        emoji = self.bot.get_emoji(740571420203024496)

        description = ''
        for command in command_names:
            to_be_added = f'{str(emoji)} {command}\n'
            description += to_be_added

        embed = embeds.normal(description, 'Available commands', ctx)

        await ctx.send(embed=embed)

    @points.command(name='info', help='Info about the point system.')
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def info(self, ctx):
        await ctx.send('https://docs.google.com/document/d/1uQ8VhfYfjXs-Ig5KJ2yaM2tP53ss37O74K3ePq3wcK4/edit?usp=sharing')

    @points.command(name='register', help='Register a user as staff.')
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def register(self, ctx, user: commands.MemberConverter = None, *, user_role=None):
        if not user:
            return await ctx.send('Please provide a user.')

        if not user_role:
            return await ctx.send('Please provide a user role.')

        points_data = read_json('assets/points.json')

        if str(user.id) in points_data:
            return await ctx.send('User already registered.')

        with open('assets/points.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[str(user.id)] = {
                "role": user_role,
                "points": 100,
                "history": []
            }

            temp.update(data)
        write_json('assets/points.json', temp)

        await ctx.send('All done! Check their profile using the command ``points profile``.')

    @points.command(name='unregister', help='Unregister a user as staff.')
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def unregister(self, ctx, user: commands.MemberConverter = None):
        if not user:
            return await ctx.send('Please provide a user.')

        points_data = read_json('assets/points.json')

        if not str(user.id) in points_data:
            return await ctx.send('User not registered.')

        with open('assets/points.json') as f:
            data = json.load(f)

            del data[str(user.id)]

        write_json('assets/points.json', data)

        await ctx.send(f'All done! Unregistered ``{user.name}`` successfully.')

    @points.command(name='profile', help='Check the user\'s profile.')
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def profile(self, ctx, user: commands.MemberConverter = None):
        if not user:
            return await ctx.send('Please provide a user.')

        points_data = read_json('assets/points.json')

        if not str(user.id) in points_data:
            return await ctx.send('This user isn\'t registered, Please register them using the command ``points register``.')

        user_info = points_data[str(user.id)]
        points = user_info['points']
        user_role = user_info['role']

        embed = embeds.normal_no_description('Profile!', ctx)

        embed.add_field(name='Id:', value=user.id, inline=True)
        embed.add_field(name='Name:', value=user.name, inline=True)
        embed.add_field(name='Joined At:', value=human(
            user.joined_at), inline=True)

        embed.add_field(name='Points:', value=points, inline=True)
        embed.add_field(name='Role:', value=user_role, inline=True)

        embed.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=embed)

    @points.command(name='add', help='Add points to a user\'s profile.')
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def add(self, ctx, user: commands.MemberConverter = None, points=None, *, reason=None):
        if not user:
            return await ctx.send('Please provide a user.')
        if not points:
            return await ctx.send('Please provide the number of points to add.')

        points_data = read_json('assets/points.json')

        if not str(user.id) in points_data:
            return await ctx.send('This user isn\'t registered, Please register them using the command ``points register``.')

        with open('assets/points.json') as f:
            data = json.load(f)

            data[str(user.id)]['points'] += int(points)
            data[str(user.id)]['history'].append({
                "reason": reason if reason else "No reason provided",
                "action": f"Added {points} points.",
                "created_at": datetime.datetime.now().timestamp()
            })

        write_json('assets/points.json', data)

        await ctx.send(f'Successfully added ``{points}`` points to ``{user.name}``. Check their current points using the command ``points profile``.')

    @points.command(name='remove', help='Remove points from a user\'s profile.')
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def remove(self, ctx, user: commands.MemberConverter = None, points=None, *, reason=None):
        if not user:
            return await ctx.send('Please provide a user.')
        if not points:
            return await ctx.send('Please provide the number of points to remove.')

        points_data = read_json('assets/points.json')

        if not str(user.id) in points_data:
            return await ctx.send('This user isn\'t registered, Please register them using the command ``points register``.')

        with open('assets/points.json') as f:
            data = json.load(f)

            data[str(user.id)]['points'] -= int(points)
            data[str(user.id)]['history'].append({
                "reason": reason if reason else "No reason provided",
                "action": f"Removed {points} points.",
                "created_at": datetime.datetime.now().timestamp()
            })

        write_json('assets/points.json', data)

        await ctx.send(f'Successfully removed ``{points}`` points from ``{user.name}``. Check their current points using the command ``points profile``.')

    @points.command(name='history', help='Get history of all the old point modifications for a user.')
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def history(self, ctx, user: commands.MemberConverter = None):
        if not user:
            return await ctx.send('Please provide a user.')

        points_data = read_json('assets/points.json')

        if not str(user.id) in points_data:
            return await ctx.send('This user isn\'t registered, Please register them using the command ``points register``.')

        user_data = points_data[str(user.id)]
        history = user_data['history']
        history.sort(key=lambda x: x['created_at'], reverse=True)

        pages = MenuPages(source=HistoryMenu(history, ctx, user),
                          timeout=60.0, clear_reactions_after=True)
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(Points(bot))
