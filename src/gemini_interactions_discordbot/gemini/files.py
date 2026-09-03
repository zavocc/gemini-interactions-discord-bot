import asyncio
from pathlib import Path
from urllib.parse import unquote, urlsplit
from uuid import uuid4

import aiofiles
import aiohttp

from gemini_interactions_discordbot import BotClient


async def upload_file(bot: BotClient, aiohttp_session: aiohttp.ClientSession, attachment_url: str) -> str:
    temporary_directory = Path.cwd() / ".tmp"
    temporary_directory.mkdir(exist_ok=True)

    original_path = Path(Path(unquote(urlsplit(attachment_url).path)).name)
    truncated_name = original_path.stem[:15] or "attachment"
    temporary_path = temporary_directory / (f"{uuid4()}.{truncated_name}{original_path.suffix}")

    try:
        async with aiohttp_session.get(attachment_url) as response:
            response.raise_for_status()

            async with aiofiles.open(temporary_path, "wb") as file:
                async for chunk in response.content.iter_chunked(64 * 1024):
                    _ = await file.write(chunk)

        uploaded_file = await bot.csession_google.aio.files.upload(file=temporary_path)

        # Check for processing status and we wait
        while not uploaded_file.state or uploaded_file.state.name != "ACTIVE":
            _ = await asyncio.sleep(5)
            uploaded_file = await bot.csession_google.aio.files.get(name=uploaded_file.name) # pyright: ignore[reportArgumentType]

        if not uploaded_file.uri:
            raise RuntimeError("File does not have a URI")

        # Return the file URI
        return uploaded_file.uri
    finally:
        temporary_path.unlink(missing_ok=True)
