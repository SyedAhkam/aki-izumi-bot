from discord.ext import commands, tasks
from jikanpy import AioJikan
from ago import human

import discord
import datetime
import dateparser
import embeds

jikan = AioJikan()


async def fetch(session, url):
    async with session.get(url) as response:
        if not response.status == 200:
            return None
        return await response.json()


class Utilities(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.reminders_collection = bot.db.reminders
        self.handle_reminders.start()

    @tasks.loop(seconds=60.0)
    async def handle_reminders(self):
        all_reminders_docs = await self.reminders_collection.find({}).to_list(None)
        for reminder_doc in all_reminders_docs:
            current_time = datetime.datetime.now().timestamp()

            reminder_time = reminder_doc['when']

            #TODO: fix bug and check if this logic is really good
            if (current_time - reminder_time) >= 0:
                user = self.bot.get_user(reminder_doc['user_id'])
                query = reminder_doc['to_be_reminded']
                jump_url = reminder_doc['jump_url']
                embed = embeds.blank()
                embed.set_author(name='Reminder!',
                                 icon_url=self.bot.user.avatar_url)
                embed.description = query
                embed.add_field(name='Jump!', value=f'[Click me!]({jump_url})')
                await user.send(embed=embed)

                await self.reminders_collection.delete_one({'_id': reminder_doc['_id']})

    @commands.command(name='anime', help='Get information about a specific anime.')
    async def anime(self, ctx, *, anime_name=None):
        if not anime_name:
            await ctx.send('Please provide an anime name to search.')
            return

        search_response = await jikan.search(search_type='anime', query=anime_name)

        if not search_response:
            await ctx.send('Something went wrong with the api, Please try again later.')
            return

        first_result = search_response['results'][0]

        url = first_result['url']
        image_url = first_result['image_url']
        title = first_result['title']
        airing = first_result['airing']
        synopsis = first_result['synopsis']
        type = first_result['type']
        episodes = first_result['episodes']
        score = first_result['score']

        start_date = first_result['start_date']
        start_date_only = start_date.split('T')[0]
        start_datetime_object = datetime.datetime.strptime(
            start_date_only, '%Y-%m-%d')
        start_datetime_string = start_datetime_object.ctime()

        end_date = first_result['end_date']

        if end_date:
            end_date_only = end_date.split('T')[0]
            end_datetime_object = datetime.datetime.strptime(
                end_date_only, '%Y-%m-%d')
            end_datetime_string = end_datetime_object.ctime()
        else:
            end_datetime_string = 'Not ended'

        members = first_result['members']
        rated = first_result['rated']

        embed = discord.Embed(title='My Anime List', description=synopsis,
                              color=0xFFFFFF, timestamp=datetime.datetime.utcnow())

        embed.set_footer(text='Powered by JikanAPI')

        embed.set_thumbnail(url=image_url)

        embed.add_field(name='Title:', value=f'[{title}]({url})', inline=True)
        embed.add_field(name='Airing:', value=airing, inline=True)
        embed.add_field(name='Type:', value=type, inline=True)

        embed.add_field(name='Episodes:', value=episodes, inline=True)
        embed.add_field(name='Rated:', value=rated, inline=True)
        embed.add_field(name='Score:', value=score, inline=True)

        embed.add_field(name='Members:', value=members, inline=True)
        embed.add_field(name='StartDate:',
                        value=start_datetime_string, inline=True)
        embed.add_field(name='EndDate:',
                        value=end_datetime_string, inline=True)

        await ctx.send(embed=embed)

    @commands.command(name='remind', aliases=['remindme'], help='Reminds you of something after a certain amount of time.')
    async def remind(self, ctx, when, *, query):
        datetime_parsed = dateparser.parse(when)

        if not datetime_parsed:
            return await ctx.send('The time you provided is invalid.')

        humanized_datetime = human(
            datetime_parsed.timestamp(), past_tense='{}', future_tense='{}')

        await self.reminders_collection.insert_one({
            'when': datetime_parsed.timestamp(),
            'to_be_reminded': query,
            'user_id': ctx.author.id,
            'jump_url': ctx.message.jump_url
        })

        await ctx.send(f'Done! I\'ll remind you about: *{query}* in {humanized_datetime}')


def setup(bot):
    bot.add_cog(Utilities(bot))
