import os
import discord
from discord.ext import commands
from discord.ui import button, View
from YouTubeToMP3.downloader import download
import requests
from pytube import YouTube
from threading import Thread, Event
from time import sleep

TOKEN = "NzY4ODI1NzkzOTA3MjYxNDcw.GFEgvD.cKJ2_HsuoIXr732_yTVoHp1VeB9ajO95ZHycE4"

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

timer = Event()
player_running = True
song_queue = []
song_lengths = []
voice_client = None

search_results = [ [], [], [], [], [] ]

def get_video_title(video_url):
    return YouTube(video_url).title
def get_video_length(video_url):
    return YouTube(video_url).length

async def add_song_to_queue(interaction, video_title, video_id):
    global voice_client

    message_response = ""

    await interaction.response.defer()  # Defer the response for the download

    # Join to channel if not joined
    if interaction.guild.voice_client == None:  # Check if not already connected
        if interaction.user.voice == None:  # Check if user is in a voice channel
            message_response = "You must connect to a voice channel before selecting an option."
            await interaction.followup.send(message_response)
            return False
        else:
            # Connect to the voice channel
            await interaction.user.voice.channel.connect()
            message_response = "Joined to " + interaction.user.voice.channel.name + "."

    # Set voice client
    voice_client = interaction.guild.voice_client

    # Check if mp3 file exists already
    mp3_exists = False
    files = files = os.listdir(".")
    for file in files:
        if file == video_title + ".mp3":
            mp3_exists = True

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # Download mp3 if it doesn't exist
    if not mp3_exists:
        await interaction.followup.send(message_response + f"\nDownloading {video_title}...")
        download(video_url)
    else:
        await interaction.followup.send(message_response + f"\nDownload skipped.")
    
    # Add song to the queue
    song_lengths.append(get_video_length(video_url))
    song_queue.append(video_title)
    await interaction.channel.send(f"Added {video_title} to the queue.")
    
    return True

class Select5Menu(View):
    used = False
    @discord.ui.button(label="1", style=discord.ButtonStyle.green)
    async def option1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.used:
            if await add_song_to_queue(interaction, search_results[0][0], search_results[0][1]):
                self.used = True
        else:
            await interaction.response.send_message("Search results can be used only once.")
    @discord.ui.button(label="2", style=discord.ButtonStyle.green)
    async def option2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.used:
            if await add_song_to_queue(interaction, search_results[1][0], search_results[1][1]):
                self.used = True
        else:
            await interaction.response.send_message("Search results can be used only once.")
    @discord.ui.button(label="3", style=discord.ButtonStyle.green)
    async def option3(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.used:
            if await add_song_to_queue(interaction, search_results[2][0], search_results[2][1]):
                self.used = True
        else:
            await interaction.response.send_message("Search results can be used only once.")
    @discord.ui.button(label="4", style=discord.ButtonStyle.green)
    async def option4(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.used:
            if await add_song_to_queue(interaction, search_results[3][0], search_results[3][1]):
                self.used = True
        else:
            await interaction.response.send_message("Search results can be used only once.")
    @discord.ui.button(label="5", style=discord.ButtonStyle.green)
    async def option5(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.used:
            if await add_song_to_queue(interaction, search_results[4][0], search_results[4][1]):
                self.used = True
        else:
            await interaction.response.send_message("Search results can be used only once.")


def player():
    global timer
    global voice_client

    while player_running:
        if len(song_queue) > 0: # Check if there are songs in the queue
            # Play the first song in the queue
            voice_client.play(source=discord.FFmpegPCMAudio(source=song_queue[0] + ".mp3"))

            # Wait for it to finish
            if timer.wait(timeout=song_lengths[0] + 1): # Event is set
                timer.clear()   # Clear the event to make it waitable

            # Pop the played song
            if len(song_queue) > 0: # Security check for stop functionality
                previous_song = song_queue[0]
                song_queue.pop(0)
                song_lengths.pop(0)

                if previous_song not in song_queue: # Check if previous song still in the queue
                    os.remove(previous_song + ".mp3") # Delete previous mp3 from the system

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
async def on_reaction_add(reaction, user):
    reaction

@bot.tree.command(name='join')
async def join(interaction: discord.Interaction):
    global voice_client

    if interaction.guild.voice_client:  # Check if already connected
        await interaction.response.send_message("Already connected to a voice channel.")
    else:
        if interaction.user.voice.channel:  # Check if user is in a voice channel
            await interaction.user.voice.channel.connect()
            await interaction.response.send_message("Joined to " + interaction.user.voice.channel.name + ".")
        else:
            await interaction.response.send_message("You must connect to a voice channel before using this command.")

    # Set voice client
    voice_client = interaction.guild.voice_client
    
@bot.tree.command(name='leave')
async def leave(interaction: discord.Interaction):
    global voice_client

    if interaction.guild.voice_client:  # Check if bot is inside a voice channel
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Left the channel.")
    else:
        await interaction.response.send_message("Not connected to a voice channel.")

    # Clear voice client
    voice_client = None

@bot.tree.command(name='queue')
async def queue(interaction: discord.Interaction):
    global song_queue

    if len(song_queue) == 0:
        await interaction.response.send_message("Queue is empty.")
        return

    message_response = ""

    counter = 1

    for elem in song_queue:
        message_response += str(counter) + ". " + elem + "\n"
        counter += 1

    await interaction.response.send_message("```Current queue:\n" + message_response + "```")


@bot.tree.command(name='play')
async def play(interaction: discord.Interaction, search: str):
    global voice_client
    global search_results

    message_response = ""

    await interaction.response.defer()  # Defer the response for the search

    # Get video ids
    API_URL = "https://youtube.googleapis.com/youtube/v3/"
    query = search.replace(" ", "%20")
    response = requests.get(f"{API_URL}search?q={query}&key=AIzaSyCHs90TcJXpXR-KZWYNXRLUKmBIEF0LO-8")
    video_id = response.json()["items"][0]["id"]["videoId"]
    video_id2 = response.json()["items"][1]["id"]["videoId"]
    video_id3 = response.json()["items"][2]["id"]["videoId"]
    video_id4 = response.json()["items"][3]["id"]["videoId"]
    video_id5 = response.json()["items"][4]["id"]["videoId"]

    # Get video titles
    video_title = get_video_title(f"https://www.youtube.com/watch?v={video_id}")
    video_title2 = get_video_title(f"https://www.youtube.com/watch?v={video_id2}")
    video_title3 = get_video_title(f"https://www.youtube.com/watch?v={video_id3}")
    video_title4 = get_video_title(f"https://www.youtube.com/watch?v={video_id4}")
    video_title5 = get_video_title(f"https://www.youtube.com/watch?v={video_id5}")

    # Set search results
    search_results[0] = [ video_title, video_id ]
    search_results[1] = [ video_title2, video_id2 ]
    search_results[2] = [ video_title3, video_id3 ]
    search_results[3] = [ video_title4, video_id4 ]
    search_results[4] = [ video_title5, video_id5 ]

    # Set the response
    message_response += "\n```Search results:\n"
    message_response += "1. " + video_title + "\n"
    message_response += "2. " + video_title2 + "\n"
    message_response += "3. " + video_title3 + "\n"
    message_response += "4. " + video_title4 + "\n"
    message_response += "5. " + video_title5 + "```"

    # Send the response with buttons
    await interaction.followup.send(message_response, view=Select5Menu())

@bot.tree.command(name='skip')
async def skip(interaction: discord.Interaction):
    global timer
    global song_queue

    message_response = ""

    if interaction.guild.voice_client:  # Check if bot is inside a voice channel
        if interaction.guild.voice_client.is_playing(): # Stop the player if it is playing something
            interaction.guild.voice_client.stop()
            message_response = f"Skipping {song_queue[0]}...\n"
        else:
            message_response = "Nothing to skip."
    else:
        await interaction.response.send_message("Not connected to a voice channel.")
        return

    sleep(1) # Wait for music to stop

    timer.set() # Set the event to interrupt wait

    await interaction.response.send_message(message_response)

@bot.tree.command(name='stop')
async def stop(interaction: discord.Interaction):
    global timer
    global song_queue
    global song_lengths

    message_response = ""

    song_queue = []
    song_lengths = []

    if interaction.guild.voice_client:  # Check if bot is inside a voice channel
        if interaction.guild.voice_client.is_playing(): # Stop the player if it is playing something
            interaction.guild.voice_client.stop()
            message_response = "Stopped the player.\n"
        await interaction.guild.voice_client.disconnect()   # Disconnect
        message_response += "Left the channel."
    else:
        message_response = "Not connected to a voice channel."

    # Delete all mp3 files
    files = os.listdir(".")
    for file in files:
        if file.endswith(".mp3"):
            os.remove(file)

    timer.set() # Set the event to interrupt wait

    await interaction.response.send_message(message_response)

playerThread = Thread(target=player)
playerThread.start()

bot.run(TOKEN)

player_running = False

playerThread.join()
