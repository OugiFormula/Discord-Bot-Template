import discord
from discord import app_commands
from discord.ext import commands
import time, json
from datetime import datetime, timezone

def load_json(file: str):
    if file == "config":
        try:
            with open('config.json', encoding='utf-8') as f:
                data = json.load(f)
                print("config Loaded in utilities!")
            return data
        except FileNotFoundError:
            print("Error: config.json not found!")
            return {}  # Return an empty dictionary to prevent crashes
        except json.JSONDecodeError:
            print("Error: config.json is not formatted correctly!")
            return {}

# Load JSON at startup
config = load_json("config")

class UtilitiesCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = time.time()

    @app_commands.command(name="patchnotes", description="allow the bot owner to send bot patch notes")
    async def patchnotes(self, interaction: discord.Interaction, notes: str):
        #input the ID of the bot-update channel
        try:
            channel = self.bot.get_channel(config["bot_update_channel_id"])
        except Exception as e:
            print(f"Error: {e}")
            await interaction.response.send_message("Error: I can't find the bot-update channel!", ephemeral=True)
            return
        #check if the user id is mine
        if interaction.user.id == config["bot_owner_id"]:
            #split the notes using \n
            note_list = notes.split("\\n")
            fields = []
            current_field = ""
            for note in note_list:
                if len(current_field) + len(note) + 2 > 1024:
                    fields.append(current_field)
                    current_field = note
                else:
                    current_field += f"\n- {note}" if current_field else f"- {note}"
            fields.append(current_field) #add the last field

            #create embed template for the patch notes
            embed = discord.Embed(
                title=f"{config["name"]} Patch Notes - Version {config["version"]}",
                description="new version yay!",
                colour=0x00b0f4,
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_footer(text=f"{config["name"]} - Patch notes")

            #add fields to the embed
            for i, field in enumerate(fields,1):
                embed.add_field(name=f"so what's new?", value=field, inline=False)
            #send the embed to the bot-update channel
            await channel.send(embed=embed)
            #send a confirmation message to the user
            await interaction.response.send_message("✅ Patch notes sent successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("you're not allowed to use this command! (if you're the bot owner add your id in config.json)", ephemeral=True)  # Prevents multiple response issues

    #show information about the bot
    @app_commands.command(name="about", description=f"Displays information about {config["name"]}, including uptime and ping.")
    async def about(self,interaction: discord.Interaction):
        cog = interaction.client.get_cog("UtilitiesCommands") or []
        uptime = time.time() - cog.bot.start_time
        uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime))
        ping = round(cog.bot.latency * 1000)

        embed = discord.Embed(title=config["name"], description={config["description"]}, color=discord.Color.blue())
        embed.add_field(name="Version", value=config["version"])
        embed.add_field(name="Created By", value=config["author"])
        embed.add_field(name="Contributors", value=', '.join(config['contributors']))
        embed.add_field(name="Library", value=f"discord.py version {discord.__version__}")
        embed.add_field(name="Total Servers", value=len(cog.bot.guilds))
        embed.add_field(name="Uptime", value=uptime_str)
        embed.add_field(name="Ping", value=f"{ping}ms")
        embed.set_footer(text="bot template provided by YukioKoito")
        if config["img_url"] != None:
            embed.set_thumbnail(url=config["img_url"])
        await interaction.response.send_message(embed=embed)

    #dynamic add commands to a list and display them to the user.
    @app_commands.command(name="help", description="Shows all available commands or details about a specific command.")
    async def help(self, interaction: discord.Interaction, command_name: str = None):
        if command_name:
            command = self.bot.tree.get_command(command_name)
            if not command:
                await interaction.response.send_message("Command not found.", ephemeral=True)
                return
            
            embed = discord.Embed(title=f"/{command.name}", description=command.description, color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="Help Menu", description="List of available commands:", color=discord.Color.blue())
            
            command_dict = {}
            for command in self.bot.tree.walk_commands():
                if command.module not in command_dict:
                    command_dict[command.module] = []
                command_dict[command.module].append(command)
            
            for cog, commands in command_dict.items():
                command_list = "\n".join([f"`/{cmd.name}` - {cmd.description}" for cmd in commands])
                embed.add_field(name=cog.replace("cogs.", ""), value=command_list, inline=False)

            await interaction.response.send_message(embed=embed)
            #await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UtilitiesCommands(bot))
