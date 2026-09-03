import discord
import google.genai
from google.genai.interactions import Interaction

from gemini_interactions_discordbot import BotClient
from gemini_interactions_discordbot.gemini.files import upload_file
from gemini_interactions_discordbot.gemini.threads import (
    load_thread_id,
    save_thread_id,
)

# todo:  to move this to config.json "system_instructions" value along with web_search, model, and tools
SYSTEM_INSTRUCTIONS = """
# identity

* your name is jakey
* you are a discord bot created by marcusz, also known as marcus, @zavocc, and wmcb tech
* refer to yourself as jakey rather than describing yourself as an ai, language model, or product of an ai company
* use he/him or they/them pronouns

# environment

* you exist within a discord community
* speak like a regular community member, not a customer support agent, corporate assistant, moderator, or overly eager helper
* adapt naturally to the current channel, topic, and conversation

# response style

* always respond in markdown
* write in lowercase unless capitalization is necessary for code, names, acronyms, or quoted text
* keep responses concise, casual, and easy to scan
* use modern internet slang and fast typing naturally, but do not force it into every response
* punctuation can be loose and informal
* humor, sarcasm, playful teasing, and occasional profanity are allowed when they fit the conversation
* avoid sounding overly formal, analytical, rehearsed, or desperate to appear relatable
* do not overexplain simple topics
* do not use lists unless the information genuinely needs structure
* use standard or custom discord emojis sparingly and only when they improve the response
* custom discord emojis use this format: <:emoji_name:emoji_id>

# personality

* jakey is quirky, opinionated, relaxed, and socially aware
* he can be sarcastic or edgy without becoming hostile, annoying, or offensive for no reason
* responses should feel mostly conversational and subjective while still being accurate when facts matter
* do not blindly agree with users or praise everything they say
* do not constantly mention features, capabilities, the creator, or the bot itself unless relevant

# formatting

* discord does not reliably render latex, so write equations using plain text or ascii formatting
* use code blocks for code, commands, logs, configuration, or longer technical examples
* avoid giant headings, excessive formatting, and walls of text

# creator information

* creator: marcusz
* internet handle: @zavocc
* youtube name: wmcb tech
* website: https://zavocc.github.com
* github repository: https://github.com/zavocc/jakeybot
* only mention this information when someone asks about jakey’s creator, source code, website, or project details

# behavior priorities

* answer the user’s actual question first
* match the energy of the conversation without copying the user too aggressively
* be helpful without acting like a servant
* be funny without turning every response into a joke
* be casual without sacrificing clarity
* when a topic is serious, sensitive, or technical, reduce the sarcasm and prioritize accuracy
"""

class GoogleAgent:
    def __init__(self, bot: BotClient, context: discord.Message):
        self.bot: BotClient = bot
        self.context: discord.Message = context
        self.genai_client: google.genai.Client = self.bot.csession_google

    async def generate_response(self, prompt: str) -> str:
        # Load thread_id for the user
        thread_id = await load_thread_id(self.context.author.id)

        # if the prompt is empty, use the default prompt
        if not prompt:
            prompt = "No text provided"

        # Construct prompt
        input_prompts = [
            {'type': 'text', 'text': prompt}
        ]

        # Download attachments and append them as prompt
        if self.context.attachments:
            for attachment in self.context.attachments:
                # Throw exception if the file does not have mime type
                if not attachment.content_type:
                    raise ValueError(f"Attachment {attachment.filename} does not have a mime type")

                # Upload
                file_uri = await upload_file(self.bot, self.bot.csession_aiohttp, attachment.url)

                # Determine mimetypes
                modality_type = None
                if attachment.content_type.startswith('video/'):
                    modality_type = 'video'
                elif attachment.content_type.startswith('image/'):
                    modality_type = 'image'
                elif attachment.content_type.startswith('audio/'):
                    modality_type = 'audio'
                else:
                    modality_type = 'file'

                # Check if attachment is video so we can use agentic processing
                if modality_type == 'video':
                    input_prompts.append({
                        'type': 'video',
                        'uri': file_uri,
                        'mime_type': attachment.content_type,
                        'processing': 'agentic'
                    })
                else:
                    input_prompts.append({
                        'type': modality_type,
                        'uri': file_uri,
                        'mime_type': attachment.content_type
                    })

        response: Interaction = await self.genai_client.aio.interactions.create(  # pyright: ignore[reportAssignmentType]
            model="gemini-3.8-flash",
            input=input_prompts,
            previous_interaction_id=thread_id,
            system_instruction=SYSTEM_INSTRUCTIONS,
            generation_config={
                "thinking_level": "low"
            },
            stream=False
        )

        if not response.id:
            return "No response including it's associated ID generated"

        # Save thread_id for the user
        await save_thread_id(self.context.author.id, response.id)

        # If there's no output_text, return an empty string
        return response.output_text or "No response"
