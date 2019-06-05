import discord
import twitterColorDetection

client = discord.Client()

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

        #Hello: Replies hello
        if command[0] == "$hello":
            await message.channel.send('Hello!')

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

        else:
            await message.channel.send('Unknown Command')

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