from discord.ext import commands
import logging
import embeds


class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ignored = (commands.errors.CommandNotFound)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, "original", error)

        # Ignore some errors
        if isinstance(error, self.ignored):
            return

        # Catching other errors
        if isinstance(error, commands.errors.DisabledCommand):
            return await ctx.send('This command has been disabled by the owner, Ask them to enable it.')

        if isinstance(error, commands.errors.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} command can not be used in Private Messages.')
            except commands.errors.Forbidden:
                pass

        if isinstance(error, commands.errors.CheckFailure):
            if isinstance(error, commands.errors.NotOwner):
                embed = embeds.error(
                    'This command is only accessible by the owner of the bot.', 'Error', ctx)
                return await ctx.send('This command is only accessible by the owner of the bot.')

            if isinstance(error, commands.errors.MissingPermissions):
                embed = embeds.error(
                    f'Looks like you don\'t have permission to access this command.\nPermissions required: ``{error.missing_perms}``', 'Error', ctx)
                await ctx.send(embed=embed)
                return

            if isinstance(error, commands.errors.BotMissingPermissions):
                embed = embeds.error(
                    f'Bot need these permissions to run that command, ``{error.missing_perms}``', 'Error', ctx)
                await ctx.send(embed=embed)
                return

            if isinstance(error, commands.errors.MissingRole):
                embed = embeds.error(
                    f'You need this role to access this command: ``{error.missing_role}``', 'Error', ctx)
                await ctx.send(embed=embed)
                return

        if isinstance(error, commands.errors.BadArgument):
            embed = embeds.error(
                'Invalid arguments given, please check the help command.', 'Error', ctx)
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.errors.CommandOnCooldown):
            embed = embeds.error(
                f'This command is on cooldown.\n Please wait ``{round(error.retry_after)}`` more seconds.', 'Error', ctx)
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.errors.ExtensionError):
            if isinstance(error, commands.errors.ExtensionNotFound):
                embed = embeds.error(
                    f'Extension with name ``{error.name}`` not found.', 'Error', ctx)
                await ctx.send(embed=embed)
                return

            if isinstance(error, commands.errors.ExtensionAlreadyLoaded):
                embed = embeds.error(
                    f'Extension with name ``{error.name}`` already loaded.', 'Error', ctx)
                return await ctx.send(embed=embed)

            if isinstance(error, commands.errors.ExtensionFailed):
                embed = embeds.error(
                    f'Extension with name ``{error.name}`` failed to load.', 'Error', ctx)
                return await ctx.send(embed)

        embed = embeds.error(
            'An unexpected error occured, Please report to the owner.', 'Error', ctx)
        await ctx.send(embed=embed)
        raise error


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
