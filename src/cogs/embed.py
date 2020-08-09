from discord.ext import commands

import asyncio
import datetime
import embeds
import json
import discord
import dateparser

color_converter = commands.ColourConverter()


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


def write_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)


def get_keys(user, guild):
    return {
        "user": user.name,
        "user_mention": user.mention,
        "user_id": user.id,
        "user_tag": f'{user.name}#{user.discriminator}',
        "user_color": user.color,
        "user_avatar_url": user.avatar_url,
        "server": guild.name,
        "server_members": len(guild.members),
        "server_icon_url": guild.icon_url
    }


def format_string_with_keys(string, keys):
    return string.format(**keys)


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='embed', invoke_without_command=True, help='A group of commands for making dynamic embeds and saving them for later user.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def embed(self, ctx):
        commands = self.embed.commands
        command_names = [x.name for x in commands]

        emoji = self.bot.get_emoji(740571420203024496)

        description = ''
        for command in command_names:
            to_be_added = f'{str(emoji)} {command}\n'
            description += to_be_added

        embed = embeds.normal(description, 'Available commands', ctx)

        await ctx.send(embed=embed)

    @embed.command(name='new', help='Create a new embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def new(self, ctx, *, name=None):
        if not name:
            return await ctx.send('Please provide a name for embed.')

        embed_data = read_json('assets/embeds.json')
        if name in embed_data:
            return await ctx.send('Embed name already exists, Choose a different name.')

        def check(msg):
            return msg.author == ctx.message.author and msg.channel == ctx.message.channel

        keys = get_keys(ctx.author, ctx.guild)

        try:
            await ctx.send('What color do you want it to be? (Default: #b5fffd)')
            msg = await ctx.bot.wait_for('message', check=check, timeout=30.0)
            try:
                color = await color_converter.convert(ctx, msg.content)
            except commands.BadArgument:
                if msg.content == 'None':
                    color = '#b5fffd'
                elif msg.content == '{user_color}':
                    try:
                        color = format_string_with_keys(
                            msg.content, {"user_color": msg.author.color})
                    except KeyError:
                        await ctx.send('Unknown key detected. Please try again.')
                        return
                else:
                    await ctx.send('The color provided by you is invalid. Exiting..')
                    return
            await ctx.send(f'Color selected: ```{color}```')

            await ctx.send('Do you want it to have a title? (Say ``None`` if not)')
            msg = await ctx.bot.wait_for('message', check=check, timeout=30.0)
            title = None if msg.content == 'None' else msg.content
            if title:
                try:
                    title = format_string_with_keys(msg.content, keys)
                except KeyError:
                    await ctx.send('Unknown key detected. Please try again.')
                    return
            await ctx.send(f'Title selected: ```{title}```')

            await ctx.send('Do you want it to have a url? (Say ``None`` if not)')
            msg = await ctx.bot.wait_for('message', check=check, timeout=30.0)
            url = None if msg.content == 'None' else msg.content
            await ctx.send(f'URL selected: ```{url}```')

            await ctx.send('Do you want it to have a timestamp? (Say ``None`` if not)')
            msg = await ctx.bot.wait_for('message', check=check, timeout=30.0)
            timestamp = None if msg.content == 'None' else datetime.datetime.utcnow()
            await ctx.send(f'Timestamp selected: ```{timestamp}```')

            await ctx.send('Do you want it to have a description? (Say ``None`` if not)')
            msg = await ctx.bot.wait_for('message', check=check, timeout=30.0)
            description = None if msg.content == 'None' else msg.content
            if description:
                try:
                    description = format_string_with_keys(msg.content, keys)
                except KeyError:
                    await ctx.send('Unknown key detected. Please try again.')
                    return
            await ctx.send(f'Description selected: ```{description}```')

            progress = await ctx.send('Generating embed...')

            embed = embeds.custom(title, color, description, timestamp, url)

            await progress.edit(content='Done!')

            await progress.edit(content='Saving for later use...')

            with open('assets/embeds.json') as f:
                data = json.load(f)

                temp = data

                data = {}
                data[name] = embed.to_dict()

                temp.update(data)
            write_json('assets/embeds.json', temp)

            await progress.edit(content='All done, Preview your embed by using ``embed preview`` command!')

        except asyncio.TimeoutError:
            await ctx.send('Timed out, Please try again later.')

    @embed.command(name='preview', help='Preview an embed created already.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def preview(self, ctx, *, name=None):
        if not name:
            return await ctx.send('Please provide an embed name.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        msg = await ctx.send('Just a sec...')

        embed_raw = embed_data[name]

        embed = embeds.get_embed_from_dict(embed_raw)

        await msg.edit(content="Here is your embed:", embed=embed)

    @embed.group(name='edit', invoke_without_command=True, help='A group of commands used to edit an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def edit(self, ctx):
        commands = self.edit.commands
        command_names = [x.name for x in commands]

        emoji = self.bot.get_emoji(740571420203024496)

        description = ''
        for command in command_names:
            to_be_added = f'{str(emoji)} {command}\n'
            description += to_be_added

        embed = embeds.normal(description, 'Available commands', ctx)

        await ctx.send(embed=embed)

    @edit.command(name='footer', help='Edit the footer of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def footer(self, ctx, name=None, text=None, icon_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not text:
            return await ctx.send('Text is a required field which you\'re missing.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]
        keys = get_keys(ctx.author, ctx.guild)

        try:
            text = format_string_with_keys(text, keys)
        except KeyError:
            await ctx.send('Unknown key detected. Please try again.')
            return

        if icon_url:
            try:
                icon_url = format_string_with_keys(icon_url, keys)
            except KeyError:
                await ctx.send('Unknown key detected. Please try again.')
                return
        else:
            icon_url = discord.Embed.Empty

        embed = embeds.get_embed_from_dict(embed_raw)
        embed.set_footer(text=text, icon_url=icon_url)

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @edit.command(name='image', help='Edit the image of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def image(self, ctx, name=None, image_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not image_url:
            return await ctx.send('Image url is a required field which you\'re missing.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]
        keys = get_keys(ctx.author, ctx.guild)

        embed = embeds.get_embed_from_dict(embed_raw)

        try:
            image_url = format_string_with_keys(image_url, keys)
        except KeyError:
            await ctx.send('Unknown key detected. Please try again.')
            return

        embed.set_image(url=image_url)

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @edit.command(name='thumbnail', help='Edit the thumbnail of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def thumbnail(self, ctx, name=None, thumbnail_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not thumbnail_url:
            return await ctx.send('Thumbnail url is a required field which you\'re missing.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]
        keys = get_keys(ctx.author, ctx.guild)

        embed = embeds.get_embed_from_dict(embed_raw)

        try:
            thumbnail_url = format_string_with_keys(thumbnail_url, keys)
        except KeyError:
            await ctx.send('Unknown key detected. Please try again.')
            return

        embed.set_thumbnail(url=thumbnail_url)

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @edit.command(name='author', help='Edit the author of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def author(self, ctx, name=None, author_name=None, icon_url=None, author_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not author_name:
            return await ctx.send('Author name is a required field which you\'re missing.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]
        keys = get_keys(ctx.author, ctx.guild)

        embed = embeds.get_embed_from_dict(embed_raw)

        try:
            author_name = format_string_with_keys(author_name, keys)
        except KeyError:
            await ctx.send('Unknown key detected. Please try again.')
            return

        if icon_url:
            try:
                icon_url = format_string_with_keys(icon_url, keys)
            except KeyError:
                await ctx.send('Unknown key detected. Please try again.')
                return
        else:
            icon_url = discord.Embed.Empty

        if author_url:
            try:
                author_url = format_string_with_keys(author_url, keys)
            except KeyError:
                await ctx.send('Unknown key detected. Please try again.')
                return
        else:
            icon_url = discord.Embed.Empty

        embed.set_author(name=author_name, url=author_url, icon_url=icon_url)

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @edit.command(name='title', help='Edit the title of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def title(self, ctx, name=None, *, new_title=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not new_title:
            return await ctx.send('New title is a required field which you\'re missing.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]
        keys = get_keys(ctx.author, ctx.guild)

        embed = embeds.get_embed_from_dict(embed_raw)

        try:
            new_title = format_string_with_keys(new_title, keys)
        except KeyError:
            await ctx.send('Unknown key detected. Please try again.')
            return

        embed.title = new_title

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @edit.command(name='description', help='Edit the description of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def description(self, ctx, name=None, *, new_description=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not new_description:
            return await ctx.send('New description is a required field which you\'re missing.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]
        keys = get_keys(ctx.author, ctx.guild)

        embed = embeds.get_embed_from_dict(embed_raw)

        try:
            new_description = format_string_with_keys(new_description, keys)
        except KeyError:
            await ctx.send('Unknown key detected. Please try again.')
            return

        embed.description = new_description

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @edit.command(name='url', help='Edit the url of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def url(self, ctx, name=None, *, new_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not new_url:
            return await ctx.send('New url is a required field which you\'re missing.')

        embed_data = read_json('assets/embeds.json')
        keys = get_keys(ctx.author, ctx.guild)

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]

        embed = embeds.get_embed_from_dict(embed_raw)

        try:
            new_url = format_string_with_keys(new_url, keys)
        except KeyError:
            await ctx.send('Unknown key detected. Please try again.')
            return

        embed.url = new_url

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @edit.command(name='timestamp', help='Edit the timestamp of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def timestamp(self, ctx, name=None, *, new_timestamp=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not new_timestamp:
            return await ctx.send('New timestamp is a required field which you\'re missing.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]

        embed = embeds.get_embed_from_dict(embed_raw)

        try:
            parsed_datetime = dateparser.parse(
                new_timestamp, settings={'TO_TIMEZONE': 'UTC'})

            if not parsed_datetime:
                return await ctx.send('Your timestamp is invalid. Exiting...')
        except ValueError:
            return await ctx.send('Your timestamp is invalid. Exiting...')

        embed.timestamp = parsed_datetime

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @edit.command(name='color', help='Edit the color of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def color(self, ctx, name=None, *, new_color=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not new_color:
            return await ctx.send('New color is a required field which you\'re missing.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]

        embed = embeds.get_embed_from_dict(embed_raw)

        try:
            if new_color.lower() == 'default':
                converted_color = '#b5fffd'
            elif new_color == '{user_color}':
                converted_color = ctx.author.color
            else:
                converted_color = await color_converter.convert(ctx, new_color)
        except commands.BadArgument:
            await ctx.send('The color provided by you is invalid. Exiting..')
            return

        converted_hex_color = None

        try:
            if not converted_color.startswith('0x'):
                converted_hex_color = int('0x' + converted_color[1:], 16)
                embed.color = converted_hex_color
            else:
                embed.color = converted_color
        except AttributeError:
            embed.color = converted_color

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @embed.group(name='field', invoke_without_command=True, help='Group of commands for adding fields in an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def field(self, ctx):
        commands = self.field.commands
        command_names = [x.name for x in commands]

        emoji = self.bot.get_emoji(740571420203024496)

        description = ''
        for command in command_names:
            to_be_added = f'{str(emoji)} {command}\n'
            description += to_be_added

        embed = embeds.normal(description, 'Available commands', ctx)

        await ctx.send(embed=embed)

    @field.command(name='add', help='Add a field in an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def add(self, ctx, name=None, field_name=None, field_value=None, is_inline=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not field_name:
            return await ctx.send('Field name is a required field which you\'re missing.')
        if not field_value:
            return await ctx.send('Field value is a required field which you\'re missing.')
        if not is_inline:
            is_inline = True
            await ctx.send('You haven\'t specified if the field is inline or not, Using True by default.')
        else:
            is_inline = is_inline.lower() == "true"

        progress = await ctx.send('Working on it...')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_raw = embed_data[name]
        keys = get_keys(ctx.author, ctx.guild)

        embed = embeds.get_embed_from_dict(embed_raw)

        try:
            field_name = format_string_with_keys(field_name, keys)
        except KeyError:
            await ctx.send('Unknown key detected. Please try again.')
            return

        try:
            field_value = format_string_with_keys(field_value, keys)
        except KeyError:
            await ctx.send('Unknown key detected. Please try again.')
            return

        embed.add_field(name=field_name, value=field_value, inline=is_inline)

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @field.command(name='remove', help='Remove a field from an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def remove(self, ctx, name=None, field_name=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not field_name:
            return await ctx.send('Field name is a required field which you\'re missing.')

        progress = await ctx.send('Working on it...')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        fields = embed_data[name]['fields']

        field_exists = [x for x in fields if x['name'] == field_name]

        if not field_exists:
            return await ctx.send('That field doesn\'t exist. Add it using the command ``embed field add``.')

        index_of_field = fields.index(field_exists[0])

        embed_raw = embed_data[name]

        embed = embeds.get_embed_from_dict(embed_raw)
        embed.remove_field(index_of_field)

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @field.command(name='clear_all', help='Clear all the fields from an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def clear_all(self, ctx, name=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]
        embed = embeds.get_embed_from_dict(embed_raw)

        embed.clear_fields()

        await progress.edit(content='Saving updated embed...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[name] = embed.to_dict()

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @embed.command(name='delete', help='Delete an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def delete(self, ctx, name=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        with open('assets/embeds.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            del temp[name]

            temp.update(data)
        write_json('assets/embeds.json', temp)

        await progress.edit(content='All done!')

    @embed.command(name='send_here', help='Send an embed in the same channel.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def send_here(self, ctx, name=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to send.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_raw = embed_data[name]
        embed = embeds.get_embed_from_dict(embed_raw)

        await ctx.message.delete()
        await ctx.send(embed=embed)

    @embed.command(name='send_in', help='Send an embed in the specified channel.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def send_in(self, ctx, name=None, channel: commands.TextChannelConverter = None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to send.')
        if not channel:
            return await ctx.send('Please provide a channel.')

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_raw = embed_data[name]
        embed = embeds.get_embed_from_dict(embed_raw)

        await ctx.message.delete()
        await channel.send(embed=embed)

    @embed.command(name='test')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def test(self, ctx, *, text):
        keys = get_keys(ctx.author, ctx.guild)

        try:
            formatted = format_string_with_keys(text, keys)
        except KeyError:
            await ctx.send('Unknown key detected. Please try again.')
            return

        await ctx.send(formatted)


def setup(bot):
    bot.add_cog(Embed(bot))
