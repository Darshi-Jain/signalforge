from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta
from typing import TypeVar

from google import genai
from google.genai import types
from google.oauth2.credentials import Credentials
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


def _get_gcloud_credentials() -> Credentials:
    token = subprocess.check_output(
        ["gcloud", "auth", "print-access-token"],
        text=True,
    ).strip()

    if not token:
        raise RuntimeError(
            "Unable to obtain a gcloud access token. "
            "Run `gcloud auth login` first."
        )

    return Credentials(
        token=token,
        expiry=datetime.utcnow() + timedelta(minutes=55),
    )


class GeminiProvider:
    def __init__(
        self,
        project_id: str | None = None,
        location: str | None = None,
        model: str | None = None,
    ) -> None:
        self.project_id = project_id or os.getenv(
            "GOOGLE_CLOUD_PROJECT",
            "signalforge-csm-ai",
        )
        self.location = location or os.getenv(
            "GOOGLE_CLOUD_LOCATION",
            "global",
        )
        self.model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

        self.client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location,
            credentials=_get_gcloud_credentials(),
        )

    def generate_structured(
        self,
        prompt: str,
        output_schema: type[T],
        system_instruction: str,
    ) -> T:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=output_schema,
            ),
        )

        if response.parsed is None:
            raise RuntimeError("Gemini returned no structured response.")

        return output_schema.model_validate(response.parsed)
