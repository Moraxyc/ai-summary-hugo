import os

from openai import (
    APIConnectionError,
    APIStatusError,
    OpenAI,
    RateLimitError,
)

_client: OpenAI | None = None
_base_url: str | None = None
_system_prompt = (
    "You are a concise summarizer. Summarize the article accurately and briefly."
)


def configure_base_url(base_url: str | None) -> None:
    """Set the API endpoint (base URL) for the OpenAI-compatible client.

    Must be called before the client is first instantiated. When None,
    falls back to the OPENAI_BASE_URL environment variable and finally
    the OpenAI SDK default.
    """
    global _base_url
    _base_url = base_url


def configure_system_prompt(system_prompt: str | None) -> None:
    """Override the system prompt used for summary generation."""
    global _system_prompt
    if system_prompt is not None:
        _system_prompt = system_prompt


def get_client() -> OpenAI:
    global _client
    if _client is None:
        base_url = _base_url or os.environ.get("OPENAI_BASE_URL")
        _client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), base_url=base_url)
    return _client


def generate_summary(
    content,
    model_name="gpt-4o-mini",
    prompt_prefix="请在100字内用中文总结以下文章的核心内容: ",
):
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": _system_prompt},
                {"role": "user", "content": prompt_prefix + content},
            ],
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except APIConnectionError as e:
        print("The server could not be reached. Please check your network connection.")
        print(e.__cause__)
    except RateLimitError:
        print("Rate limit exceeded (status code 429). Please wait before retrying.")
    except APIStatusError as e:
        print(f"API returned a non-200 status code: {e.status_code}")
        print(f"Response: {e.response}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None
