from __future__ import annotations

import os

from agents.extensions.models.litellm_model import LitellmModel


def get_agent_model():
    """
    Return the model used by SignalForge tool-using agents.

    For now we use Gemini through Vertex AI.
    Later this factory will support our self-hosted
    Hugging Face/vLLM endpoint as well.
    """

    provider = os.getenv(
        "SIGNALFORGE_AGENT_PROVIDER",
        "gemini",
    )

    if provider == "gemini":
        return LitellmModel(
            model="vertex_ai/gemini-2.5-flash",
        )

    raise ValueError(
        f"Unsupported agent provider: {provider}"
    )
