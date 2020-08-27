from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from discord.ext.menus import MenuPages, ListPageSource

import discord
import embeds

color_converter = commands.ColourConverter()


def get_next_level_xp(level):
    xp = 5*(int(level)**2)+50*int(level)+100
    return xp


def create_thumbnail(avatar_img, bg_img):
    bigsize = (avatar_img.size[0] * 3, avatar_img.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(avatar_img.size, Image.ANTIALIAS)
    avatar_img.putalpha(mask)

    bg_img.paste(avatar_img, (20, 8), avatar_img)

    return bg_img


def create_progress_bar(progressbar_bg_img, current_xp, next_level_xp, color=(98, 211, 245)):
    draw = ImageDraw.Draw(progressbar_bg_img)

    percentage_of_xp = round((current_xp / next_level_xp) * 100)
    progress_value = round((percentage_of_xp / 100) * 600)

    x, y, diam = progress_value, 8, 34
    draw.ellipse([x, y, x+diam, y+diam], fill=color)

    ImageDraw.floodfill(progressbar_bg_img, xy=(
        14, 24), value=color, thresh=40)

    return progressbar_bg_img


def draw_text(base_img, text, color, coords, font, font_size):
    base_img = base_img.convert('RGBA')
    txt = Image.new('RGBA', base_img.size, (255, 255, 255, 0))

    fnt = ImageFont.truetype(font, font_size)
    d = ImageDraw.Draw(txt)

    d.text(coords, text, font=fnt, fill=color)

    return Image.alpha_composite(base_img, txt)


def generate_rank_img(user_avatar, bg_color, user, xp_doc, user_rank):
    avatar_img = Image.open(BytesIO(user_avatar)).resize((65, 65))
    decorations_img_transparent = Image.open('../assets/rank_decorations.png')
    progressbar_bg = Image.open(
        '../assets/rank_progressbar_bg.png').convert('RGB')

    current_xp = xp_doc['xp']
    required_xp_for_next_level = get_next_level_xp(xp_doc['level'] + 1)

    with Image.new('RGB', (400, 100), color=bg_color.value) as bg_img:

        bg_img = create_thumbnail(avatar_img, bg_img)

        progressbar_img = create_progress_bar(
            progressbar_bg,
            current_xp,
            required_xp_for_next_level,
            color=bg_color.to_rgb()
        ).resize((275, 30))
        bg_img.paste(progressbar_img, (100, 70))

        bg_img = draw_text(
            bg_img,
            user.name,
            (0, 0, 0, 255),
            (15, 75),
            '../assets/Oswald-Medium.ttf',
            15
        )
        bg_img = draw_text(
            bg_img,
            f'{current_xp}/{required_xp_for_next_level}',
            (255, 255, 255, 255),
            (190, 73),
            '../assets/Oswald-ExtraLight.ttf',
            15
        )
        bg_img = draw_text(
            bg_img,
            str(xp_doc['level'] + 1),
            (0, 0, 0, 255),
            (380, 73),
            '../assets/Oswald-ExtraLight.ttf',
            15
        )
        bg_img = draw_text(
            bg_img,
            'Ranking:',
            (0, 0, 0, 255),
            (95, 5),
            '../assets/Oswald-Medium.ttf',
            25
        )
        bg_img = draw_text(
            bg_img,
            str(user_rank + 1),
            (0, 0, 0, 255),
            (200, 10),
            '../assets/Oswald-ExtraLight.ttf',
            20
        )
        bg_img = draw_text(
            bg_img,
            'Weekly:',
            (0, 0, 0, 255),
            (95, 32),
            '../assets/Oswald-Medium.ttf',
            25
        )
        bg_img = draw_text(
            bg_img,
            'ComingSoon',
            (0, 0, 0, 255),
            (200, 37),
            '../assets/Oswald-ExtraLight.ttf',
            20
        )
        bg_img = draw_text(
            bg_img,
            str(xp_doc['level']),
            (0, 0, 0, 255),
            (345, 3),
            '../assets/Oswald-ExtraLight.ttf',
            50
        )

        output_buffer = BytesIO()
        bg_img.save(output_buffer, 'png')
        output_buffer.seek(0)

        return output_buffer


class LeaderboardMenu(ListPageSource):
    def __init__(self, data, ctx):
        super().__init__(data, per_page=5)
        self.ctx = ctx

    async def write_page(self, data, fields_list, offset):
        menu_embed = embeds.normal_no_description('Leaderboard!', self.ctx)
        for field in fields_list:
            member = self.ctx.guild.get_member(field[1]['_id'])
            field_name = f'#{field[0] + 1} - {member.name}'
            xp = field[1]['xp']
            level = field[1]['level']
            field_value = f'ID: ``{member.id}``\nXP: ``{xp}``\nLevel: ``{level}``'
            menu_embed.add_field(
                name=field_name, value=field_value, inline=False)

        return menu_embed

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        fields_list = []
        for entry in entries:
            fields_list.append(entry)

        return await self.write_page(entries, fields_list, offset)


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels_collection = bot.db.levels
        self.config_collection = bot.db.config

    @commands.command()
    async def test(self, ctx, level: int):
        level_xp = get_next_level_xp(level)
        await ctx.send(level_xp)

    @commands.command(name='rank', help='Check your current xp and level')
    async def rank(self, ctx, user: commands.MemberConverter = None):
        if user:

            if user.bot:
                return await ctx.send('Bots can\'t level up.')

            user_xp_doc = await self.levels_collection.find_one({'_id': user.id})
            avatar = user.avatar_url_as(format='png')
            avatar_file_obj = await avatar.read()

        else:
            user_xp_doc = await self.levels_collection.find_one({'_id': ctx.author.id})

            avatar = ctx.author.avatar_url_as(format='png')
            avatar_file_obj = await avatar.read()

        all_xp_docs = await self.levels_collection.find({}).to_list(None)
        sorted_docs = [i for i in sorted(
            enumerate(all_xp_docs), key=lambda x:x[1]['xp'], reverse=True)]

        rank_user = user if user else ctx.author
        user_rank = [i[0]
                     for i in sorted_docs if i[1]['_id'] == rank_user.id][0]

        default_color = await color_converter.convert(ctx, '#b5fffd')
        color = default_color if rank_user.color.value == 0 else rank_user.color

        rank_img = generate_rank_img(
            avatar_file_obj, color, rank_user, user_xp_doc, user_rank)

        await ctx.send(file=discord.File(rank_img, filename='rank.png'))

    @commands.command(name='leaderboard', help='Check the leaderboard of xp\'s')
    async def leaderboard(self, ctx):
        all_xp_docs = await self.levels_collection.find({}).to_list(None)
        sorted_docs = [i for i in sorted(
            enumerate(all_xp_docs), key=lambda x:x[1]['xp'], reverse=True)]

        menu = MenuPages(source=LeaderboardMenu(sorted_docs, ctx),
                         timeout=60.0, clear_reactions_after=True)
        await menu.start(ctx)

    @commands.command(name='modifyxp', help='Add or remove xp from a user')
    @commands.has_permissions(administrator=True)
    async def modifyxp(self, ctx, action=None, quantity=None, user: commands.MemberConverter = None):
        if not action:
            return await ctx.send('Please provide an action like ``add/remove``.')
        if not quantity:
            return await ctx.send('Please provide a quantity.')
        if not user:
            return await ctx.send('Please provide a user.')

        if action == 'add':
            await self.levels_collection.find_one_and_update(
                {'_id': ctx.author.id},
                {'$inc': {
                    'xp': int(quantity)
                }}
            )
            await ctx.send(f'Added ``{quantity}`` to {user.name}\'s xp.')
        elif action == 'remove':
            await self.levels_collection.find_one_and_update(
                {'_id': ctx.author.id},
                {'$inc': {
                    'xp': - int(quantity)
                }}
            )
            await ctx.send(f'Removed ``{quantity}`` from {user.name}\'s xp.')
        else:
            await ctx.send('Invalid action.')

    @commands.command(name='ignore_channel_xp', help='Make the bot ignore a channel for xp.')
    @commands.has_permissions(administrator=True)
    async def ignore_channel_xp(self, ctx, channel: commands.TextChannelConverter = None):
        if not channel:
            return await ctx.send('Please provide a channel.')

        await self.config_collection.find_one_and_update(
            {'_id': 'levels'},
            {'$push': {
                'ignored_channels': channel.id
            }}
        )

        await ctx.send(f'{channel.name} will be ignored from now on.')


def setup(bot):
    bot.add_cog(Levels(bot))
