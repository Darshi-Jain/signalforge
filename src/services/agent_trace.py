from __future__ import annotations

from typing import Any


def extract_run_trace(result: Any) -> list[dict]:
    events: list[dict] = []

    for item in result.new_items:
        event = {
            "type": getattr(item, "type", type(item).__name__),
        }

        raw_item = getattr(item, "raw_item", None)

        if raw_item is not None:
            name = getattr(raw_item, "name", None)
            arguments = getattr(raw_item, "arguments", None)

            if name:
                event["tool_name"] = name

            if arguments:
                event["arguments"] = arguments

        output = getattr(item, "output", None)

        if output is not None:
            event["output"] = str(output)

        events.append(event)

    return events
