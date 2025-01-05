import openai
from openai import OpenAI
import os


def generate_summary(prompt):
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "请在100字内用中文总结以下文章的核心内容: ",
                },
                {"role": "user", "content": prompt},
            ],
            model="gpt-3.5-turbo",
        )
        return response.choices[0].message.content
    except openai.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
    except openai.RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
    except openai.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
