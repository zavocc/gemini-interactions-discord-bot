import os

import discord
from dotenv import load_dotenv

from .subclass import BotClientSubclass

_env_loaded = load_dotenv()
if not _env_loaded:
    raise ValueError("No .env file found")

bot: BotClientSubclass = BotClientSubclass()


@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    _ = await ctx.respond("Hey!")


def main():
    # Traverse through cogs and load them
    for cog in os.listdir(f"src/{bot.BOTNAME}/cogs"):
        if cog.endswith(".py"):
            _ = bot.load_extension(f"{bot.BOTNAME}.cogs.{cog[:-3]}")
    bot.run(os.getenv("DISCORD_TOKEN"))  # run the bot with the token
