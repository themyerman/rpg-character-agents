"""
Stage 1: Basic API call — ask Claude something, get an answer.
Run with: python main.py
"""

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment


def ask(prompt: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    return response.content[0].text


if __name__ == "__main__":
    answer = ask("What is the capital of France? Answer in one sentence.")
    print(answer)
