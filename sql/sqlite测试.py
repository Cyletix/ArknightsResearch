'''
Description: 文件描述
Author: Cyletix
Date: 2023-01-27 22:39:37
LastEditTime: 2023-01-27 22:41:21
FilePath: \ArknightsResearch\sqlite测试.py
'''
import sqlite3

# 创建与数据库的连接,返回一个Connection对象，我们就是通过这个对象与数据库进行交互
conn = sqlite3.connect('test.db')

#在内存中创建数据库
conn = sqlite3.connect(':memory:')

#创建一个游标 cursor
cur = conn.cursor()

# 建表的sql语句
sql_text_1 = '''CREATE TABLE scores
           (姓名 TEXT,
            班级 TEXT,
            性别 TEXT,
            语文 NUMBER,
            数学 NUMBER,
            英语 NUMBER);'''
# 执行sql语句
cur.execute(sql_text_1)
