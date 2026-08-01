from __future__ import annotations

from src.models.voice_of_customer import VoiceOfCustomerFinding
from src.providers.gemini import GeminiProvider
from src.tools import get_recent_meeting_notes


SYSTEM_INSTRUCTION = """
You are the Voice of Customer Agent for SignalForge.

Analyze only the supplied customer meeting notes.

Your responsibilities:
- Determine customer sentiment.
- Detect competitor mentions.
- Detect pricing objections.
- Detect product or capability gaps.
- Detect explicit or implied churn language.
- Assign a risk level.
- Cite evidence using the supplied note identifiers.

Rules:
- Do not invent facts.
- Do not use information outside the supplied notes.
- Every important conclusion must be supported by evidence.
- Use low confidence when evidence is limited or contradictory.
"""


class VoiceOfCustomerAgent:
    def __init__(
        self,
        provider: GeminiProvider | None = None,
    ) -> None:
        self.provider = provider or GeminiProvider()

    def analyze(
        self,
        customer_id: str,
    ) -> VoiceOfCustomerFinding:
        notes = get_recent_meeting_notes(
            customer_id=customer_id,
            limit=6,
        )

        if not notes:
            raise ValueError(
                f"No meeting notes found for customer: {customer_id}"
            )

        note_text = "\n\n".join(
            (
                f"Source ID: {note.note_id}\n"
                f"Date: {note.meeting_date}\n"
                f"Meeting type: {note.meeting_type}\n"
                f"Text: {note.note_text}"
            )
            for note in notes
        )

        prompt = f"""
Customer ID: {customer_id}

Analyze the following customer meeting notes.

{note_text}
"""

        return self.provider.generate_structured(
            prompt=prompt,
            output_schema=VoiceOfCustomerFinding,
            system_instruction=SYSTEM_INSTRUCTION,
        )
