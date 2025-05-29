#!/usr/bin/env python3

import sys
import asyncio
import logging

import niobot
import yaml

from _lib.config import get_owners
from _lib.logs import initialize_logger
from _lib.matrix import check_homeserver_wellknown
from _lib.enums import ReactionEmojis

# ================================================
# Initialization!  DO NOT EDIT!
# ================================================

logger = initialize_logger()
logging.basicConfig(filename="debug.log", level=logging.DEBUG, encoding="utf-8",
                    errors="backslashreplace")

# Load base credentials and matrix information
try:
    with open('.matrix_credentials.yaml', mode="r") as f:
        credentials = yaml.safe_load(f)
except Exception as e:
    logger.critical(f"Encountered error loading matrix credentials. | {str(e)}", exc_info=e)
    sys.exit(1)

# Load base bot configuration
try:
    with open('config.yaml', mode="r") as f:
        bot_config = yaml.safe_load(f)
except Exception as e:
    logger.critical(f"Encountered error loading base bot configuration. | {str(e)}",
                    exc_info=e)
    sys.exit(1)


# Initialize Bot
bot = niobot.NioBot(
    homeserver=check_homeserver_wellknown(bot_config["home_domain"]),
    user_id=credentials['USER_ID'],
    device_id=bot_config["device_id"],  # default is nio-bot if not specified
    store_path=bot_config["store_path"],  # Need details - no "What is the store?" section
    command_prefix=bot_config["command_prefix"],
    case_insensitive=bot_config["case_insensitive"],
    owner_id=bot_config["owners"][0],  # Note we use lib.decorators.@is_owner for checks now
    ignore_self=bot_config["ignore_self"],  # Ignore the bot's own messages and commands.
    global_message_type=bot_config['global_message_type']
)
# Load bot modules
bot.mount_module("modules.admin")
bot.mount_module("modules.patch_pilots")


# ================================================
# Event Handlers - Unless you know what you're
# doing, don't touch this area.
# ================================================

@bot.on_event('command_error')
async def on_command_error(ctx: niobot.Context, error: Exception):
    """Called whenever an exception occurs on a command."""
    logger.error(f"Error encountered: {str(error)}", exc_info=error)
    await bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.WARNING.value)


@bot.on_event('command')
async def on_command(ctx: niobot.Context):
    logger.info(f"User {ctx.message.sender} ran command {ctx.command.name}")


@bot.on_event("ready")
async def on_ready(sync_result: niobot.SyncResponse):
    msg = (f"We are CONNECTED!\nHomeserver: {bot.homeserver}\nUser: {bot.user_id}\n"
           f"Device: {bot.device_id}\n"
           f"Auto-joining rooms: \n - ")
    if bot.rooms.keys():
        msg += f"{"\n - ".join(bot.rooms.keys())}"
    else:
        msg += "(None)"
    logger.info(msg)
    if bot_config["ROOM_ID"] not in bot.rooms.keys():
        await bot.join(bot_config["ROOM_ID"])


# ================================================
# Command definitions - don't modify these!
# ================================================

@bot.command(name="owner", description="Indicates who owns and operates this bot.")
async def say_owner(ctx: niobot.Context):
    msg = "My owner(s) are:\n"
    for owner in bot_config["owners"]:
        msg += f" - `{owner}`\n"
    await ctx.respond(msg.rstrip('\r\n'), message_type="m.notice")


# Other Commands are defined in individual command modules.
# These should be imported at the beginning of the file and exist under modules/{SOMETHING}.py


# ================================================
# EXECUTION - DO NOT ALTER
# ================================================

if __name__ == "__main__":
    bot.run(password=credentials["PASSWORD"])
