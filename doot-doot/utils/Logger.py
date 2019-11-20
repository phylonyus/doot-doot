import datetime
import json
import discord
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler


def getConfig(path):
    configFile = open(path, "r")
    return json.loads(configFile.read())


config = getConfig("config.json")


# Logger from Fido2603's noDoot (https://github.com/Fido2603/noDoot/blob/master/utilities/logger.py)
def setup_logger():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%H:%M:%S')

    handler = TimedRotatingFileHandler("logs/doot-doot.log", when="midnight", interval=1, encoding="UTF-8")
    handler.suffix = "%Y%m%d"
    handler.setFormatter(formatter)

    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)

    logger = logging.getLogger("doot-doot")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)  # CAN BE CHANGED TO "logging.DEBUG", when run locally to enable debugging!
    logger.addHandler(screen_handler)


async def log(message, bot, level="INFO", debug=""):
    pass
    # Return if the logging level is not DEBUG, and the bot is trying to log some debugging stuff
    logger = logging.getLogger("doot-doot")
    if (logger.getEffectiveLevel != logging.DEBUG) and (level == "DEBUG"):
        return

    logChannel = bot.get_channel(int(config['log_channel']))
    time = datetime.datetime.now().strftime('%H:%M:%S')

    if level == "ERROR":
        levelemote = "❌"
    elif level == "CRITICAL":
        levelemote = "🔥"
    elif level == "WARNING":
        levelemote = "❗"
    elif level == "DEBUG":
        levelemote = "🔧"
    else:
        levelemote = "🔎"

    await logChannel.send("`[" + time + "]` **" + levelemote + " " + level + ":** " + message)

    if debug == "":
        logDebug(message, level)
        return
    logDebug(debug, level)


def logDebug(message, level="INFO"):
    logger = logging.getLogger("doot-doot")

    if level == "DEBUG":
        logger.debug(message)
    elif level == "CRITICAL":
        logger.critical(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    else:
        logger.info(message)


async def logCommand(commandName, ctx, level="INFO"):
    pass
    if isinstance(ctx.message.channel, discord.DMChannel):
        await log(ctx.author.name + "#" + ctx.author.discriminator + " just ran the " + commandName + " command",
                  ctx.bot, level)
    else:
        await log(
            ctx.author.name + "#" + ctx.author.discriminator + " just ran the " + commandName + " command, in the channel #" + ctx.channel.name + " (`" + str(
                ctx.channel.id) + "`), in the guild " + ctx.guild.name + " (`" + str(ctx.guild.id) + "`)", ctx.bot,
            level)
