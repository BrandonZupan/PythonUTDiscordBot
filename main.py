import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$updateicon'):
        with open("white.png", "rb") as image:
            f = image.read()
            b = bytearray(f)
            await message.guild.edit(icon=b)
            await message.channel.send("Icon set to white")

keyFile = open('keys.txt', 'r')
key = keyFile.read()
client.run(key)