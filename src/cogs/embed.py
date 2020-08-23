from discord.ext import commands
from discord.ext.menus import MenuPages, ListPageSource
from ago import human

import embeds
import datetime
import dateparser
import re
import discord

# TODO: Allow {embed: <embed_name>} keys in other commands

url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
color_converter = commands.ColourConverter()


async def is_document_exists(collection, id):
    return await collection.count_documents({'_id': id}, limit=1)


async def convert_color(ctx, color):
    try:
        if color.lower() == 'default':
            return await color_converter.convert(ctx, '#b5fffd')
        return await color_converter.convert(ctx, color)
    except commands.BadArgument:
        return None


async def parse_datetime(string):
    try:
        return dateparser.parse(string, settings={'TO_TIMEZONE': 'UTC'})
    except ValueError:
        return None


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


async def format_embed(user, guild, embed):
    keys = get_keys(user, guild)

    if embed.title:
        embed.title = format_string_with_keys(embed.title, keys)

    if embed.description:
        embed.description = format_string_with_keys(embed.description, keys)

    if embed.footer:
        footer_text = format_string_with_keys(embed.footer.text, keys)
        embed.set_footer(text=footer_text, icon_url=embed.footer.icon_url)

    if embed.author:
        author_name = format_string_with_keys(embed.author.name, keys)
        embed.set_author(name=author_name, url=embed.author.url,
                         icon_url=embed.author.icon_url)

    if embed.fields:
        new_fields = []
        for field in embed.fields:
            formatted_field_name = format_string_with_keys(field.name, keys)
            formatted_field_value = format_string_with_keys(field.value, keys)
            new_fields.append((formatted_field_name, formatted_field_value))

        embed.clear_fields()

        for name, value in new_fields:
            embed.add_field(name=name, value=value)

    return embed


class EmbedListMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        super().__init__(data, per_page=4)

    async def write_page(self, menu, embeds_list):
        menu_embed = embeds.normal_no_description('Embed List', self.ctx)

        for embed in embeds_list:
            embed_field = embed['embed']
            humanized_created_at = human(embed['created_at'])
            field_value = f'''
                **Type:** ``{embed_field['type']}``
                **Fields:** ``{len(embed_field['fields']) if 'fields' in embed_field else 'None'}``
                **Color:** ``{embed_field['color'] if 'color' in embed_field else 'None'}``
                **Created_at:** ``{humanized_created_at}``
            '''
            menu_embed.add_field(
                name=embed['_id'], value=field_value, inline=False)

        return menu_embed

    async def format_page(self, menu, entries):
        embeds_list = []

        for entry in entries:
            embeds_list.append((entry))
        return await self.write_page(menu, embeds_list)


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embeds_collection = bot.db.embeds

    @commands.group(name='embed', invoke_without_command=True, help='A group of commands for making dynamic embeds and saving them for later use.')
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

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if is_already_exists:
            return await ctx.send('Embed name already exists, Choose a different name.')

        embed = embeds.blank_no_color()
        embed_raw = embed.to_dict()

        await self.embeds_collection.insert_one({
            '_id': name,
            'embed': embed_raw,
            'created_at': datetime.datetime.now().timestamp()
        })

        await ctx.send('All done, Preview your embed by using ``embed preview`` command!')

    @embed.command(name='preview', help='Preview an embed created already.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def preview(self, ctx, *, name=None):
        if not name:
            return await ctx.send('Please provide an embed name.')
        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})

        embed = embeds.get_embed_from_dict(embed_doc['embed'])

        try:
            formatted_embed = await format_embed(ctx.author, ctx.guild, embed)
        except KeyError:
            return await ctx.send('Unknown key detected. Please fix it.')

        await ctx.send(content="Here is your embed:", embed=formatted_embed)

    @embed.command(name='list', help='List all the previously made embeds.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def _list(self, ctx):
        all_embeds = await self.embeds_collection.find({}).to_list(None)

        if not all_embeds:
            return await ctx.send('No embeds found, Create one using ``embed new`` command.')

        menu = MenuPages(
            source=EmbedListMenu(ctx, all_embeds),
            clear_reactions_after=True,
            timeout=60.0
        )
        await menu.start(ctx)

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

    @edit.command(name='title', help='Edit the title of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def title(self, ctx, name=None, *, new_title=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not new_title:
            return await ctx.send('New title is a required field which you\'re missing.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        new_embed = embeds.get_embed_from_dict(embed_raw)

        if new_title.lower() == 'none':
            new_embed.title = discord.Embed.Empty
        else:
            new_embed.title = new_title

        new_embed_raw = new_embed.to_dict()
        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully set the embed title as ```{new_title}```')

    @edit.command(name='description', help='Edit the description of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def description(self, ctx, name=None, *, new_description=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not new_description:
            return await ctx.send('New description is a required field which you\'re missing.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        new_embed = embeds.get_embed_from_dict(embed_raw)

        if new_description.lower() == 'none':
            new_embed.description = discord.Embed.Empty
        else:
            new_embed.description = new_description

        new_embed_raw = new_embed.to_dict()
        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully set the embed description as ```{new_description}```')

    @edit.command(name='color', help='Edit the color of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def color(self, ctx, name=None, *, new_color=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not new_color:
            return await ctx.send('New color is a required field which you\'re missing.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        new_embed = embeds.get_embed_from_dict(embed_raw)

        if new_color.lower() == 'none':
            new_embed.color = discord.Embed.Empty
        else:
            converted_color = await convert_color(ctx, new_color)
            if not converted_color:
                return await ctx.send('The color provided by you is invalid.')

            new_embed.color = converted_color

        new_embed_raw = new_embed.to_dict()

        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully set the embed color as ```{new_color}```')

    @edit.command(name='timestamp', help='Edit the timestamp of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def timestamp(self, ctx, name=None, *, new_timestamp=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not new_timestamp:
            return await ctx.send('New timestamp is a required field which you\'re missing.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']
        new_embed = embeds.get_embed_from_dict(embed_raw)

        if new_timestamp.lower() == 'none':
            new_embed.timestamp = discord.Embed.Empty
        else:
            parsed_datetime = await parse_datetime(new_timestamp)

            if not parsed_datetime:
                return await ctx.send('Invalid timestamp')

            new_embed.timestamp = parsed_datetime

        new_embed_raw = new_embed.to_dict()

        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully set the embed timestamp as ```{new_timestamp}```')

    @edit.command(name='url', help='Edit the url of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def url(self, ctx, name=None, *, new_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not new_url:
            return await ctx.send('New url is a required field which you\'re missing.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']
        new_embed = embeds.get_embed_from_dict(embed_raw)

        if new_url.lower() == 'none':
            new_embed.url = discord.Embed.Empty
        else:
            if not re.search(url_regex, new_url):
                return await ctx.send('URL is invalid.')

            new_embed.url = new_url

        new_embed_raw = new_embed.to_dict()

        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully set the embed url as ```{new_url}```')

    @edit.command(name='footer', help='Edit the footer of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def footer(self, ctx, name=None, text=None, icon_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not text:
            return await ctx.send('Text is a required field which you\'re missing.')

        if not icon_url:
            icon_url = discord.Embed.Empty

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        new_embed = embeds.get_embed_from_dict(embed_raw)

        if text.lower() == 'none':
            text == discord.Embed.Empty

        new_embed.set_footer(text=text, icon_url=icon_url)

        new_embed_raw = new_embed.to_dict()

        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully set the embed footer as ```{text}```')

    @edit.command(name='image', help='Edit the image of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def image(self, ctx, name=None, image_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not image_url:
            return await ctx.send('Image url is a required field which you\'re missing.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        new_embed = embeds.get_embed_from_dict(embed_raw)

        if image_url.lower() == 'none':
            image_url = discord.Embed.Empty

        new_embed.set_image(url=image_url)

        new_embed_raw = new_embed.to_dict()

        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully set the embed image as ```{image_url}```')

    @edit.command(name='thumbnail', help='Edit the thumbnail of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def thumbnail(self, ctx, name=None, thumbnail_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not thumbnail_url:
            return await ctx.send('Thumbnail url is a required field which you\'re missing.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        new_embed = embeds.get_embed_from_dict(embed_raw)

        if thumbnail_url.lower() == 'none':
            thumbnail_url = discord.Embed.Empty

        new_embed.set_thumbnail(url=thumbnail_url)

        new_embed_raw = new_embed.to_dict()

        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully set the embed thumbnail as ```{thumbnail_url}```')

    @edit.command(name='author', help='Edit the author of an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def author(self, ctx, name=None, author_name=None, icon_url=None, author_url=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not author_name:
            return await ctx.send('Author name is a required field which you\'re missing.')
        if not icon_url:
            icon_url = discord.Embed.Empty
        if not author_url:
            author_url = discord.Embed.Empty

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        new_embed = embeds.get_embed_from_dict(embed_raw)

        if author_name.lower() == 'none':
            new_embed.remove_author()
        else:
            new_embed.set_author(
                name=author_name, url=author_url, icon_url=icon_url)

        new_embed_raw = new_embed.to_dict()

        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully set the embed author as ```{author_name}```')

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

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        new_embed = embeds.get_embed_from_dict(embed_raw)
        new_embed.add_field(
            name=field_name, value=field_value, inline=is_inline)

        new_embed_raw = new_embed.to_dict()

        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully added a field with name and value```{field_name}\n{field_value}```')

    @field.command(name='remove', help='Remove a field from an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def remove(self, ctx, name=None, *, field_name=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')
        if not field_name:
            return await ctx.send('Field name is a required field which you\'re missing.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        new_embed = embeds.get_embed_from_dict(embed_raw)

        fields = embed_raw['fields']
        field_exists = [x for x in fields if x['name'] == field_name]

        if not field_exists:
            return await ctx.send('That field doesn\'t exist. Add it using the command ``embed field add``.')

        index_of_field = fields.index(field_exists[0])

        new_embed.remove_field(index_of_field)

        new_embed_raw = new_embed.to_dict()

        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully removed field with name```{field_name}```')

    @field.command(name='clear_all', help='Clear all the fields from an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def clear_all(self, ctx, name=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        new_embed = embeds.get_embed_from_dict(embed_raw)
        new_embed.clear_fields()

        new_embed_raw = new_embed.to_dict()

        await self.embeds_collection.find_one_and_update(
            {'_id': name},
            {'$set': {'embed': new_embed_raw}}
        )

        await ctx.send(f'Successfully cleared all embed fields.')

    @embed.command(name='delete', help='Delete an embed.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def delete(self, ctx, name=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to edit.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        await self.embeds_collection.delete_one({'_id': name})

        await ctx.send(f'Successfully deleted the embed with name {name}')

    @embed.command(name='send_here', help='Send an embed in the same channel.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def send_here(self, ctx, name=None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to send.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        embed = embeds.get_embed_from_dict(embed_raw)

        try:
            formatted_embed = await format_embed(ctx.author, ctx.guild, embed)
        except KeyError:
            return await ctx.send('Unknown key detected. Please fix it.')

        await ctx.send(embed=formatted_embed)
        await ctx.message.delete()

    @embed.command(name='send_in', help='Send an embed in the specified channel.')
    @commands.has_any_role(697877262737080392, 709556238463008768)
    async def send_in(self, ctx, name=None, channel: commands.TextChannelConverter = None):
        if not name:
            return await ctx.send('Please provide the name of embed which you want to send.')
        if not channel:
            return await ctx.send('Please provide a channel.')

        is_already_exists = await is_document_exists(self.embeds_collection, name)
        if not is_already_exists:
            return await ctx.send('This embed doesn\'t exist, Create it using the command ``embed new``.')

        embed_doc = await self.embeds_collection.find_one({'_id': name})
        embed_raw = embed_doc['embed']

        embed = embeds.get_embed_from_dict(embed_raw)

        try:
            formatted_embed = await format_embed(ctx.author, ctx.guild, embed)
        except KeyError:
            return await ctx.send('Unknown key detected. Please fix it.')

        await channel.send(embed=formatted_embed)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Embed(bot))
