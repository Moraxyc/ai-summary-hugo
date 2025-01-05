import os
import sys
import argparse
import frontmatter
from .dataProcess import DataProcess
from .requestSummary import generate_summary


def main(target_path, model_name, language):
    # 调整 target_path 为目标路径
    data_process = DataProcess(
        os.path.join(target_path, "assets/data/summary/summary.json")
    )
    posts_path = get_posts_path(target_path)

    for post_path in posts_path:
        post = frontmatter.load(post_path)
        slug = post["slug"]
        lang = post.get("lang", "zh")

        # 根据语言调整生成总结时的 prompt
        if language == "zh":
            prompt_prefix = "请在100字内用中文总结以下文章的核心内容: "
        elif language == "en":
            prompt_prefix = (
                "Please summarize the main content of the article within 100 words: "
            )
        else:
            print(
                f"Invalid language specified: {language}. Only 'zh' (Chinese) or 'en' (English) are supported."
            )
            sys.exit(1)

        # 生成总结
        if data_process.check_slug_and_lang_exists(slug, lang):
            json_data = data_process.get_json_by_slug_and_lang(slug, lang)
            if not json_data["generated"]:
                print(
                    f"Generating summary for {post['title']} using {model_name} model in {language}"
                )
                summary_content = generate_summary(
                    post.content, model_name, prompt_prefix
                )
                return_status = True if summary_content else False
                data_process.edit_json_by_slug_and_lang(
                    slug, lang, summary_content, return_status
                )
                data_process.save_json()
            else:
                print(f"Article summary already generated: {post['title']}")
        else:
            print(
                f"Generating summary for article: {post['title']} using {model_name} model"
            )
            summary_content = generate_summary(post.content, model_name, prompt_prefix)
            return_status = True if summary_content else False
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
        default="gpt-3.5-turbo",
        help="AI model name to use for summary generation (default: gpt-3.5-turbo)",
    )
    parser.add_argument(
        "--language",
        type=str,
        choices=["zh", "en"],
        default="zh",
        help="Language for summary generation. 'zh' for Chinese, 'en' for English (default: 'zh')",
    )

    args = parser.parse_args()

    main(args.target, args.model, args.language)


if __name__ == "__main__":
    entry()
