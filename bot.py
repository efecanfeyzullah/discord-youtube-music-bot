import discord
from discord import app_commands
from discord.ext import commands

TOKEN = "NzY4ODI1NzkzOTA3MjYxNDcw.GFEgvD.cKJ2_HsuoIXr732_yTVoHp1VeB9ajO95ZHycE4"

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

    guild_count = 0

    for guild in bot.guilds:
        print(f"Guild ID: {guild.id}, Guild Name: {guild.name}")
        guild_count = guild_count + 1

    print("Mercarb Mekani is in " + str(guild_count) + " guilds.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    return

    response = "Annen"
    await message.channel.send(response)

@bot.tree.command(name='join')
async def join(interaction: discord.Interaction):
    if interaction.guild.voice_client:  # Check if already connected
        await interaction.response.send_message("Already connected to a voice channel.")
    else:
        if interaction.user.voice.channel:  # Check if user is in a voice channel
            await interaction.user.voice.channel.connect()
            await interaction.response.send_message("Joined to " + interaction.user.voice.channel.name + ".")
        else:
            await interaction.response.send_message("You must connect to a voice channel before using this command.")
    
@bot.tree.command(name='leave')
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:  # Check if bot is inside a voice channel
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Left the channel.")
    else:
        await interaction.response.send_message("Not connected to a channel.")

@bot.tree.command(name='play')
async def play(interaction: discord.Interaction, name: str):
    message_response = ""

    # Join to channel if not joined
    if interaction.guild.voice_client == None:  # Check if not already connected
        if interaction.user.voice.channel:  # Check if user is in a voice channel
            await interaction.user.voice.channel.connect()
            message_response = "Joined to " + interaction.user.voice.channel.name + "."
        else:
            message_response = "You must connect to a voice channel before using this command."
            return
    
    # Play mp3
    interaction.guild.voice_client.play(source=discord.FFmpegPCMAudio(source=name))
    await interaction.response.send_message(message_response + "\nPlaying...")

bot.run(TOKEN)