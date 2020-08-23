from discord.ext import commands
from discord.ext.menus import MenuPages, ListPageSource
from ago import human

import embeds
import datetime


async def is_document_exists(collection, id):
    return await collection.count_documents({'_id': id}, limit=1)


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
        self.staff_collection = bot.db.staff

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

        is_already_exists = await is_document_exists(self.staff_collection, user.id)
        if is_already_exists:
            return await ctx.send('User already registered.')

        await self.staff_collection.insert_one({
            '_id': user.id,
            'role': user_role,
            'points': 100,
            'history': []
        })

        await ctx.send('All done! Check their profile using the command ``points profile``.')

    @points.command(name='unregister', help='Unregister a user as staff.')
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def unregister(self, ctx, user: commands.MemberConverter = None):
        if not user:
            return await ctx.send('Please provide a user.')

        is_already_exists = await is_document_exists(self.staff_collection, user.id)
        if not is_already_exists:
            return await ctx.send('User not registered.')

        await self.staff_collection.delete_one({'_id': user.id})

        await ctx.send(f'All done! Unregistered ``{user.name}`` successfully.')

    @points.command(name='profile', help='Check the user\'s profile.')
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def profile(self, ctx, user: commands.MemberConverter = None):
        if not user:
            return await ctx.send('Please provide a user.')

        is_already_exists = await is_document_exists(self.staff_collection, user.id)
        if not is_already_exists:
            return await ctx.send('This user isn\'t registered, Please register them using the command ``points register``.')

        user_doc = await self.staff_collection.find_one({'_id': user.id})

        points = user_doc['points']
        user_role = user_doc['role']

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
    async def add(self, ctx, user: commands.MemberConverter = None, points: int = None, *, reason=None):
        if not user:
            return await ctx.send('Please provide a user.')
        if not points:
            return await ctx.send('Please provide the number of points to add.')

        is_already_exists = await is_document_exists(self.staff_collection, user.id)
        if not is_already_exists:
            return await ctx.send('This user isn\'t registered, Please register them using the command ``points register``.')

        await self.staff_collection.find_one_and_update(
            {'_id': user.id},
            {
                '$inc': {'points': points},
                '$push': {'history': {
                    'reason': reason if reason else 'No reason provided.',
                    'action': f'Added {points} points.',
                    'created_at': datetime.datetime.now().timestamp()
                }}
            }
        )

        await ctx.send(f'Successfully added ``{points}`` points to ``{user.name}``. Check their current points using the command ``points profile``.')

    @points.command(name='remove', help='Remove points from a user\'s profile.')
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def remove(self, ctx, user: commands.MemberConverter = None, points: int = None, *, reason=None):
        if not user:
            return await ctx.send('Please provide a user.')
        if not points:
            return await ctx.send('Please provide the number of points to remove.')

        is_already_exists = await is_document_exists(self.staff_collection, user.id)
        if not is_already_exists:
            return await ctx.send('This user isn\'t registered, Please register them using the command ``points register``.')

        await self.staff_collection.find_one_and_update(
            {'_id': user.id},
            {
                '$inc': {'points': -points},
                '$push': {'history': {
                    'reason': reason if reason else 'No reason provided.',
                    'action': f'Removed {points} points.',
                    'created_at': datetime.datetime.now().timestamp()
                }}
            }
        )

        await ctx.send(f'Successfully removed ``{points}`` points from ``{user.name}``. Check their current points using the command ``points profile``.')

    @points.command(name='history', help='Get history of all the old point modifications for a user.')
    @commands.has_any_role(709556238463008768, 697877262737080392)
    async def history(self, ctx, user: commands.MemberConverter = None):
        if not user:
            return await ctx.send('Please provide a user.')

        is_already_exists = await is_document_exists(self.staff_collection, user.id)
        if not is_already_exists:
            return await ctx.send('This user isn\'t registered, Please register them using the command ``points register``.')

        user_doc = await self.staff_collection.find_one({'_id': user.id})

        history = user_doc['history']
        history.sort(key=lambda x: x['created_at'], reverse=True)

        pages = MenuPages(source=HistoryMenu(history, ctx, user),
                          timeout=60.0, clear_reactions_after=True)
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(Points(bot))
