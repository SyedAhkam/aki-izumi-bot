from discord.ext import commands


def format_nickname(string, data):
    return string.format(**data)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='change_nickname', help='Change nickname of a person.')
    @commands.has_permissions(administrator=True)
    async def change_nickname(self, ctx, user: commands.MemberConverter = None, *, nickname=None):
        if not user:
            await ctx.send('Please provide a user.')
            return

        if not nickname:
            await ctx.send('Please provide a nickname.')
            return

        formatted_nickname = format_nickname(nickname, {'name': user.name})

        await user.edit(nick=formatted_nickname)
        await ctx.send(f'Successfully changed ``{user.name}\'s`` nickname from ``{user.nick}`` to ``{formatted_nickname}``')

    @commands.command(name='kick', help='Kicks a specified user.')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: commands.MemberConverter = None, *, reason=None):

        if not user:
            await ctx.send('Please provide a user.')
            return

        if user == ctx.author:
            await ctx.send('You can\'t kick yourself.')
            return

        if user.id == ctx.guild.owner_id:
            await ctx.send('You can\'t kick the server owner.')
            return

        await user.kick(reason=reason)
        await ctx.send(f'User {user.name} has been kicked successfully.')

    @commands.command(name='ban', help='Bans a specified user.')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: commands.MemberConverter = None, *, reason=None):

        if not user:
            await ctx.send('Please provide a user.')
            return

        if user == ctx.author:
            await ctx.send('You can\'t ban yourself.')
            return

        if user.id == ctx.guild.owner_id:
            await ctx.send('You can\'t ban the server owner.')
            return

        await user.ban(reason=reason)
        await ctx.send(f'User ``{user.name}`` has been banned successfully.')

    @commands.command(name='unban', help='Unban a specified user.')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: commands.UserConverter = None, *, reason=None):

        if not user:
            await ctx.send('Please provide a user.')
            return

        if user == ctx.author:
            await ctx.send('You can\'t unban yourself.')
            return

        if user.id == ctx.guild.owner_id:
            await ctx.send('You can\'t unban the server owner.')
            return

        banlist = await ctx.guild.bans()

        if not user in banlist:
            return await ctx.send('User is not banned.')

        await ctx.guild.unban(user)
        await ctx.send(f'User {user.name} has been unbanned successfully.')

    @commands.command(name='dm', help='DM\'s a specified user.')
    @commands.has_permissions(administrator=True)
    async def dm(self, ctx, user: commands.MemberConverter = None, *, message=None):

        if not user:
            await ctx.send('Please provide a user.')
            return

        if not message:
            await ctx.send('Please provide a message.')
            return

        await ctx.message.delete()
        await user.create_dm()
        await user.dm_channel.send(message)


def setup(bot):
    bot.add_cog(Moderation(bot))
