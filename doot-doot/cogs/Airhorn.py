import discord
import random
import asyncio
import os
import re
import json
import requests
from discord.ext import commands

def getConfig(path):
    configFile = open(path, "r")
    return json.loads(configFile.read())


config = getConfig("config.json")

sounds_path = config['sounds_path']
sub_cmd_sep = config['sub_cmd_sep']

# defining function to handle playing sounds in Voice Channel
async def play_file(ctx, filename):
    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel.")
        return

    voice_channel = ctx.author.voice.channel
    print(f'{str(ctx.author)} is in {voice_channel}')
    try:
        voice_channel = await voice_channel.connect()

    # catching most common errors that can occur while playing effects
    except discord.Forbidden:
        await ctx.send(
            "Command raised error \"403 Forbidden\". Please check if bot has permission to join and speak in voice "
            "channel")
        return
    except TimeoutError:
        await ctx.send(
            "There was an error while joining channel (Timeout). It's possible that either Discord API or bot host "
            "has latency/connection issues. Please try again later if issues will continue contact bot owner.")
        return
    except discord.ClientException:
        await ctx.send("I am already playing a sound! Please wait to the current sound is done playing!")
        return
    except Exception as e:
        await ctx.send(
            "There was an error processing your request. Please try again. If issues will continue contact bot owner.")
        print(f'Error trying to join a voicechannel: {e}')
        return

    # There is a 1 in 100th chance that it
    # will do a rickroll instead of the desired sound
    random_chance = random.randint(1, 500)
    if random_chance == 1:
        source = discord.FFmpegPCMAudio("sounds/rickroll.mp3")
    else:
        try:
            source = discord.FFmpegPCMAudio(filename)

        # edge case: missing file error
        except FileNotFoundError:
            await ctx.send(
                "There was an issue with playing sound: File Not Found. Its possible that host of bot forgot to copy "
                "over a file. If this error occured on official bot please use D.github to report issue.")
    try:
        voice_channel.play(source, after=lambda: print("played doot"))
    # catching most common errors that can occur while playing effects
    except discord.Forbidden:
        await ctx.send("There was issue playing a sound effect. please check if bot has speak permission")
        await voice_channel.disconnect()
        return
    except TimeoutError:
        await ctx.send(
            "There was a error while attempting to play the sound effect (Timeout) its possible that either discord "
            "API or bot host has latency or network issues. Please try again later, if issues will continue contact "
            "bot owner")
        await voice_channel.disconnect()
        return
    except Exception as e:
        await ctx.send(
            "There was an issue playing the sound. Please try again later. If issues will continue contact bot owner.")
        await voice_channel.disconnect()
        print(f'Error trying to play a sound: {e}')
        return

    #await ctx.send(":thumbsup: played the effect!")
    while voice_channel.is_playing():
        await asyncio.sleep(1)

    voice_channel.stop()

    await voice_channel.disconnect()

def getAliasDict():
	alias_dict = {}
	with os.scandir(sounds_path) as it:
		for entry in it:
			cmd = str(entry.name)
			path = entry.path
			if entry.is_file():
				cmd = cmd.split('.')[0]
				# print(cmd + " " + path)
				alias_dict[cmd] = path
			if entry.is_dir():
				alias_dict[cmd] = []
				with os.scandir(entry.path) as it2:
					for sub_entry in it2:
						sub_cmd = str(sub_entry.name.split('.')[0])
						sub_path = sub_entry.path
						full_cmd = cmd + sub_cmd_sep + sub_cmd
						# print(full_cmd + " " + sub_path)
						alias_dict[full_cmd] = sub_path
						alias_dict[cmd].append(sub_path)
	return alias_dict

alias_dict = getAliasDict()
aliases = list(alias_dict.keys())

# Beginning of commands
class Airhorn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=aliases)
    @commands.guild_only()
    async def master_command(self, ctx):
        """Handles all commands in a sketchy custom way"""
        command = ctx.message.content.split(config['prefix'])[1]
        alias_entry = alias_dict[command]
        if isinstance(alias_entry, list):
            file_path = random.choice(alias_entry)
        else:
            file_path = alias_entry
        await play_file(ctx, file_path)

    @commands.command()
    @commands.guild_only()
    async def check_aliases(self, ctx):
        await ctx.send("current aliases:")
        await ctx.send(str(aliases))
        # await ctx.send(str(alias_dict)[:2000])

    @commands.command()
    @commands.guild_only()
    async def restart(self, ctx):
        os.system('. /home/robbiechatbot/doot-doot/DootRestart.sh')
        await ctx.send('ok, tried to restart myself')

    @commands.command()
    @commands.guild_only()
    async def add(self, ctx):
        '''use like: 'add wow  to add file to wow group, otherwise adds file as base sound'''
        command = ctx.message.content.split(config['prefix'])[1]
        attachment = ctx.message.attachments[0]
        url = attachment.url
        filename = attachment.filename
        if len(command.split(sub_cmd_sep)) == 2:
            group = command.split(sub_cmd_sep)[1]
        else:
            group = ''
        save_path = os.path.join(sounds_path, group, filename)
        downloaded_file = requests.get(url)
        open(save_path, 'wb').write(downloaded_file.content)
        await ctx.send(f'added {filename}')
        self.restart()

    #TODO handle these aliases we still want
    # @commands.command(aliases=['planes','airplane','boeing','airbus'])
    # @commands.guild_only()
    # async def aviation(self, ctx):
    #     """Aviation Related Sounds"""
    #     filename = random.choice(os.listdir("sounds/aviation"))
    #     await play_file(ctx, "sounds/aviation/" + filename)

    # @commands.command(aliases=['420','bong','bongrip'])
    # @commands.guild_only()
    # async def weed(self, ctx):
    #     """Bong Rips"""
    #     filename = random.choice(os.listdir("sounds/420"))
    #     await play_file(ctx, "sounds/420/" + filename)


def setup(bot):
    bot.add_cog(Airhorn(bot))
