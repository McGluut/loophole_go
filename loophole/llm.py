from __future__ import annotations

from loophole.errors import DependencyError, ProtocolError


class LLMClient:
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
    ):
        try:
            import anthropic
        except ModuleNotFoundError as exc:
            raise DependencyError(
                "The 'anthropic' package is required to run Loophole's live agent loop. "
                "Install project dependencies before starting a session."
            ) from exc

        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens

    def call(self, system: str, user_message: str, temperature: float = 0.5) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        text_blocks = [
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text" and getattr(block, "text", None)
        ]
        if not text_blocks:
            raise ProtocolError("Model response did not contain any text content.")
        return "\n".join(text_blocks)
