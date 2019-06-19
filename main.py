import discord
import twitterColorDetection
import datetime
from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#SQL Database
engine = create_engine('sqlite:///responces.db', echo=True)
Base = declarative_base()

class ccCommand(Base):
    __tablename__ = "imageCommands"
    
    #Has a column for the ID, name, and responce
    #id = Column(Integer, primary_key=True)
    name = Column(String, primary_key=True)
    responce = Column(String)

#Create the Table   
Base.metadata.create_all(engine)

#Start the SQL session
Session = sessionmaker(bind=engine)
session = Session()

#Discord client
client = commands.Bot(command_prefix='$')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

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
        commandList = str()
        for instance in session.query(ccCommand).order_by(ccCommand.name):
            commandList += instance.name + ' '
        await ctx.send(commandList)

    #If one argument, delete that command
    if len(args) == 1:
        print(args[0])
        victim = session.query(ccCommand).filter_by(name=args[0]).one()
        print(victim.responce)
        session.delete(victim)
        session.commit()
        await ctx.message.add_reaction('👌')

    #If 2 or more arguments, combine them and modify database
    if len(args) >= 2:
        #newCC = ccCommand(args[0], ' '.join(args[1:]))
        #await ctx.send("Command " + newCC.name + " with link " + newCC.responce)
        newCC = ccCommand(name=args[0], responce=' '.join(args[1:]))
        session.merge(newCC)
        session.commit()
        #await ctx.send("Command " + newCC.name + " with link " + newCC.responce)
        await ctx.message.add_reaction('👌')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        #await ctx.send(ctx.message.content)
        command = ctx.message.content.lower()
        command = command.split(" ", 1)

        #Look if its in the database
        for instance in session.query(ccCommand).order_by(ccCommand.name):
            if instance.name == command[0][1:]:
                await ctx.send(instance.responce)
                return
    else:
        print(error)

"""
#Look if command is in the database
@client.event
async def on_message(message):

    if message.author == client.user:
        return
    
    #Check if they're talking to bot
    if message.content.startswith('$'):
        command = message.content.lower()
        command = command.split(" ", 1)

        #Look if its in the database
        for instance in session.query(ccCommand).order_by(ccCommand.id):
            if instance.name == command[0]:
                await message.channel.send(instance.responce)
                return
"""

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