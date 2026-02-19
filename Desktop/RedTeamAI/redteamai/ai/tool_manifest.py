"""Build OpenAI-compatible function calling schemas from tool definitions."""
from __future__ import annotations
from typing import Any


def build_tool_schema(
    name: str,
    description: str,
    parameters: dict[str, Any],
    required: list[str] | None = None,
) -> dict:
    """Build a single OpenAI function-calling tool schema."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required or [],
            },
        },
    }


def string_param(description: str, enum: list[str] | None = None) -> dict:
    p: dict = {"type": "string", "description": description}
    if enum:
        p["enum"] = enum
    return p


def integer_param(description: str, minimum: int | None = None, maximum: int | None = None) -> dict:
    p: dict = {"type": "integer", "description": description}
    if minimum is not None:
        p["minimum"] = minimum
    if maximum is not None:
        p["maximum"] = maximum
    return p


def boolean_param(description: str) -> dict:
    return {"type": "boolean", "description": description}


def array_param(description: str, item_type: str = "string") -> dict:
    return {"type": "array", "items": {"type": item_type}, "description": description}
