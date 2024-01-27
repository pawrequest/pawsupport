from __future__ import annotations

import functools
import sys
from typing import Literal

from loguru import logger


def get_loguru(log_file, profile: Literal["local", "remote", "default"] = None) -> logger:
    if profile == "local":
        logger.info("Using local log profile")
        terminal_format = log_fmt_local_terminal
    elif profile == "remote":
        logger.info("Using remote log profile")
        terminal_format = log_fmt_server_terminal
    elif profile == 'defailt' or profile is None:
        logger.info("Using default log profile (remote)")
        terminal_format = log_fmt_server_terminal
    else:
        raise ValueError(f"Invalid profile: {profile}")

    logger.remove()

    logger.add(log_file, rotation="1 day", delay=True, encoding="utf8")
    logger.add(sys.stderr, level="DEBUG", format=terminal_format)

    return logger


BOT_COLOR = {
    "Scraper": "cyan",
    "Monitor": "green",
    "Backup": "magenta",
}


def log_fmt_local_terminal(record):
    category = record["extra"].get("category", "General")
    bot_colour = BOT_COLOR.get(category, "white")
    category = f"{category:<9}"
    max_length = 100
    file_txt = f"{record['file'].path}:{record['line']}"

    if len(file_txt) > max_length:
        file_txt = file_txt[:max_length]

    # clickable link only works at start of line
    return f"{file_txt:<{max_length}} | <lvl>{record['level']: <7} | {coloured(category, bot_colour)} | {record['message']}</lvl>\n"


def coloured(msg: str, colour: str) -> str:
    return f"<{colour}>{msg}</{colour}>"


def log_fmt_server_terminal(record):
    """Format for server-side logging"""
    category = record["extra"].get("category", "General")
    category = f"{category:<9}"
    colour = BOT_COLOR.get(category, "white")

    file_line = f"{record['file']}:{record['line']}- {record['function']}()"
    bot_says = f"<bold>{coloured(category, colour):<9} </bold> | {coloured(record['message'], colour)}"

    return f"<lvl>{record['level']: <7} </lvl>| {bot_says} | {file_line}\n"


def logger_wraps(*, entry=True, exit=True, level="DEBUG"):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs)
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper