import discord
from discord.ext import commands
import os
import json
import time

def load_json(file: str):
    if file == "config":
        with open('config.json') as f:
            config = json.load(f)
            print("Config Loaded!")
        return config

config = load_json("config")
TOKEN = config["TOKEN"]

# Bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=config["PREFIX"], intents=intents)

bot.start_time = time.time()  # Track uptime

@bot.event
async def on_ready():
    print("------------------------------------")
    print(f"Project: {config['name']}")
    print(f"Bot Name: {bot.user.name}")
    print(f"Bot version: {config['version']}")
    print(f"Discord.py Version: {discord.__version__}")
    print(f"Bot created by {config['author']}")
    print(f"special thanks to our contributors: {', '.join(config['contributors'])}")
    print("------------------------------------")
    await bot.change_presence(activity=discord.Game(name='Discord Ranked'))
    await bot.tree.sync()
    print("Commands synced!")


# Load all cogs dynamically
async def load_cogs():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def setup_hook():
    await load_cogs()

# Run bot using the token from config.json
bot.run(TOKEN)