import discord
from discord.ext import commands
import matplotlib.pyplot as plt
#import pandas as pd

#Discord client
client = commands.Bot(command_prefix='$')

async def joinChartGenerator(ctx):
    totalUsers = 0
    dates = []
    #df = pd.DataFrame(columns=['number', 'joindate'])
    print("Gathering Users")
    allUsers = ctx.guild.members
    for i in allUsers:
        totalUsers += 1
        dates.append(i.joined_at)
        #df[totalUsers] = i.joined_at
        #print(f"User {i.name} joined at {i.joined_at}")
    print(f"Total Users: {str(totalUsers)}")
    dates.sort()
    #print(dates)

    #Plot with matplotlib
    #y axis will be members
    y = range(totalUsers)
    plt.suptitle(ctx.guild.name)
    plt.ylabel("Number of Users")
    plt.xlabel("Join Date")
    plt.plot_date(dates, y)    
    plt.locator_params(axis='x', nbins=8)
    plt.savefig("plot.png")

    #Upload to discord
    await ctx.send(file=discord.File('plot.png'))

async def is_admin(ctx):
    #permissions = ctx.message.author.roles
    role = discord.utils.get(ctx.guild.roles, id=490250496028704768)
    #Moderator on UT Discord
    if role in ctx.author.roles:
        return True
    #Admin on test server
    role = discord.utils.get(ctx.guild.roles, id=527944399649243146)
    if role in ctx.author.roles:
        return True
    else:
        return False

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command(name="usergraph")
async def usergraph(ctx):
    await joinChartGenerator(ctx)


keyFile = open('keys.txt', 'r')
key = keyFile.read()
client.run(key)


