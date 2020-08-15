from discord.ext import commands

import discord
import os
import ast
import json
import embeds


def is_document_exists(collection, id):
    return collection.count_documents({'_id': id}, limit=1)

# For eval command


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class OwnerOnly(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.blacklisted_collection = bot.db.blacklisted

    @commands.command(name='load', help='Loads a specified category.')
    @commands.is_owner()
    async def load(self, ctx, extension):
        ctx.bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} loaded Successfully.')

    @commands.command(name='unload', help='Unloads a specified category.')
    @commands.is_owner()
    async def unload(self, ctx, extension):
        ctx.bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} unloaded Successfully.')

    @commands.command(name='reload', help='Reloads a specified category.')
    @commands.is_owner()
    async def reload(self, ctx, extension):
        ctx.bot.unload_extension(f'cogs.{extension}')
        ctx.bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} reloaded Successfully.')

    @commands.command(name='change_presence', help='Change presence of the bot.')
    @commands.is_owner()
    async def change_presence(self, ctx, presence_type=None, *, presence_text=None):

        types = ['playing', 'streaming', 'listening', 'watching']

        if not presence_type:
            await ctx.send(f'Please provide a type of presence.\nAvailable types: {types}')
            return

        if not presence_text:
            await ctx.send('Please provide a text to be set as the bot\'s presence.')
            return

        if presence_type.lower() == 'playing':
            game = discord.Game(presence_text)
            await ctx.bot.change_presence(status=discord.Status.online, activity=game)

            await ctx.send(f'Changed presence to ``{presence_text}``')

        elif presence_type.lower() == 'streaming':
            stream = discord.Streaming(
                name=presence_text, url='https://www.twitch.tv/syed_ahkam')
            await ctx.bot.change_presence(status=discord.Status.online, activity=stream)

            await ctx.send(f'Changed presence to ``{presence_text}``')

        elif presence_type.lower() == 'listening':
            listening = discord.Activity(
                type=discord.ActivityType.listening, name=presence_text)
            await ctx.bot.change_presence(status=discord.Status.online, activity=listening)

            await ctx.send(f'Changed presence to ``{presence_text}``')

        elif presence_type.lower() == 'watching':
            activity = discord.Activity(
                type=discord.ActivityType.watching, name=presence_text)
            await ctx.bot.change_presence(status=discord.Status.online, activity=activity)

            await ctx.send(f'Changed presence to ``{presence_text}``')

        else:
            await ctx.send(f'Invalid Presence Type\nAvailable types: ``{",".join(types)}``')

    @commands.command(name='logout', help='Logout the bot from discord api.')
    @commands.is_owner()
    async def logout(self, ctx):
        await ctx.send('Bot is now logging out, Bye.')
        print('Bot logged out through logout command.')
        await ctx.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, cmd):
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            'os': os,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))
        await ctx.send(f'```py\n{result}\n```')

    @commands.command(name='blacklist', help='Blacklist a user from using the bot commands.')
    @commands.is_owner()
    async def blacklist(self, ctx, user: commands.UserConverter = None, reason=None):

        if not user:
            await ctx.send('Please specify a user to blacklist.')
            return

        if user.id in ctx.bot.owner_ids:
            return await ctx.send('Can\'t blacklist the owners.')

        # config_data = read_json('assets/config.json')

        # if user.id in config_data['blacklisted_users']:
        #     return await ctx.send('User already blacklisted.')

        if is_document_exists(self.blacklisted_collection, user.id):
            return await ctx.send('This user is already blacklisted.')

        # with open('assets/config.json') as f:
        #     data = json.load(f)

        #     data['blacklisted_users'].append(user.id)

        # write_json('assets/config.json', data)

        # for some reason i gotta do this
        # ctx.bot.unload_extension(f'cogs.events')
        # ctx.bot.load_extension(f'cogs.events')

        self.blacklisted_collection.insert_one({
            '_id': user.id,
            'reason': reason if reason else 'No reason provided'
        })

        embed = embeds.normal(
            f'``{user.name}`` has been blacklisted from using the bot. If you ever change your mind just do ``unblacklist`` command.', 'Blacklisted!', ctx)
        await ctx.send(embed=embed)

    @commands.command(name='unblacklist', help='Unblacklist a user from using the bot commands.')
    @commands.is_owner()
    async def unblacklist(self, ctx, user: commands.UserConverter = None):

        if not user:
            await ctx.send('Please specify a user to unblacklist.')
            return

        # config_data = read_json('assets/config.json')

        # if not user.id in config_data['blacklisted_users']:
        #     return await ctx.send('User not blacklisted.')

        if not is_document_exists(self.blacklisted_collection, user.id):
            return await ctx.send('This user is not blacklisted.')

        # with open('assets/config.json') as f:
        #     data = json.load(f)

        #     data['blacklisted_users'].remove(user.id)

        # write_json('assets/config.json', data)

        # # for some reason i gotta do this
        # ctx.bot.unload_extension(f'cogs.events')
        # ctx.bot.load_extension(f'cogs.events')

        self.blacklisted_collection.delete_one({'_id': user.id})

        embed = embeds.normal(
            f'``{user.name}`` has been removed from the bot blacklist.', 'Unblacklisted!', ctx)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(OwnerOnly(bot))
