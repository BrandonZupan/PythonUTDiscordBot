import discord
from discord.ext import commands

client = commands.Bot(command_prefix='$')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

"""
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

        #Hello: Replies hello
        if command[0] == "$hello":
            await message.channel.send('Hello!')

        elif command[0] == "$updateicon":
            #Check if admin
            if message.author.guild_permissions.administrator:

                try:
                    with open(command[1] + ".png", "rb") as image:
                        f = image.read()
                        b = bytearray(f)
                        await message.guild.edit(icon=b)
                        await message.channel.send("Icon set to " + command[1])
                #If the file isn't found, then the tower color is probably unknown
                except FileNotFoundError:
                    await message.channel.send("Error: Unknown tower color.  Options are white, orange, orangewhite, and dark")
                #No option was entered
                except IndexError:
                    await message.channel.send("Please enter an argument")

            else: 
                await message.channel.send("You do not have permission to do that")
"""

@client.command()
async def hello(ctx):
    await ctx.send("Hello " + str(ctx.author).split('#')[0] + '!')


keyFile = open('keys.txt', 'r')
key = keyFile.read()
client.run(key)