'''
Author: Moraxyc me@morax.icu
Date: 2023-08-16 00:40:10
LastEditors: Moraxyc me@morax.icu
LastEditTime: 2023-08-16 03:11:02
FilePath: /ai-summary-hugo/main.py
Description: 

Copyright (c) 2023 by Moraxyc, All Rights Reserved. 
'''
import os
import sys
import frontmatter
from dataProcess import dataProcess
from requestSummary import generate_summary

if __name__ != '__main__':
    print("请直接输入\"python main.py\"运行")
    sys.exit(0)

def getPostsPath():
    paths = []
    for root, _, files in os.walk("./content/posts"):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                paths.append(file_path)
    return paths

data_process = dataProcess("./data/summary/summary.json")

path = iter(getPostsPath())
while True:
    try:
        post = frontmatter.load(next(path))
        if data_process.check_slug_exists(post['slug']):
            json_data = data_process.get_json_by_slug(post['slug'])
            if not json_data['generated']:
                data_process.edit_json_by_slug(post['slug'], generate_summary(post.content), True)
                data_process.save_json()
        else:
            summary_content = generate_summary(post.content)
            new_summary = {
                "title": post['title'],
                "slug": post['slug'],
                "generated": True,
                "summary": summary_content
            }
            data_process.add_new_summary(new_summary)
            data_process.save_json()
    except StopIteration:
        break

sys.exit(0)