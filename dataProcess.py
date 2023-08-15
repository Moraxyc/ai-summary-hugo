'''
Author: Moraxyc me@morax.icu
Date: 2023-08-16 01:55:38
LastEditors: Moraxyc me@morax.icu
LastEditTime: 2023-08-16 02:39:14
FilePath: /ai-summary-hugo/dataProcess.py
Description: 

Copyright (c) 2023 by Moraxyc, All Rights Reserved. 
'''
import json

class dataProcess:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_json()
        self.slug_cache = {}

    def load_json(self):
        with open(self.file_path, 'r') as json_file:
            data = json.load(json_file)
        return data

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