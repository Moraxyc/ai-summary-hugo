'''
Author: Moraxyc me@morax.icu
Date: 2023-08-16 00:40:10
LastEditors: Moraxyc me@morax.icu
LastEditTime: 2023-08-16 12:01:11
FilePath: /blog-hugo/ai-summary-hugo/main.py
Description: 脚本运行入口

Copyright (c) 2023 by Moraxyc, All Rights Reserved. 
'''
import os
import sys
import frontmatter
from .dataProcess import dataProcess
from .requestSummary import generate_summary

def main():
    data_process = dataProcess("../data/summary/summary.json")
    posts_path = get_posts_path()

    for post_path in posts_path:
        post = frontmatter.load(post_path)
        slug = post['slug']

        if data_process.check_slug_exists(slug):
            json_data = data_process.get_json_by_slug(slug)
            if not json_data['generated']:
                print("Generating summary for" + post['title'])
                summary_content = generate_summary(post.content)
                return_status = True if summary_content else False
                data_process.edit_json_by_slug(slug, summary_content, return_status)
                data_process.save_json()
            else:
                print("文章已生成总结: " + post["title"])
        else:
            print("为文章生成总结: " + post['title'])
            summary_content = generate_summary(post.content)
            return_status = True if summary_content else False
            if not return_status:print("为文章生成总结失败: " + post['title'])
            new_summary = {
                "title": post['title'],
                "slug": slug,
                "generated": return_status,
                "summary": summary_content
            }
            data_process.add_new_summary(new_summary)
            data_process.save_json()

    sys.exit(0)

def get_posts_path():
    paths = []
    for root, _, files in os.walk("../content/posts"):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                paths.append(file_path)
    return paths

if __name__ == '__main__':
    main()
