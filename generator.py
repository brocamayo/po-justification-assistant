"""
Claude API integration for PO justification generation.
Uses forced tool use to guarantee structured JSON output.
"""

import anthropic


def generate_po_justification(user_input: str) -> dict[str, str]:
    """
    Generate a structured PO justification from a free-form description.
    Returns dict with keys: what, why, why_now, why_good_value.
    """
    client = anthropic.Anthropic()

    tools = [
        {
            "name": "record_justification",
            "description": (
                "Record the structured purchase order justification "
                "with all four required sections."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "what": {
                        "type": "string",
                        "description": (
                            "Clear, professional description of what is being purchased "
                            "and its intended purpose in the project."
                        ),
                    },
                    "why": {
                        "type": "string",
                        "description": (
                            "Business rationale explaining why this purchase is necessary "
                            "for manufacturing operations."
                        ),
                    },
                    "why_now": {
                        "type": "string",
                        "description": (
                            "Timing justification — why this purchase must be made now, "
                            "referencing schedule drivers, lead times, or operational urgency."
                        ),
                    },
                    "why_good_value": {
                        "type": "string",
                        "description": (
                            "Value justification — why this cost is reasonable, including "
                            "vendor selection rationale, market comparison, or cost-benefit analysis."
                        ),
                    },
                },
                "required": ["what", "why", "why_now", "why_good_value"],
            },
        }
    ]

    prompt = f"""You are a professional procurement analyst supporting a manufacturing program manager.

The user has described a purchase they need to justify. Extract all relevant details from their \
description and generate a formal Purchase Order justification suitable for management review \
and approval.

User input:
{user_input}

Instructions:
- Write in clear, professional business language suitable for senior management review.
- Be specific and factual — avoid vague or generic phrasing.
- Each section should be 2–4 concise sentences.
- If certain details (e.g. exact cost or vendor) are not mentioned, write naturally around them.
- Focus on business impact, operational necessity, and fiscal responsibility.
- If a project number or reference code is mentioned, preserve it exactly as given — do not reformat or invent a naming convention for it.
"""

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=2048,
        tools=tools,
        tool_choice={"type": "tool", "name": "record_justification"},
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        response = stream.get_final_message()

    for block in response.content:
        if block.type == "tool_use" and block.name == "record_justification":
            return block.input

    raise ValueError(
        "Claude did not return a structured justification. Please try again."
    )
