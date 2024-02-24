'''
Author: Moraxyc me@morax.icu
Date: 2023-08-16 01:55:38
LastEditors: Moraxyc me@morax.icu
LastEditTime: 2023-08-16 11:50:00
FilePath: /ai-summary-hugo/dataProcess.py
Description: 处理summary.json数据

Copyright (c) 2023 by Moraxyc, All Rights Reserved. 
'''
import json
import os
import shutil
import sys


class dataProcess:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_json()
        if not self.data:
            print("文件结构错误! 请删除summary.json或调整结构!")
            sys.exit(0)
        self.slug_cache = {}

    def load_json(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as json_file:
                data = json.load(json_file)
            return data if self.validate_json_structure else False
        else:
            try:
                print("summary.json不存在, 初始化中")
                os.makedirs(self.file_path.rstrip(
                    'summary.json'), exist_ok=True)
                shutil.copy("./summary.json", self.file_path)
                with open(self.file_path, 'r') as json_file:
                    data = json.load(json_file)
                return data
            except FileNotFoundError:
                print("初始化summary.json失败, 源文件不存在")
            except OSError as e:
                print(f"初始化summary.json文件时出现错误: {e}")

    def validate_json_structure(self, data):
        if data == {"summaries": []}:
            return True
        if not isinstance(data, dict):
            return False
        summaries = data.get("summaries")
        if not isinstance(summaries, list):
            return False
        for summary in summaries:
            if not isinstance(summary, dict):
                return False
            required_keys = {"title", "slug", "generated", "summary"}
            if not all(key in summary for key in required_keys):
                return False
        return True

    def check_slug_exists(self, target_slug):
        if target_slug in self.slug_cache:
            return self.slug_cache[target_slug]
        for summary in self.data.get("summaries", []):
            if summary.get("slug") == target_slug:
                self.slug_cache[target_slug] = True
                return True
        self.slug_cache[target_slug] = False
        return False

    def get_json_by_slug(self, target_slug):
        for summary in self.data.get("summaries", []):
            if summary.get("slug") == target_slug:
                return summary
        return None

    def edit_json_by_slug(self, target_slug, new_summary, new_state):
        for summary in self.data.get("summaries", []):
            if summary.get("slug") == target_slug:
                summary["summary"] = new_summary
                summary["generated"] = new_state
                return None
        return None

    def save_json(self):
        with open(self.file_path, 'w') as json_file:
            json.dump(self.data, json_file, indent=4, ensure_ascii=False)

    def add_new_summary(self, new_summary):
        if "summaries" not in self.data:
            self.data["summaries"] = []
        self.data["summaries"].append(new_summary)