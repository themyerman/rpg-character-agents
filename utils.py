"""
Shared UI helpers.
"""


def pick(prompt: str, options: list[tuple[str, str]], default_idx: int = 0) -> str:
    """Display a numbered menu and return the selected value.
    Defaults to options[default_idx] on empty or invalid input."""
    print(f"\n{prompt}")
    for i, (_, label) in enumerate(options, 1):
        suffix = "  (default)" if i - 1 == default_idx else ""
        print(f"  {i}. {label}{suffix}")
    raw = input("> ").strip()
    if raw:
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx][0]
        except ValueError:
            pass
    return options[default_idx][0]
