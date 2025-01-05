import openai
import os


def generate_summary(
    content,
    model_name="gpt-3.5-turbo",
    prompt_prefix="请在100字内用中文总结以下文章的核心内容: ",
):
    try:
        # 设置 OpenAI API 密钥
        openai.api_key = os.environ.get("OPENAI_API_KEY")

        # 拼接 prompt 内容
        prompt = prompt_prefix + content

        # 调用 OpenAI API 进行总结生成
        response = openai.completions.create(
            model=model_name,
            prompt=prompt,
            max_tokens=150,  # You can adjust the max tokens based on your needs
        )

        # 返回生成的总结内容
        return response["choices"][0]["text"].strip()

    except openai.APIConnectionError as e:
        print("The server could not be reached. Please check your network connection.")
        print(e.__cause__)
    except openai.RateLimitError as e:
        print("Rate limit exceeded (status code 429). Please wait before retrying.")
    except openai.APIStatusError as e:
        print(f"API returned a non-200 status code: {e.status_code}")
        print(f"Response: {e.response}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return None  # 返回 None 以表示失败
