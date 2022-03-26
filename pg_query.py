'''
Description: 查询本地数据库中 所有干员的 指定单列信息，按序号排列，以list形式返回结果
Author: Cyletix
Date: 2021-12-24 14:35:31
LastEditTime: 2022-02-19 22:48:41
FilePath: \ArknightsResearch\pg_query.py
'''
from psycopg2 import connect


def dblink():
    arkdb = connect(database="Arknights",
                    user="postgres",
                    password="shen124357689",
                    host="127.0.0.1",
                    port="5432")
    return arkdb


def pg_query(column: str):
    cursor = dblink().cursor()
    #查询数量
    cursor.execute("""
    SELECT COUNT(*) FROM operators;""")
    count = cursor.fetchone()[0]
    #查询干员信息
    cursor.execute("""
    SELECT {0} FROM operators
    ORDER BY 序号;""".format(column))

    column_list = []
    for i in range(count):
        row = cursor.fetchone()[0]
        column_list.append(row)

    return column_list


def pg_insert(column: str):
    cursor = dblink().cursor()
    #查询数量
    cursor.execute("""
    SELECT COUNT(*) FROM operators;""")
    count = cursor.fetchone()[0]
    #查询干员信息
    cursor.execute("""
    SELECT {0} FROM operators
    ORDER BY 序号;""".format(column))

    cursor.execute('''
    INSERT INTO public.base_info (id, codename, star, profession, codename_jp, codename_en, add_time, order_id)
    VALUES (DEFAULT, '令', 6, '辅助', NULL, 'Ling', '2022-01-25 16:00:00.000000', NULL);
    '''.format(column))

    column_list = []
    for i in range(count):
        row = cursor.fetchone()[0]
        column_list.append(row)
    return column_list


if __name__ == '__main__':  #测试
    print(pg_query('阿米娅'))