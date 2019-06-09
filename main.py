import discord
import twitterColorDetection
import datetime
from discord.ext import commands

class ccCommand:
    def __init__(self, name, responce):
        self.name = name
        self.responce = responce






client = commands.Bot(command_prefix='$')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

async def is_admin(ctx):
    return ctx.message.author.guild_permissions.administrator

##############
###Commands###
##############

@client.command(name='hello')
async def hello(ctx):
    await ctx.send("Hello " + str(ctx.author).split('#')[0] + '!')

@client.command(name='updateicon')
@commands.check(is_admin)
async def updateicon(ctx, color):
    if color == 'auto':
        color = await on_updatecolor(ctx)
    try:
        with open(color + ".png", "rb") as image:
            f = image.read()
            b = bytearray(f)
            await ctx.guild.edit(icon=b)
            await ctx.channel.send("Icon set to " + color)
    #If the file isn't found, then the tower color is probably unknown
    except FileNotFoundError:
        await ctx.send("Error: Unknown tower color.  Options are white, orange, orangewhite, and dark")

@client.command(name='score')
async def score(ctx):
    await ctx.send("Texas beat OU 48 to 45 in the Red River Rivalry with a last second field goal by Dicker the Kicker! :metal:")

@client.command(name='time')
async def timeCommand(ctx):
    currentDT = datetime.datetime.now()
    outTime = currentDT.strftime("%I:%M %p")
    await ctx.send("It is " + outTime + " and OU still sucks!")

@client.command(name='cc')
@commands.check(is_admin)
async def cc(ctx, *args):
    #If zero arguments, list all commands
    if len(args) == 0:
        return
    #If one argument, delete that command
    if len(args) == 1:
        return
    #If 2 or more arguments, combine them and modify database
    if len(args) >= 2:
        newCC = ccCommand(args[0], ' '.join(args[1:]))
        await ctx.send("Command " + newCC.name + " with link " + newCC.responce)

#Used to automatically update color
async def on_updatecolor(ctx):
    try:
        towerRGB = twitterColorDetection.getRGB()
        towerColor = twitterColorDetection.getColorNames(towerRGB[0], towerRGB[1])
        #Determine the correct icon
        towerColorName = towerColor[0].lower() + towerColor[1].lower()
        possibleColors = {
            "orangeorange": "orange",
            "whiteorange": "orangewhite",
            "whitewhite": "white",
            "darkdark": "dark"
        }
        towerColorName = possibleColors[towerColorName]

        return towerColorName


    except Exception as e:
        await ctx.send("Error: " + str(e))


keyFile = open('keys.txt', 'r')
key = keyFile.read()
client.run(key)