# Architecture

The MVP uses a deterministic, inspectable orchestration layer before introducing LLM autonomy.

1. `CustomerRepository` exposes synthetic customer data as tools.
2. Specialist analyzers inspect adoption, support, relationships, commercial status, and customer sentiment.
3. The investigation orchestrator combines findings using explicit weights.
4. A validation rule adjusts potential seasonal false positives.
5. The system returns a typed `InvestigationReport` containing evidence, confidence, contradictions, and approval-gated actions.

## Next agentic layer

The next version will wrap repository functions as OpenAI Agents SDK function tools. A supervisor agent will decide which tools and specialists to invoke, while deterministic Python remains responsible for calculations. Structured outputs will continue to use the Pydantic schemas in `src/models/schemas.py`.
