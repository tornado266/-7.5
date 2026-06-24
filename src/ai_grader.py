"""AI provider client and IELTS grading request."""

import os

from openai import APIConnectionError, APIStatusError, OpenAI, OpenAIError

from src.prompts import build_grading_prompt


class AIGraderError(Exception):
    """Detailed error raised when an AI provider request fails."""

    def __init__(
        self,
        provider: str,
        model: str,
        original_error: Exception,
        status_code: int | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.original_error = original_error
        self.status_code = status_code
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        error_type = type(self.original_error).__name__
        status = self.status_code if self.status_code is not None else "N/A"
        return (
            f"Provider: {self.provider}\n"
            f"Model: {self.model}\n"
            f"Exception Type: {error_type}\n"
            f"HTTP Status Code: {status}\n\n"
            f"{error_type}:\n{self.original_error}"
        )


def build_client(provider: str) -> OpenAI:
    """Create an API client for DeepSeek or OpenAI."""
    if provider == "DeepSeek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY is missing. Please set it before running the app."
            )

        return OpenAI(
            api_key=api_key,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Please set it before running the app."
        )

    return OpenAI(api_key=api_key)


def grade_essay(provider: str, task_type: str, topic: str, essay: str, model: str) -> str:
    """Send the IELTS essay to an AI provider and return a markdown correction report."""
    client = build_client(provider)

    prompt = build_grading_prompt(
        task_type=task_type,
        topic=topic,
        essay=essay,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert IELTS Writing examiner.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    except APIStatusError as exc:
        raise AIGraderError(
            provider=provider,
            model=model,
            original_error=exc,
            status_code=exc.status_code,
        ) from exc
    except (APIConnectionError, OpenAIError) as exc:
        raise AIGraderError(
            provider=provider,
            model=model,
            original_error=exc,
        ) from exc
    except Exception as exc:
        raise AIGraderError(
            provider=provider,
            model=model,
            original_error=exc,
        ) from exc

    return response.choices[0].message.content or ""
