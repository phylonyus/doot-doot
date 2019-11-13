import discord
import random
import asyncio
import os
import re
from discord.ext import commands


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
    random_chance = random.randint(1, 100)
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
#maximum doot

    #await ctx.send(":thumbsup: played the effect!")
    while voice_channel.is_playing():
        await asyncio.sleep(1)

    voice_channel.stop()

    await voice_channel.disconnect()

def getSoundFiles():
	f = []
	dirs = os.listdir("sounds/")
	for file in dirs:
		f.append(file)
	return f



# Beginning of commands
class Airhorn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def wow(self, ctx):
        """Says wow."""
        filename = random.choice(os.listdir("sounds/wow"))
        await play_file(ctx, "sounds/wow/" + filename)

    @commands.command()
    @commands.guild_only()
    async def doot(self, ctx):
        """Doots the horn."""
        await play_file(ctx, "sounds/airhorn.mp3")

    @commands.command()
    @commands.guild_only()
    async def bazinga(self, ctx):
        """BAZINGA!"""
        await play_file(ctx, "sounds/bazinga.mp3")

    @commands.command()
    @commands.guild_only()
    async def justdoit(self, ctx):
        """Tells you to just do it."""
        await play_file(ctx, "sounds/justdoit.mp3")

    @commands.command()
    @commands.guild_only()
    async def clap(self, ctx):
        """..you did good. Here are some claps."""
        await play_file(ctx, "sounds/clap.mp3")

    @commands.command()
    @commands.guild_only()
    async def oof(self, ctx):
        """Roblox oof."""
        await play_file(ctx, "sounds/oof.mp3")

    @commands.command()
    @commands.guild_only()
    async def nope(self, ctx):
        """Nope."""
        await play_file(ctx, "sounds/nope.mp3")

    @commands.command()
    @commands.guild_only()
    async def suspense(self, ctx):
        """Sudden suspense."""
        await play_file(ctx, "sounds/suddensus.mp3")

    @commands.command()
    @commands.guild_only()
    async def sad(self, ctx):
        """The saddest music you've ever heard."""
        await play_file(ctx, "sounds/sadmusic.mp3")

    @commands.command()
    @commands.guild_only()
    async def fail(self, ctx):
        """Wow.. you failed pretty bad tbh."""
        await play_file(ctx, "sounds/fail.mp3")

    @commands.command()
    @commands.guild_only()
    async def gay(self, ctx):
        """HA Gay sound effect"""
        await play_file(ctx, "sounds/hagay.mp3")

    @commands.command()
    @commands.guild_only()
    async def no(self, ctx):
        """No."""
        await play_file(ctx, "sounds/no.mp3")

    @commands.command()
    @commands.guild_only()
    async def godno(self, ctx):
        """No.. GOD. NO."""
        await play_file(ctx, "sounds/godno.mp3")

    @commands.command()
    @commands.guild_only()
    async def dootstorm(self, ctx):
        """What song is this? Ah, it's Darude - Dootstorm."""
        await play_file(ctx, "sounds/dootstorm.mp3")

    @commands.command()
    @commands.guild_only()
    async def WTF(self, ctx):
        """Bitch... what the fuck?"""
        await play_file(ctx, "sounds/WTF.mp3")

    @commands.command()
    @commands.guild_only()
    async def fuckedup(self, ctx):
        """it was at this moment he knew.. he fucked up."""
        await play_file(ctx, "sounds/fuckedup.mp3")

    @commands.command()
    @commands.guild_only()
    async def ohno(self, ctx):
        """oh no no no."""
        await play_file(ctx, "sounds/ohno.mp3")

    @commands.command()
    @commands.guild_only()
    async def ohhh(self, ctx):
        """ohhhhhhh."""
        await play_file(ctx, "sounds/ohhh.mp3")

    @commands.command()
    @commands.guild_only()
    async def thuglife(self, ctx):
        """So you think you are living the thug life?"""
        await play_file(ctx, "sounds/thuglife.mp3")

    @commands.command()
    @commands.guild_only()
    async def horn(self, ctx):
        """DJ horn."""
        await play_file(ctx, "sounds/djhorn.mp3")

    @commands.command()
    @commands.guild_only()
    async def phintro(self, ctx):
        """Sound Effect from intro of popular xxx website (no actuall 18+ content present)"""
        await play_file(ctx, "sounds/phintro.mp3")

    @commands.command()
    @commands.guild_only()
    async def memereview(self, ctx):
        """👏meme👏review"""
        await play_file(ctx, "sounds/meme-review.mp3")

    @commands.command()
    @commands.guild_only()
    async def spongebob(self, ctx):
        """this IS whole intro song from Spongebob, play at your discretion"""
        await play_file(ctx, "sounds/spongebob.mp3")

    @commands.command()
    @commands.guild_only()
    async def mariocoin(self, ctx):
        """Ding!"""
        await play_file(ctx, "sounds/mario_coin.mp3")

    @commands.command()
    @commands.guild_only()
    async def honk(self, ctx):
        """Honk Honk!"""
        await play_file(ctx, "sounds/honk.mp3")


def setup(bot):
    bot.add_cog(Airhorn(bot))
