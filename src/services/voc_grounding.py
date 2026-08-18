from __future__ import annotations

from typing import Any

from src.repositories import MeetingRepository


CHURN_TERMS = (
    "cancel",
    "cancellation",
    "not renew",
    "non-renew",
    "nonrenew",
    "leave the platform",
    "leaving the platform",
    "switch provider",
    "switching provider",
    "replace the platform",
    "replacing the platform",
    "evaluating alternatives",
    "evaluate alternatives",
)

COMPETITOR_TERMS = (
    "competitor",
    "alternative provider",
    "alternative vendor",
)


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    normalized = text.lower()
    return any(term in normalized for term in terms)


def validate_voc_finding(
    customer_id: str,
    finding: Any,
):
    notes = MeetingRepository().get_customer_notes(customer_id)

    note_map = {
        note["note_id"]: note["note_text"]
        for note in notes
    }

    validation_errors: list[str] = []

    # 1. Validate evidence IDs and evidence text.
    for evidence in finding.evidence:
        source_text = note_map.get(evidence.note_id)

        if source_text is None:
            validation_errors.append(
                f"Unknown evidence note_id: {evidence.note_id}"
            )
            continue

        if evidence.evidence_text.strip() not in source_text:
            validation_errors.append(
                f"Evidence text for {evidence.note_id} does not "
                "match the source note."
            )

    all_note_text = " ".join(note_map.values())

    # 2. Validate explicit churn-language classification.
    actual_churn_language = _contains_any(
        all_note_text,
        CHURN_TERMS,
    )

    if finding.churn_language_detected and not actual_churn_language:
        finding.churn_language_detected = False

        # Churn was unsupported, so reduce the qualitative risk.
        finding.risk_score = min(finding.risk_score, 35.0)

        if finding.risk_level.lower() in {"high", "critical"}:
            finding.risk_level = "Low"

        validation_errors.append(
            "Removed unsupported churn-language classification."
        )

    # 3. Validate explicit competitor classification.
    actual_competitor_language = _contains_any(
        all_note_text,
        COMPETITOR_TERMS,
    )

    if (
        finding.competitor_mentioned
        and not actual_competitor_language
    ):
        finding.competitor_mentioned = False
        validation_errors.append(
            "Removed unsupported competitor classification."
        )

    # 4. Organizational change alone is not customer sentiment.
    organizational_only = (
        "champion" in all_note_text.lower()
        and not actual_churn_language
        and not actual_competitor_language
    )

    if organizational_only:
        finding.sentiment = "Neutral"
        finding.sentiment_score = 0.0

        # Organizational/stakeholder changes belong to the
        # Relationship specialist, not Voice of Customer.
        if not any([
            finding.churn_language_detected,
            finding.competitor_mentioned,
            finding.pricing_objection,
            finding.product_gap_detected,
            finding.expansion_signal_detected,
        ]):
            finding.risk_level = "Low"
            finding.risk_score = min(
                finding.risk_score,
                20.0,
            )

            finding.summary = (
                "Recent customer notes document an organizational change: "
                "the primary champion left and a new business owner has not "
                "yet been confirmed. The notes contain no explicit negative "
                "sentiment, churn language, competitor mention, pricing "
                "objection, or product-gap signal. This should be evaluated "
                "by the Relationship specialist rather than treated as "
                "Voice of Customer risk."
            )

    if validation_errors:
        finding.missing_information.extend(
            [
                f"Grounding validation: {error}"
                for error in validation_errors
            ]
        )

    return finding
