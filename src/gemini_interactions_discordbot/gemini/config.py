from pathlib import Path
from typing import Literal

import aiofiles
from pydantic import BaseModel, Field, ValidationError

# for now it reads config.json from CWD
FILEJSON = Path.cwd() / "config.json"

class AgentConfig(BaseModel):
    model: str = Field(default="gemini-3.8-flash", description="The model to use for the bot")
    web_search: bool = Field(default=False, description="Use Google Search to ground the model")
    reasoning_effort: Literal["low", "medium", "high"] = Field(default="low", description="The level of reasoning effort to use")
    service_tier: Literal["flex", "priority"] | None = Field(default=None, description="The service tier to use")

# Parse and load the config
# TODO: store this within the entire bot lifecycle rather than reloading it each time
async def load_config() -> AgentConfig:
    # Check if file exists otherwise we return defaults
    try:
        async with aiofiles.open(FILEJSON, mode="r") as f:
            data = await f.read()
            return AgentConfig.model_validate_json(data)
    except FileNotFoundError:
        return AgentConfig()
    except ValidationError:
        raise
