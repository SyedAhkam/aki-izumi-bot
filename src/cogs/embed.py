from discord.ext import commands

import asyncio
import datetime
import embeds
import json
import discord

color_converter = commands.ColourConverter()


def read_json(filename):
    with open(filename) as f:
        return json.load(f)


def write_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='embed')
    async def embed(self, ctx):
        pass

    @embed.command(name='new')
    async def new(self, ctx, *, name=None):
        if not name:
            return await ctx.send('Please provide a name for embed.')

        embed_data = read_json('assets/embeds.json')
        if name in embed_data:
            return await ctx.send('Embed name already exists, Choose a different name.')

        def check(msg):
            return msg.author == ctx.message.author and msg.channel == ctx.message.channel

        try:
            await ctx.send('What color do you want it to be? (Default: #b5fffd)')
            msg = await ctx.bot.wait_for('message', check=check, timeout=30.0)
            try:
                color = await color_converter.convert(ctx, msg.content)
            except commands.BadArgument:
                if msg.content == 'None':
                    color = '#b5fffd'
                else:
                    await ctx.send('The color provided by you is invalid. Exiting..')
                    return
            await ctx.send(f'Color selected: ```{color}```')

            await ctx.send('Do you want it to have a title? (Say ``None`` if not)')
            msg = await ctx.bot.wait_for('message', check=check, timeout=30.0)
            title = None if msg.content == 'None' else msg.content
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
            await ctx.send(f'Description selected: ```{description}```')

            progress = await ctx.send('Generating embed...')

            embed = embeds.custom(title, color, description, timestamp, url)

            await progress.edit(content='Done!')
            # await ctx.send(embed.to_dict())
            # await ctx.send(embed=embed)

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

    @embed.command(name='preview')
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

    @embed.group(name='edit')
    async def edit(self, ctx):
        pass

    @edit.command(name='footer')
    async def footer(self, ctx, name=None, text=None, icon_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not text:
            return await ctx.send('Text is a required field which you\'re missing.')
        if not icon_url:
            icon_url = discord.Embed.Empty

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]

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

    @edit.command(name='image')
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

        embed = embeds.get_embed_from_dict(embed_raw)
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

    @edit.command(name='thumbnail')
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

        embed = embeds.get_embed_from_dict(embed_raw)
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

    @edit.command(name='author')
    async def author(self, ctx, name=None, author_name=None, icon_url=None, author_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not author_name:
            return await ctx.send('Author name is a required field which you\'re missing.')
        if not icon_url:
            icon_url = discord.Embed.Empty
        if not author_url:
            author_url = discord.Embed.Empty

        embed_data = read_json('assets/embeds.json')

        if not name in embed_data:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        progress = await ctx.send('Working on it...')

        embed_raw = embed_data[name]

        embed = embeds.get_embed_from_dict(embed_raw)
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

    @embed.group(name='field')
    async def field(self, ctx):
        pass

    @field.command(name='add')
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

        embed = embeds.get_embed_from_dict(embed_raw)
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

    @field.command(name='remove')
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

    @field.command(name='clear_all')
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

    @embed.command(name='delete')
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

    @embed.command(name='fix_timestamp')
    async def fix_timestamp(self, ctx, name=None):
        pass

    @embed.command(name='send_here')
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

    @embed.command(name='send_in')
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


def setup(bot):
    bot.add_cog(Embed(bot))
