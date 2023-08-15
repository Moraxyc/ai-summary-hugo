'''
Author: Moraxyc me@morax.icu
Date: 2023-08-16 02:32:59
LastEditors: Moraxyc me@morax.icu
LastEditTime: 2023-08-16 03:13:45
FilePath: /ai-summary-hugo/requestSummary.py
Description: 

Copyright (c) 2023 by Moraxyc, All Rights Reserved. 
'''
import openai
import os

def generate_summary(prompt):
    api_key = os.environ["OPENAI_API_KEY"]
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "请用中文, 100 字总结以下的核心内容："},
            {"role": "user", "content": prompt}
        ]
    )
    return response.get("choices")[0]["message"]["content"]
