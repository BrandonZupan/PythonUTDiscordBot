import discord
import twitterColorDetection
import datetime
from discord.ext import commands
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from joinGraph import joinChartGenerator

#Start logging
logging.basicConfig(level=logging.INFO)

#SQL Database
engine = create_engine('sqlite:///responces.db', echo=False)
Base = declarative_base()

#Nitro Database, must be approved into SQL
global nitroCommands
nitroCommands = {}

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

async def in_secretChannel(ctx):
    """Checks if a command was used in a secret channel"""
    secretChannels = {
        'ece-torture-dungeon': 508350921403662338,
        'nitro-commands': 591363307487625227
    }
    usedChannel = ctx.channel.id
    for channel in secretChannels:
        if secretChannels[channel] == usedChannel:
            return True

    #It dont exist
    return False

async def is_nitro(ctx):
    """Checks if a user has Discord Nitro"""
    #Fake Nitro
    role = discord.utils.get(ctx.guild.roles, id=591362960232808452)
    if role in ctx.author.roles:
        return True
    #Real Nitro on test server
    role = discord.utils.get(ctx.guild.roles, id=42)
    if role in ctx.author.roles:
        return True
    else:
        return False

##############
###Commands###
##############

@client.command(name='hello')
async def hello(ctx):
    message = "Hello " + str(ctx.author).split('#')[0] + '!'
    await ctx.send(message)
    logmessage(ctx, message)

@client.command(name='usergraph', hidden=True)
@commands.check(is_admin)
async def usergraph(ctx):
    await joinChartGenerator(ctx)

@client.command(name='updateicon', hidden=True)
@commands.check(is_admin)
async def updateicon(ctx, color):
    """
    Updates the server icon
    
    Color options are orange, orangewhite, white, dark, or auto
    """
    if color == 'auto':
        color = await on_updatecolor(ctx)
    try:
        with open(color + ".png", "rb") as image:
            f = image.read()
            b = bytearray(f)
            await ctx.guild.edit(icon=b)
            await ctx.channel.send("Icon set to " + color)
            logging.info("Icon set to " + color + " by " + ctx.author.name)
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
    message = "It is " + outTime + " and OU still sucks!"
    await ctx.send(message)
    logmessage(ctx, message)

@client.command(name='modifycommand')
@commands.check(is_nitro)
@commands.check(in_secretChannel)
async def modifycommand(ctx, *args):
    """
    Nitro command for modifying the command database

    List commands: $modiftycommand
    Modify or create a command: $modifycommand <command_name> <responce>

    Action must be confirmed by a moderator with $approve <command_name>
    """

    #If zero arguments, list all commands
    if len(args) == 0:
        commandList = str()
        for instance in session.query(ccCommand).order_by(ccCommand.name):
            commandList += instance.name + ' '
        await ctx.send(commandList)

    #If 2 or more arguments, combine them and modify database
    if len(args) >= 2:
        #Add to nitro database
        nitroCommands[args[0]] = ' '.join(args[1:])
        await ctx.send("Recieved, please wait for moderator to confirm it")

@client.command(name='pending', hidden=True)
@commands.check(is_admin)
@commands.check(in_secretChannel)
async def pending(ctx):
    """
    List pending commands sent by nitro users

    List pending: $pending
    Approve a command: $approve <command_name>
    Deny a command: $deny <command_name>
    """
    message = ""

    #Check if there's pending commands, if so list them
    if len(nitroCommands) >= 1:
        for command in nitroCommands:
            message += command + ": '" + nitroCommands[command] + "' "
    
    else:
        message = "No pending commands"
    await ctx.send(message)

@client.command(name='approve', hidden=True)
@commands.check(is_admin)
@commands.check(in_secretChannel)
async def approve(ctx, command):
    """
    Approve a command added by a nitro user

    List pending: $pending
    Approve a command: $approve <command_name>
    Deny a command: $deny <command_name>
    """

    if command in nitroCommands.keys():
        #Add it to the database
        newCC = ccCommand(name=command, responce=nitroCommands[command])
        session.merge(newCC)
        session.commit()
        #Remove from dict
        del nitroCommands[command]
        await ctx.message.add_reaction('👌')
        logging.info(ctx.author.name + " added " + newCC.name + " with responce " + newCC.responce)
    #Command not in dict
    else:
        await ctx.send("Error: Command not in queue")

@client.command(name='deny', hidden=True)
@commands.check(is_admin)
@commands.check(in_secretChannel)
async def deny(ctx, command):
    """
    Deny a command added by a nitro user

    List pending: $pending
    Approve a command: $approve <command_name>
    Deny a command: $deny <command_name>
    """
    if command in nitroCommands.keys():
        #Remove from dict
        del nitroCommands[command]
        await ctx.message.add_reaction('👌')
    #Command not in dict
    else:
        await ctx.send("Error: Command not in queue")


@client.command(name='cc', hidden=True)
@commands.check(is_admin)
@commands.check(in_secretChannel)
async def cc(ctx, *args):
    """
    Modifies the command database

    List commands: $cc
    Modify or create a command: $cc <command_name> <responce>
    Delete a command: $cc <command_name>

    Bot will confirm with :ok_hand:
    """
    #If zero arguments, list all commands
    if len(args) == 0:
        commandList = str()
        for instance in session.query(ccCommand).order_by(ccCommand.name):
            commandList += instance.name + ' '
        await ctx.send(commandList)

    #If one argument, delete that command
    if len(args) == 1:
        victim = session.query(ccCommand).filter_by(name=args[0]).one()
        session.delete(victim)
        session.commit()
        await ctx.message.add_reaction('👌')
        logging.info(ctx.author.name + " deleted " + victim.name)

    #If 2 or more arguments, combine them and modify database
    if len(args) >= 2:
        #newCC = ccCommand(args[0], ' '.join(args[1:]))
        #await ctx.send("Command " + newCC.name + " with link " + newCC.responce)
        newCC = ccCommand(name=args[0], responce=' '.join(args[1:]))
        session.merge(newCC)
        session.commit()
        #await ctx.send("Command " + newCC.name + " with link " + newCC.responce)
        await ctx.message.add_reaction('👌')
        logging.info(ctx.author.name + " added " + newCC.name + " with responce " + newCC.responce)

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

#Add reactions to messages in suggestions to allow voting
@client.event
async def on_message(ctx):
    #Check if it was sent to suggestions
    if ctx.channel.id == 469191877489459220:
        #reactions = ['thumbsup', 'thumbsdown', 'shrug']
        await ctx.add_reaction('👍')
        await ctx.add_reaction('👎')
        await ctx.add_reaction('🤷')
        return
    #Add an ickycat to anime
    if ctx.channel.id == 565561419769315328:
        #ickycat = discord.Emoji()
        #ickycat.name='ickycat'
        await ctx.add_reaction('<:ickycat:576983438385741836>')
        return
    await client.process_commands(ctx)


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

#Logs a message that is sent
def logmessage(ctx, message):
    logging.info("Sent message '" + message + "' to " + ctx.channel.name)


keyFile = open('keys.txt', 'r')
key = keyFile.read()
client.run(key)