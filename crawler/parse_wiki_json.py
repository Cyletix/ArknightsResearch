'''
Description: 文件描述
Author: Cyletix
Date: 2023-01-11 00:23:13
LastEditTime: 2023-01-11 03:24:23
FilePath: \ArknightsResearch\parse_wiki_json.py
'''
import json

json_path='\精一满级全部记录.json'
with open(json_path, 'r', encoding='utf8') as f:
    json_content=json.load(f)
    f.close()

json_content['records']