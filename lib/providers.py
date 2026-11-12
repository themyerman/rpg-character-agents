"""
Provider shim: run the generators against a local open-weight model instead of
the Anthropic API, without touching any call site.

The agents all talk to the model through one narrow surface:

    client.messages.create(model=, max_tokens=, system=, tools=, messages=)
      -> response.stop_reason in {"end_turn", "tool_use"}
      -> response.content: list of blocks, each either
           - a text block with .text, or
           - a tool-use block with .type == "tool_use", .name, .input, .id

This module provides an OllamaClient that mimics exactly that surface, talking to
a local Ollama server (http://localhost:11434) over stdlib HTTP — no new
dependency. It translates the Anthropic-style message/tool shapes to Ollama's
/api/chat format on the way out and back again, so the existing tool-use loop in
lib/utils works unchanged.

Selection is by environment variable (see lib.utils.get_client):

    RPG_PROVIDER = "anthropic" (default) | "ollama"
    RPG_MODEL    = model name (Ollama, e.g. "llama3.2:3b"; ignored for Anthropic)
    RPG_OLLAMA_HOST = base URL (default "http://localhost:11434")

Default behavior is unchanged: with no env set, the app uses Anthropic exactly as
before. This exists so the trickster battery can compare a small open-weight model
against Claude on the *same* app and prompts.
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from uuid import uuid4


# ── Response blocks mimicking the Anthropic SDK objects the code reads ──────────

class _TextBlock:
    __slots__ = ("type", "text")

    def __init__(self, text: str):
        self.type = "text"
        self.text = text


class _ToolUseBlock:
    __slots__ = ("type", "id", "name", "input")

    def __init__(self, id: str, name: str, input: dict):
        self.type = "tool_use"
        self.id = id
        self.name = name
        self.input = input


class _Response:
    __slots__ = ("content", "stop_reason")

    def __init__(self, content: list, stop_reason: str):
        self.content = content
        self.stop_reason = stop_reason


# ── Translation: Anthropic-style <-> Ollama /api/chat ──────────────────────────

def _tools_to_ollama(tools: list | None) -> list | None:
    """Anthropic tool (name/description/input_schema) -> Ollama function tool."""
    if not tools:
        return None
    out = []
    for t in tools:
        out.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
            },
        })
    return out


def _messages_to_ollama(system: str, messages: list) -> list:
    """Translate the running Anthropic-style message list to Ollama chat messages.

    Stateless per call: the loop passes the full history every time, so we rebuild
    a tool-call id -> name map from assistant tool-use blocks as we go, and use it
    to label the tool-result turns Ollama expects as role "tool".
    """
    out: list = []
    if system:
        out.append({"role": "system", "content": system})

    id_to_name: dict[str, str] = {}

    for m in messages:
        role = m["role"]
        content = m["content"]

        # user text
        if role == "user" and isinstance(content, str):
            out.append({"role": "user", "content": content})
            continue

        # user tool results (list of {"type":"tool_result","tool_use_id","content"})
        if role == "user" and isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    out.append({
                        "role": "tool",
                        "content": str(block.get("content", "")),
                        "tool_name": id_to_name.get(block.get("tool_use_id", ""), ""),
                    })
                else:
                    out.append({"role": "user", "content": str(block)})
            continue

        # assistant turn: content is a list of our block objects (echoed back)
        if role == "assistant":
            text_parts = []
            tool_calls = []
            for block in content:
                if getattr(block, "type", None) == "tool_use":
                    id_to_name[block.id] = block.name
                    tool_calls.append({
                        "function": {"name": block.name, "arguments": block.input},
                    })
                elif getattr(block, "type", None) == "text":
                    text_parts.append(block.text)
                elif isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            msg = {"role": "assistant", "content": "".join(text_parts)}
            if tool_calls:
                msg["tool_calls"] = tool_calls
            out.append(msg)
            continue

        # fallback
        out.append({"role": role, "content": str(content)})

    return out


# ── The drop-in client ─────────────────────────────────────────────────────────

class _Messages:
    def __init__(self, host: str, model: str, timeout: float):
        self._host = host.rstrip("/")
        self._model = model
        self._timeout = timeout

    def create(self, *, model=None, max_tokens=4096, system="", messages=None, tools=None):
        """Mimics anthropic client.messages.create for the subset the app uses.

        The hardcoded `model=` passed by call sites (claude-opus-4-7) is ignored;
        the Ollama model comes from configuration.
        """
        payload = {
            "model": self._model,
            "messages": _messages_to_ollama(system, messages or []),
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        ollama_tools = _tools_to_ollama(tools)
        if ollama_tools:
            payload["tools"] = ollama_tools

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self._host}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Ollama request failed ({self._host}/api/chat): {e}. "
                f"Is Ollama running and is model '{self._model}' pulled?"
            ) from e

        msg = body.get("message", {}) or {}
        content: list = []

        text = msg.get("content") or ""
        if text:
            content.append(_TextBlock(text))

        tool_calls = msg.get("tool_calls") or []
        for tc in tool_calls:
            fn = tc.get("function", {}) or {}
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except (ValueError, TypeError):
                    args = {}
            content.append(_ToolUseBlock(f"toolu_{uuid4().hex[:12]}", fn.get("name", ""), args))

        # Guarantee content[0].text exists for the no-tool synthesize path.
        if not content:
            content.append(_TextBlock(""))

        stop_reason = "tool_use" if tool_calls else "end_turn"
        return _Response(content, stop_reason)


class OllamaClient:
    """Drop-in replacement for anthropic.Anthropic covering client.messages.create."""

    def __init__(self, model: str, host: str | None = None, timeout: float = 600.0):
        host = host or os.environ.get("RPG_OLLAMA_HOST", "http://localhost:11434")
        self.messages = _Messages(host, model, timeout)
