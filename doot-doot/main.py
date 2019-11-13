# Setting up configuration
import json
import traceback
import utils

from datetime import datetime

import discord
from discord.ext.commands import Bot

from utils import Logger

def getConfig(path):
    configFile = open(path, "r")
    return json.loads(configFile.read())


config = getConfig("config.json")

# Preparing the cogs
initial_extensions = [
    'Airhorn',
    'Basics',
    'Fun'
]

# Prefix, description that appear in !help
client = Bot(
    description="dooting on the haters | The Soundboard | 1 in 100 chance to be rickrolled for free when using bot!",
    command_prefix=config['prefix'], pm_help=False)

# Loading special extension for Eval
client.load_extension('jishaku')

# Initialization of bot and logging in
@client.event
async def on_ready():
    # We setup the logger first
    Logger.setup_logger()

    await Logger.log("Bot startup done!", client, "INFO",
                     f'Logged in as {client.user.name} (ID: {client.user.id}) | Connected to {len(client.guilds)} '
                     f'servers with a total of {len(client.users)} users')
    await client.change_presence(activity=discord.Game(
        name='Doot Doot Motherfucker | Prefix is ' + config['prefix'] + ' | List of commands under ' + config[
            'prefix'] + 'help'))


@client.event
async def on_guild_join(guild):
    logs_channel = config['log_channel']
    guild_id = str(guild.id)
    owner_id = str(guild.owner)
    owner_name = str(guild.owner.name)
    guild_name = str(guild.name)
    channel = client.get_channel(logs_channel)
    embed = discord.Embed(title="Bot was added to new server", colour=discord.Colour(0x1738d4),
                          description="DootDoot was added to new server\n" + guild_id + "\nOwned by " + owner_name +
                                      "(`" + owner_id + "`)\nGuild name: " + guild_name,
                          timestamp=datetime.utcnow())
    embed.set_thumbnail(url="https://cdn.onlinewebfonts.com/svg/img_145486.png")

    await channel.send(embed=embed)
    Logger.logDebug("Bot was added to a new server mannn!", "INFO")


@client.event
async def on_guild_remove(guild):
    ch = client.get_channel(config['log_channel'])
    embed = discord.Embed(title="Bot left server", colour=discord.Colour(0x1738d4),
                          description="DootDoot was removed from a server\n{} ({})\n"
                                      "Owned by {} ({})".format(guild.name, guild.id, str(guild.owner),
                                                                guild.owner.id),
                          timestamp=datetime.utcnow())
    embed.set_thumbnail(url="https://cdn1.iconfinder.com/data/icons/interface-elements-ii-1/512/Logout-512.png")
    await ch.send(embed=embed)
    Logger.logDebug("Bot was removed from a server!", "INFO")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith(config['prefix']):
        command = message.content.split(config['prefix'], maxsplit=1)[-1].split(maxsplit=1)[0]
        if isinstance(message.channel, discord.DMChannel):
            wheremessage = f"in the DM channel with the ID {message.channel.id}"
        elif message.guild is not None:
            wheremessage = f"in the server {message.guild.name} (`{message.guild.id}`) in the channel " \
                           f"#{message.channel.name} (`{message.channel.id}`)"
        await Logger.log(f"{message.author.name} (`{message.author.id}`) just used {command} command, "
                         f"{wheremessage}!", client, "INFO")
        await client.process_commands(message)


# Adding the cogs to the bot
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            client.load_extension("cogs." + extension)
        except Exception as e:
            Logger.log(f"Error occurred while loading cog {extension} - Error: {e}", client, "ERROR")
            print(traceback.format_exc())

client.run(config['token'])
