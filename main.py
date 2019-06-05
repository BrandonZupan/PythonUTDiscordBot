import discord

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

        if command[0] == "$updateicon":
            with open("white.png", "rb") as image:
                f = image.read()
                b = bytearray(f)
                await message.guild.edit(icon=b)
                await message.channel.send("Icon set to white")

keyFile = open('keys.txt', 'r')
key = keyFile.read()
client.run(key)