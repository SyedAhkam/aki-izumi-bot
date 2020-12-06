from discord.ext import commands, tasks

import embeds

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embeds_collection = bot.db.embeds
        self.webhook_reminder.start()
    
    def cog_unload(self):
        self.webhook_reminder.cancel()
    
#     @tasks.loop(hours=24, reconnect=True)
#     async def webhook_reminder(self):
#           await self.bot.wait_until_ready()
#         guild = self.bot.get_guild(697877261952483471)
#         channel = guild.get_channel(728096716884279357)
#         webhooks = await channel.webhooks()
#         await webhooks[0].send('Reminder!')

    @tasks.loop(minutes=2, reconnect=True)
    async def webhook_reminder(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(697877261952483471)
        channel = guild.get_channel(728096716884279357)
        webhooks = await channel.webhooks()
        
        embed_doc = await self.embeds_collection.find_one({'_id': 'staff_reminder'})
        embed = embeds.get_embed_from_dict(embed_doc['embed'])
        
        await webhooks[0].send(embed=embed)
    
def setup(bot):
    bot.add_cog(Reminders(bot))
