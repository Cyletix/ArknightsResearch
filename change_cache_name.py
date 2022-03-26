'''
Description: 批量修改缓存网页的名称
Author: Cyletix
Date: 2022-02-19 21:59:37
LastEditTime: 2022-02-19 22:25:43
FilePath: \ArknightsResearch\temp.py
'''
import os
import re

file_dir = 'D:\OneDrive\Code\GitHub\ArknightsResearch\cache\\'
fileList = os.listdir(file_dir)
for file in fileList:
    try:
        op = file.split('html_cache_')[1].split('.html')[0]
        oldname = file_dir + file
        newname = file_dir + op + ' - PRTS - 玩家自由构筑的明日方舟中文Wiki.html'
        os.rename(oldname, newname)  #用os模块中的rename方法对文件改名
        print(oldname, '======>', newname)
    except (IndexError):
        continue
    except (FileExistsError):
        continue