import discord
from discord.ext import commands

from gemini_interactions_discordbot import BotClient
from gemini_interactions_discordbot.gemini import Agent


# message chunker, splits messages to list
def chunk_message(message: str, chunk_size: int = 2000) -> list[str]:
    return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

class EventListeners(commands.Cog):
    def __init__(self, bot: BotClient): # pyright: ignore[reportMissingSuperCall]
        self.bot: BotClient = bot

    # on_message
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Strip mention of bot ID
        cleaned_message = message.content.replace(f"<@{self.bot.user.id}>", "").strip()  # pyright: ignore[reportOptionalMemberAccess]

        # Init agent
        agent_instance = Agent(self.bot, message)

        # Generate response
        try:
            async with message.channel.typing():
                response = await agent_instance.generate_response(cleaned_message)

            # Send response
            for chunk in chunk_message(response):
                _ = await message.channel.send(chunk)
        except Exception:
            _ = await message.channel.send(f"<@{message.author.id}> an error occurred when generating a response.")
            raise

def setup(bot: BotClient):
    bot.add_cog(EventListeners(bot))
