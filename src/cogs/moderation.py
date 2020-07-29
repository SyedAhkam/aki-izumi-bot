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

    @commands.command(name='verify', help='Give users the verified role.')
    @commands.has_any_role(697877262737080390, 697877262737080391)
    async def verified(self, ctx, user: commands.MemberConverter = None):
        if not user:
            await ctx.send('Please provide a user.')
            return

        verified_role = ctx.guild.get_role(697877261952483477)

        await user.add_roles(verified_role)
        await ctx.send(f'Successfully added the verified role to ``{user.name}``')


def setup(bot):
    bot.add_cog(Moderation(bot))
