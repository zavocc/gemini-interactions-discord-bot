# Threads manager
import json
from pathlib import Path
from typing import cast

import aiofiles
import aiofiles.os

# TODO: ensure conversations dir is placed in root project, right now its based on whatever the user is in CWD
THREADS_DIR = Path.cwd() / "conversations"

async def load_thread_id(user_id: int) -> str | None:
    try:
        async with aiofiles.open(THREADS_DIR / f"{user_id}.json", "r") as f:
            # read stateful_conv_id property
            data = await f.read()
            loaded_json = cast(dict[str, object], json.loads(data))
            thread_id = loaded_json.get("stateful_conv_id")

            # if the stateful_conv_id has empty value, return None
            if not thread_id:
                return None

            # Check if thread_id is a string
            if not isinstance(thread_id, str):
                return None

            return thread_id
    except (FileNotFoundError, json.JSONDecodeError):
        return None


async def save_thread_id(user_id: int, thread_id: str) -> None:
    THREADS_DIR.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(THREADS_DIR / f"{user_id}.json", "w") as f:
        _ = await f.write(json.dumps({"stateful_conv_id": thread_id}))

async def clear_thread_id(user_id: int) -> None:
    try:
        await aiofiles.os.remove(THREADS_DIR / f"{user_id}.json")
    except FileNotFoundError:
        pass
