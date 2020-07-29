from discord.ext import commands
import json

def read_json(filename):
    with open(filename) as f:
        return json.load(f)

def write_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='add_nickname_role', help='Add roles to follow the nickname system.')
    @commands.has_permissions(administrator=True)
    async def add_nickname_role(self, ctx, role: commands.RoleConverter=None, *, nickname=None):
        if not role:
            await ctx.send('Please provide a role.')
            return
        if not nickname:
            await ctx.send('Please provide a nickname.')
            return

        nicknames = read_json('assets/nicknames.json')

        if str(role.id) in nicknames:
            await ctx.send('This role is already added.')
            return

        with open('assets/nicknames.json') as f:
            data = json.load(f)

            temp = data

            data = {}
            data[str(role.id)] = {
                'role_id': str(role.id),
                'role_name': role.name,
                'nickname': nickname
            }

            temp.update(data)

        write_json('assets/nicknames.json', temp)
        print(temp)
        await ctx.send(f'Added role ``{role.name}`` with nickname ``{nickname}`` successfully')


def setup(bot):
    bot.add_cog(Config(bot))
