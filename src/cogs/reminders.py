from discord.ext import commands, tasks

import embeds
import asyncio

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embeds_collection = bot.db.embeds
        self.config_collection = bot.db.config
        self.webhook_reminder.start()
    
    def cog_unload(self):
        self.webhook_reminder.cancel()

    async def remind_disboard(self, channel, delay):
        print(f'Sleeping {delay} seconds for disboard reminder')
        await asyncio.sleep(delay)

        embed_doc = await self.embeds_collection.find_one({'_id': 'disboard_reminder'})
        embed = embeds.get_embed_from_dict(embed_doc['embed'])

        await channel.send(embed=embed)

    @commands.Cog.listener(name='on_message')
    async def check_for_disboard_bump(self, message):
        if message.content == '!d bump':
            guild = self.bot.get_guild(697877261952483471)

            disboard_channel_doc = await self.config_collection.find_one({'_id': 'disboard'})
            disboard_channel_obj = guild.get_channel(disboard_channel_doc['disboard_channel'])
            
            await self.bot.loop.create_task(self.remind_disboard(disboard_channel_obj, 7200)) # 2 hours
            print('Scheduled loop for disboard')

    @tasks.loop(hours=24, reconnect=True)
    async def webhook_reminder(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(697877261952483471)
        channel = guild.get_channel(728096716884279357)
        webhooks = await channel.webhooks()
        
        embed_doc = await self.embeds_collection.find_one({'_id': 'staff_reminder'})
        embed = embeds.get_embed_from_dict(embed_doc['embed'])
        
        await webhooks[0].send(content='@everyone', embed=embed)
    
def setup(bot):
    bot.add_cog(Reminders(bot))
