import argparse
import os
import sys

import frontmatter

from .dataProcess import DataProcess
from .requestSummary import (
    configure_base_url,
    configure_system_prompt,
    generate_summary,
)


def resolve_prompt(value):
    """Resolve a prompt value. If it starts with '@', read from that file."""
    if value is None:
        return None
    if value.startswith("@"):
        with open(value[1:]) as f:
            return f.read()
    return value


def main(
    target_path, model_name, language, base_url=None, prompt=None, system_prompt=None
):
    # 配置 API 端点（base_url），需在 client 首次实例化之前调用
    configure_base_url(base_url)
    # 配置自定义系统提示词
    configure_system_prompt(resolve_prompt(system_prompt))

    # 调整 target_path 为目标路径
    data_process = DataProcess(
        os.path.join(target_path, "assets/data/summary/summary.json")
    )
    posts_path = get_posts_path(target_path)

    # 自定义 prompt 优先于语言默认值
    custom_prompt_prefix = resolve_prompt(prompt)

    for post_path in posts_path:
        post = frontmatter.load(post_path)
        slug = post["slug"]
        lang = post.get("lang", "zh")

        # 根据语言调整生成总结时的 prompt（未指定自定义 prompt 时）
        if custom_prompt_prefix is not None:
            prompt_prefix = custom_prompt_prefix
        elif language == "zh":
            prompt_prefix = "请在100字内用中文总结以下文章的核心内容: "
        elif language == "en":
            prompt_prefix = (
                "Please summarize the main content of the article within 100 words: "
            )
        else:
            print(
                f"Invalid language specified: {language}. Only 'zh' (Chinese)"
                " or 'en' (English) are supported."
            )
            sys.exit(1)

        # 生成总结
        if data_process.check_slug_and_lang_exists(slug, lang):
            json_data = data_process.get_json_by_slug_and_lang(slug, lang)
            if not json_data["generated"]:
                print(
                    f"Generating summary for {post['title']} using"
                    f" {model_name} model in {language}"
                )
                summary_content = generate_summary(
                    post.content, model_name, prompt_prefix
                )
                return_status = bool(summary_content)
                data_process.edit_json_by_slug_and_lang(
                    slug, lang, summary_content, return_status
                )
                data_process.save_json()
            else:
                print(f"Article summary already generated: {post['title']}")
        else:
            print(
                f"Generating summary for article: {post['title']} using"
                f" {model_name} model"
            )
            summary_content = generate_summary(post.content, model_name, prompt_prefix)
            return_status = bool(summary_content)
            if not return_status:
                print(f"Failed to generate summary for article: {post['title']}")
            new_summary = {
                "title": post["title"],
                "slug": slug,
                "lang": language,
                "generated": return_status,
                "summary": summary_content,
            }
            data_process.add_new_summary(new_summary)
            data_process.save_json()

    sys.exit(0)


def get_posts_path(target_path):
    # 将 posts 路径替换为基于 target_path 的完整路径
    posts_folder = os.path.join(target_path, "content/posts")
    paths = []
    for root, _, files in os.walk(posts_folder):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                paths.append(file_path)
    return paths


def entry():
    parser = argparse.ArgumentParser(description="Generate article summaries.")
    parser.add_argument(
        "--target",
        type=str,
        default="../",  # 设置默认目标路径为上一路径
        help="Base target directory for processing (default: parent directory)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="AI model name to use for summary generation (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--language",
        type=str,
        choices=["zh", "en"],
        default="zh",
        help="Language for summary generation: 'zh' (Chinese) or 'en'"
        " (English), default 'zh'",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Custom OpenAI-compatible API endpoint (base URL), e.g."
        " https://api.deepseek.com/v1 (default: OpenAI official endpoint"
        " or OPENAI_BASE_URL env var)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Custom user prompt prefix prepended to the article content."
        " Prefix with '@' to read from a file, e.g. @prompts/summary.txt"
        " (default: language-based built-in prompt)",
    )
    parser.add_argument(
        "--system-prompt",
        type=str,
        default=None,
        help="Override the built-in system prompt. Prefix with '@' to read"
        " from a file (default: concise summarizer instruction)",
    )

    args = parser.parse_args()

    main(
        args.target,
        args.model,
        args.language,
        args.base_url,
        args.prompt,
        args.system_prompt,
    )


if __name__ == "__main__":
    entry()
