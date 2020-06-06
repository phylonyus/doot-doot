import discord
import random
import asyncio
import os
import sys
import subprocess
import re
import json
import requests
from pathlib import Path

from discord.ext import commands

def getConfig(path):
    configFile = open(path, "r")
    return json.loads(configFile.read())


config = getConfig("config.json")

sounds_path = config['sounds_path']
sub_cmd_sep = config['sub_cmd_sep']

voice_channel = None

def isLoud(savepath):
    cmd = 'ffmpeg -i'+ savepath + ' -filter:a volumedetect -f null /dev/null 2>&1 | grep -oP \'mean_volume: \\K.([0-9]?\\d+(\\.\\d+))\''
    out = subprocess.getoutput(cmd)
    num = float(out.split()[0])
    if num >= -6.0:
        return True
    else:
        return False

############################################################### Define class for pretty printing
class DisplayablePath(object):
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0
 
    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))

###############################################################

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

def getAliasInfo():
    alias_dict = {}
    category_list = []
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
                category_list.append(cmd)
                with os.scandir(entry.path) as it2:
                    for sub_entry in it2:
                        sub_cmd = str(sub_entry.name.split('.')[0])
                        sub_path = sub_entry.path
                        full_cmd = cmd + sub_cmd_sep + sub_cmd
                        # print(full_cmd + " " + sub_path)
                        alias_dict[full_cmd] = sub_path
                        alias_dict[cmd].append(sub_path)
    return alias_dict, category_list

def restart_bot():
    os.system('. /home/robbiechatbot/doot-doot/DootRestart.sh')

alias_dict, category_list = getAliasInfo()
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
    async def sounds(self, ctx):
        """View a list of categories and their sounds"""
        user = ctx.message.author
        paths = DisplayablePath.make_tree(Path(sounds_path))
        msg_limit = 2000
        size = 0
        message = []
        msg = "```"
        for path in paths:
            message.append(path.displayable())
        #print(len(message))
        for i in range(0, len(message)):
            block = message[i]
            #print(block)
            if size+(len(block)+4) <= msg_limit:
                msg+=('\n'+block)
                #print('a')
                size += len(block)+4
                if i == len(message)-1:
                    msg+="""```"""
                    await user.send(msg)
                #print(size)
            elif size+len(block) > msg_limit:
                msg+="""```"""
                await user.send(msg)
                #print(len(msg))
                msg="```"
                size=0

    @commands.command()
    @commands.guild_only()
    async def check_aliases(self, ctx):
        await ctx.send("current aliases:")
        msg_limit = 2000
        aliases_str = str(aliases)
        for i in range(0, len(aliases_str), msg_limit):
            message = aliases_str[i:i+msg_limit]
            await ctx.send(message)

    @commands.command()
    @commands.guild_only()
    async def check_cats(self, ctx):
        await ctx.send("current categories:")
        msg_limit = 2000
        cats_str = str(category_list)
        for i in range(0, len(cats_str), msg_limit):
            message = cats_str[i:i+msg_limit]
            await ctx.send(message)
    

    @commands.command()
    @commands.guild_only()
    async def restart(self, ctx):
        restart_bot()
        await ctx.send('ok, tried to restart myself')

    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        if voice_channel != None and voice_channel.is_playing():
            voice_channel.stop()
            await voice_channel.disconnect()

    @commands.command()
    @commands.guild_only()
    async def add(self, ctx):
        '''command will be filename w/o file extension. You can add to group like: 'add wow'''
        command = ctx.message.content.split(config['prefix'])[1]
        attachment = ctx.message.attachments[0]
        url = attachment.url
        filename = attachment.filename
        if len(command.split(sub_cmd_sep)) == 2:
            group = command.split(sub_cmd_sep)[1]
        else:
            group = ''
        save_dir = os.path.join(sounds_path, group)
        save_path = os.path.join(save_dir, filename)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        downloaded_file = requests.get(url)
        open(save_path, 'wb').write(downloaded_file.content)
        if isLoud(save_path):
            os.remove(save_path)
            await ctx.send("""
```
ERROR: fUnNy bEcAuSe LoUd. Sound too loud, please choose a different file
```
""")
        else:
            await ctx.send(f'added {filename}, restarting')
            restart_bot()

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
