'''
Description: 文件描述
Author: Cyletix
Date: 2021-12-24 15:17:41
LastEditTime: 2022-03-27 03:15:59
FilePath: \ArknightsResearch\干员名阵列打印.py
'''


def print_matrix(column):  # 从PostgreSQL获取
    from psycopg2 import connect
    arkdb = connect(database="Arknights",
                    user="postgres",
                    password="shen124357689",
                    host="127.0.0.1",
                    port="5432")
    cursor = arkdb.cursor()
    # 查询数量
    cursor.execute("""
    SELECT COUNT(*) FROM operators;""")
    count = cursor.fetchone()[0]
    # 查询所有干员名字
    cursor.execute("""
    SELECT 干员 FROM operators
    ORDER BY 序号;""")
    name_list = []
    col_num = 1
    row_num = 0
    row = 1
    prt_str = ''
    for i in range(count):
        name = cursor.fetchone()[0]
        if name == '斯卡蒂' or name == '浊心斯卡蒂':  # 排除红蓝蒂
            continue
        elif name == '阿米娅（近卫）':  # 剑兔别名转换
            name = '近卫阿米娅'
        name_list.append(name)
        if col_num == column:
            split_sign = '\n'
            col_num = 0
            row += 1
        else:
            split_sign = '	'
        prt_str += (name + split_sign)
        col_num += 1
        row_num += 1

    print(prt_str)

    with open(r'杂项/干员阵列({}×{}).txt'.format(row, column), 'w', encoding='utf-8') as f:
        f.write(prt_str)
    arkdb.close()


def print_matrix_from_xls(column):  # 从excel获取
    import pandas as pd
    df = pd.read_excel(
        'D:\OneDrive\Code\Github\ArknightsResearch\明日方舟.xlsx', sheet_name='干员信息')
    name_list = list(df['干员'])
    count = len(name_list)
    col_num = 1
    row_num = 0
    row = 1
    prt_str = ''
    add_explain = ''
    for name in name_list:
        # add_explain=' 排除红蓝蒂'
        # if name == '斯卡蒂' or name == '浊心斯卡蒂':  # 排除红蓝蒂
        #     continue
        if name == '阿米娅（近卫）':  # 剑兔别名转换
            name = '近卫阿米娅'
        if col_num == column:
            split_sign = '\n'
            col_num = 0
            row += 1
        else:
            split_sign = '	'
        prt_str += (name + split_sign)
        col_num += 1
        row_num += 1

    with open(r'杂项/干员阵列({0}×{1}-{2}){3}.txt'.format(row, column, count, add_explain), 'w', encoding='utf-8') as f:
        f.write(prt_str)


if __name__ == '__main__':
    column = 10  # 在此处修改要限制的列数
    # print_matrix(column)
    print_matrix_from_xls(column)
