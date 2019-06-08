import discord
import twitterColorDetection
import datetime
from discord.ext import commands

client = commands.Bot(command_prefix='$')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    #Check if they're talking to bot
    if message.content.startswith('$'):
        #Break up the message text into an array of lowercase letters
        command = message.content.lower()
        command = command.split()
        print(command)

        #Time
        elif command[0] == "$time":
            currentDT = datetime.datetime.now()
            outTime = currentDT.strftime("%I:%M %p")
            await message.channel.send("It is " + outTime + " and OU still sucks!")

        elif command[0] == "$updateicon":
            #Check if admin
            if message.author.guild_permissions.administrator:

                #See if we are auto updating
                if command[1] == "auto":
                    command[1] = await on_updatecolor(message)

                try:
                    with open(command[1] + ".png", "rb") as image:
                        f = image.read()
                        b = bytearray(f)
                        await message.guild.edit(icon=b)
                        await message.channel.send("Icon set to " + command[1])
                #If the file isn't found, then the tower color is probably unknown
                except FileNotFoundError:
                    await message.channel.send("Error: Unknown tower color. " + 
                    "Options are white, orange, orangewhite, and dark")
                #No option was entered
                except IndexError:
                    await message.channel.send("Please enter an argument")

            else: 
                await message.channel.send("You do not have permission to do that")


async def is_admin(ctx):
    return ctx.message.author.guild_permissions.administrator

@client.command(name='hello')
async def hello(ctx):
    await ctx.send("Hello " + str(ctx.author).split('#')[0] + '!')

@client.command(name='updateicon')
@commands.check(is_admin)
async def updateicon(ctx, color):
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
    ctx.send("Texas beat OU 48 to 45 in the Red River Rivalry with a last second field goal by Dicker the Kicker! :metal:")


#Used to automatically update color
async def on_updatecolor(message):
    try:
        towerRGB = twitterColorDetection.getRGB()
        towerColor = twitterColorDetection.getColorNames(towerRGB[0], towerRGB[1])
        #Determine the correct icon
        towerColorName = towerColor[0] + towerColor[1]
        possibleColors = {
            "orangeorange": "orange",
            "whiteorange": "orangewhite",
            "whitewhite": "white",
            "darkdark": "dark"
        }
        towerColorName = possibleColors[towerColorName]

        return towerColorName


    except Exception as e:
        await message.channel.send("Error: " + str(e))


keyFile = open('keys.txt', 'r')
key = keyFile.read()
client.run(key)