from discord.ext import commands, tasks

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_reminder.start()
    
    def cog_unload(self):
        self.webhook_reminder.cancel()
    
    @tasks.loop(hours=24, reconnect=True)
    async def webhook_reminder(self):
        guild = self.bot.get_guild(697877261952483471)
        channel = guild.get_channel(728096716884279357)
        webhooks = await channel.webhooks()
        await webhook[0].send('Reminder!')
    
def setup(bot):
    bot.add_cog(Reminders(bot))
