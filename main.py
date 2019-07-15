import discord
import twitterColorDetection
from datetime import datetime
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
postsEngine = create_engine(":memory:", echo=True)
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

class posts(Base):
    __tablename__ = datetime.now().strftime("%m-%y")

    #Column for name, posts, how many mentions, how many times mentioned, how many posts in anime
    name = Column(String, primary_key=True)
    posts = Column(Integer)
    mentions = Column(Integer)
    mentioned = Column(Integer)
    animePosts = Column(Integer)

#Create the Table   
Base.metadata.create_all(engine)    #Commands
Base.metadata.create_all(postsEngine)   #Posts

#Start the SQL session
Session = sessionmaker(bind=engine)
session = Session()

PostsSession = sessionmaker(bind=postsEngine)
postsDB = PostsSession()

#Discord client
client = commands.Bot(command_prefix='$')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


############
###Checks###
############


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
    role = discord.utils.get(ctx.guild.roles, id=598292086067953664)
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


allranks = {
    'ugs': 591000675203416076, 
    'social work': 469195563267522572, 
    'nursing': 469195544154341379, 
    'natural sciences': 469195501749665797, 
    'liberal arts': 469195411098435593, 
    'geosciences': 469195394920742943, 
    'fine arts': 469195366932283394, 
    'engineering': 469195313547313162, 
    'education': 469195286728802314, 
    'communication': 469195248913088534, 
    'business': 469195224162238464, 
    'architecture': 469195103026544642, 
    'alumni': 469348087593435136, 
    'riverside': 488209904428122112, 
    'west campus': 470052478184849408, 
    'north campus': 597955125981610008, 
    'jester west': 470052452960436235, 
    'jester east': 470052427291164672, 
    'san jacinto hall': 470052381233512458, 
    'roberts hall': 470052350065901588, 
    'prather hall': 470052139943854080, 
    'moore-hill hall': 470052105558818826, 
    'creekside hall': 470052057639026708, 
    'brackenridge hall': 470052017432428546, 
    'whitis court': 470051984939155476, 
    'littlefield hall': 470051934577885194, 
    'kinsolving hall': 470051900016820237, 
    'duren hall': 470051846527123456, 
    'carothers hall': 470051813643649035, 
    'blanton hall': 470051755456200714, 
    'andrews hall': 470051617446690837, 
    'prospective students': 579365237980135425, 
    'class of 2023': 469347181409599488, 
    'class of 2022': 469347157321973761, 
    'class of 2021': 469347128368562197, 
    'class of 2020': 469347098173898762, 
    'class of 2019': 469347057560322048
}

@client.command(name='rank')
async def rank(ctx, *newRank):
    """
    Assigns a rank/role to a user, or deletes it if they already have it

    Usage: $rank <school/college>

    View all possible ranks with $ranks
    """
    if len(newRank) == 0:
        await ctx.send("Use `$rank name` to add a rank.  Use `$ranks` to list all ranks")
    else:
        newRankName = ' '.join(newRank)
        newRankName = newRankName.lower()
        #Establish guild to use
        utdiscord = client.get_guild(469153450953932800)
        utuser = discord.utils.get(utdiscord.members, id=ctx.author.id)
        try:
            newRank = discord.utils.get(utdiscord.roles, id=allranks[newRankName])
        except:
            await ctx.send(f"{newRankName} not found.  Make sure it is typed the same way as in the list of ranks found in `$ranks`")

        #Check if they already have the role.  If so, delete it.  Else add it
        if newRank in utuser.roles:
            #If so, delete it
            await utuser.remove_roles(newRank)
            await ctx.send(f'Removed rank {newRank.name} from {ctx.author.mention}')
            logging.info(f'Removed rank {newRank.name} from {ctx.author.mention}')

        else:
            #Add it since they don't got it
            await utuser.add_roles(newRank, reason="self assigned with Eyes of Texas")
            await ctx.message.add_reaction('👌')
            logging.info(f'Added rank {newRank.name} to {ctx.author.mention}')

@client.command(name='ranks')
async def ranks(ctx):
    """
    Lists all available ranks
    """
    output = ""
    #Create embed object
    embed = discord.Embed(title="Ranks", color=0xbf5700)
    #Establish guild to use
    utdiscord = client.get_guild(469153450953932800)

    #Generate output
    for role in allranks:
        discRole = discord.utils.get(utdiscord.roles, id=allranks[role])
        members = len(discRole.members)
        output += f"`{discRole.name} {members} members`\n"

    embed.add_field(name="Join with `$rank name`", value=output, inline=False)
    await ctx.send(embed=embed)


@client.command(name='usergraph', hidden=True)
@commands.check(is_admin)
async def usergraph(ctx):
    await joinChartGenerator(ctx)


@client.command(name='updateicon', hidden=True)
@commands.check(is_admin)
async def updateicon(ctx, color):
    """
    Updates the server icon
    
    Color options are orange, orangewhite, white, dark, attackmode, or auto
    """
    if color == 'auto':
        color = await on_updatecolor(ctx)
    try:
        with open("icons/" + color + ".png", "rb") as image:
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
    currentDT = datetime.now()
    outTime = currentDT.strftime("%I:%M %p")
    message = "It is " + outTime + " and OU still sucks!"
    await ctx.send(message)
    logmessage(ctx, message)


@client.command(name='hellothere')
async def hellothere(ctx):
    await ctx.author.send("General Kenobi, you are a bold one")


#Requested by John in case he ever needs help
@client.command(name='john', hidden=True)
async def john(ctx):
    """
    https://youtu.be/Ho1LgF8ys-c
    """
    return True


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


#Send a PM when someone joins
@client.event
async def on_member_join(ctx):
    newUserMessage = f"Welcome to the UT Austin Discord {ctx.mention}!  Please select which school/college you are in by using `$rank [school/college]` in the #bot-commands channel. "
    newUserMessage += "You can also select your graduating class and where you will be living.  "
    newUserMessage += "See the list of available schools/colleges, graduating classes, and communities by using `$ranks.` \n"
    newUserMessage += "If you are having problems joining a rank, please message a member with the Founder or Moderator role.  "
    newUserMessage += "Be sure to read our rules in #real-rules."
    await ctx.send(newUserMessage)
    logging.info(f"Sent join PM to {ctx.mention}")


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