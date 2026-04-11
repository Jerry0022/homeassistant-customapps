"""LLM response parsing and HA conversation agent integration.

Provides generic utilities for extracting structured JSON from LLM
output and calling Home Assistant conversation agents.

Usage::

    from ha_customapps.llm import extract_json, parse_llm_json, call_ha_conversation_agent

    # Extract JSON from LLM output (handles code fences, bare JSON, raw)
    json_str = extract_json(raw_llm_output)
    parsed = parse_llm_json(raw_llm_output)

    # Call HA conversation agent
    response = await call_ha_conversation_agent(hass, prompt, ["openai_conversation", "openai"])
"""

from __future__ import annotations

import json
import re
from typing import Any

from homeassistant.core import HomeAssistant


def extract_json(raw: str) -> str:
    """Extract a JSON object string from raw LLM output.

    Handles three cases in order:
    1. Content wrapped in ``json ... `` or `` ... `` code fences.
    2. Bare JSON with leading/trailing prose -- locates first ``{`` and
       last ``}`` and uses that substring.
    3. Returns the stripped string as-is so ``json.loads()`` can raise a
       meaningful error if none of the above produced valid JSON.
    """
    text = raw.strip()

    # Case 1: markdown code fence
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence_match:
        return fence_match.group(1).strip()

    # Case 2: find first '{' and last '}' to isolate the JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]

    # Case 3: return as-is
    return text


def parse_llm_json(raw: str) -> dict[str, Any]:
    """Extract and parse a JSON object from raw LLM output.

    Parameters
    ----------
    raw : str
        Raw text output from an LLM, possibly containing markdown fences
        or surrounding prose.

    Returns
    -------
    dict
        The parsed JSON object.

    Raises
    ------
    json.JSONDecodeError
        If the extracted text is not valid JSON.
    ValueError
        If the parsed result is not a dict.
    """
    cleaned = extract_json(raw)
    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response must be a JSON object")
    return parsed


async def call_ha_conversation_agent(
    hass: HomeAssistant,
    prompt: str,
    agent_domains: tuple[str, ...] | list[str],
) -> str:
    """Call a Home Assistant conversation agent and return the text response.

    Searches for a configured conversation agent among the given domains
    and sends the prompt to the first one found.

    Parameters
    ----------
    hass : HomeAssistant
        The HA instance.
    prompt : str
        The text prompt to send.
    agent_domains : tuple or list of str
        Integration domains to search for a conversation agent
        (e.g. ``("openai_conversation", "openai")``).

    Returns
    -------
    str
        The agent's text response.

    Raises
    ------
    ValueError
        If no agent is configured or no response is returned.
    """
    agent_entries = []
    for domain in agent_domains:
        agent_entries.extend(hass.config_entries.async_entries(domain))

    if not agent_entries:
        raise ValueError(
            f"No conversation agent configured for domains: {agent_domains}"
        )

    response = await hass.services.async_call(
        "conversation",
        "process",
        {
            "agent_id": agent_entries[0].entry_id,
            "text": prompt,
        },
        blocking=True,
        return_response=True,
    )

    speech = (
        response.get("response", {})
        .get("speech", {})
        .get("plain", {})
        .get("speech")
    )
    if not speech:
        raise ValueError("No response returned by conversation agent")
    return speech
