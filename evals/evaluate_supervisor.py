from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from agents import set_tracing_disabled

from src.agents.agentic_supervisor import (
    investigate_customer_agentically,
)


set_tracing_disabled(True)


SPECIALIST_TOOL_MAP = {
    "investigate_relationship_risk": "Relationship",
    "investigate_support_risk": "Support",
    "investigate_product_adoption": "Product Adoption",
    "investigate_commercial_risk": "Commercial",
    "investigate_voice_of_customer": "Voice of Customer",
}


NEGATION_PATTERNS = {
    "competitor mentioned": [
        "no competitor",
        "competitor mentioned: false",
        "competitor_mentioned\": false",
        "no evidence of competitor",
    ],
    "pricing objection": [
        "no pricing objection",
        "no pricing objections",
        "pricing objection: false",
        "pricing_objection\": false",
        "no evidence of pricing objection",
    ],
    "customer explicitly intends to churn": [
        "no explicit churn",
        "no churn language",
        "churn_language_detected\": false",
        "no evidence of churn",
    ],
}


POSITIVE_CLAIM_PATTERNS = {
    "competitor mentioned": [
        "competitor_mentioned\": true",
        "competitor mentioned: true",
        "competitor was mentioned",
        "competitor is mentioned",
    ],
    "pricing objection": [
        "pricing_objection\": true",
        "pricing objection: true",
        "customer raised a pricing objection",
        "pricing objection detected",
    ],
    "customer explicitly intends to churn": [
        "churn_language_detected\": true",
        "customer intends to churn",
        "customer plans to churn",
        "customer explicitly intends to churn",
        "customer plans to cancel",
        "customer will not renew",
    ],
}


def extract_called_specialists(trace: list[dict]) -> set[str]:
    called = set()

    for event in trace:
        if event.get("type") != "tool_call_item":
            continue

        tool_name = event.get("tool_name")

        if tool_name in SPECIALIST_TOOL_MAP:
            called.add(SPECIALIST_TOOL_MAP[tool_name])

    return called


def flatten_finding(finding) -> str:
    return json.dumps(
        finding.model_dump(),
        default=str,
    ).lower()


def forbidden_claim_absent(
    text: str,
    claim: str,
) -> bool:
    """
    Return True when the forbidden positive assertion is absent.

    Negated statements such as 'no pricing objection' should not fail
    the evaluation merely because they contain the same words.
    """
    claim = claim.lower()

    positive_patterns = POSITIVE_CLAIM_PATTERNS.get(
        claim,
        [claim],
    )

    positive_assertion_found = any(
        pattern.lower() in text
        for pattern in positive_patterns
    )

    if positive_assertion_found:
        return False

    return True


def evaluate_case(case: dict, result: dict) -> dict:
    finding = result["finding"]
    trace = result["trace"]
    usage = result["usage"]

    called = extract_called_specialists(trace)

    required = set(case["required_specialists"])
    acceptable = set(case.get("acceptable_specialists", []))

    required_specialists_pass = required.issubset(called)

    unexpected_specialists = (
        called - required - acceptable
    )

    risk_pass = (
        finding.overall_risk
        in case["expected_overall_risk"]
    )

    text = flatten_finding(finding)

    evidence_checks = {
        term: term.lower() in text
        for term in case["required_evidence_terms"]
    }

    forbidden_checks = {
        claim: forbidden_claim_absent(
            text,
            claim,
        )
        for claim in case["forbidden_claims"]
    }

    evidence_pass = all(evidence_checks.values())
    forbidden_pass = all(forbidden_checks.values())

    overall_pass = all([
        risk_pass,
        required_specialists_pass,
        evidence_pass,
        forbidden_pass,
    ])

    return {
        "case_id": case["case_id"],
        "customer_id": case["customer_id"],
        "pass": overall_pass,
        "risk": {
            "pass": risk_pass,
            "expected": case["expected_overall_risk"],
            "actual": finding.overall_risk,
            "score": finding.overall_risk_score,
        },
        "specialists": {
            "pass": required_specialists_pass,
            "required": sorted(required),
            "called": sorted(called),
            "unexpected": sorted(unexpected_specialists),
            "count": len(called),
        },
        "evidence": {
            "pass": evidence_pass,
            "checks": evidence_checks,
        },
        "forbidden_claims": {
            "pass": forbidden_pass,
            "checks": forbidden_checks,
        },
        "usage": {
            "requests": usage.requests,
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "total_tokens": usage.total_tokens,
        },
    }


async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--cases",
        default="evals/cases/customer_risk_cases.json",
    )

    args = parser.parse_args()

    cases = json.loads(
        Path(args.cases).read_text()
    )

    results = []

    for case in cases:
        print(
            f"\nRunning eval: {case['case_id']} "
            f"({case['customer_id']})"
        )

        run = await investigate_customer_agentically(
            case["customer_id"]
        )

        evaluation = evaluate_case(case, run)

        results.append(evaluation)

        print(
            json.dumps(
                evaluation,
                indent=2,
            )
        )

    Path("evals/results").mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        Path("evals/results")
        / "latest_supervisor_eval.json"
    )

    output_path.write_text(
        json.dumps(
            results,
            indent=2,
        )
    )

    passed = sum(
        1 for result in results
        if result["pass"]
    )

    print("\n=== EVAL SUMMARY ===")
    print(f"Passed: {passed}/{len(results)}")
    print(f"Results: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
