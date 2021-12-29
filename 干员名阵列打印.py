'''
Description: 文件描述
Author: Cyletix
Date: 2021-12-24 15:17:41
LastEditTime: 2021-12-29 11:01:52
FilePath: \Code\GitHub\ArknightsResearch\干员名阵列打印.py
'''
def print_matrix(column):
    from psycopg2 import connect
    arkdb = connect(database="Arknights",
                user="postgres",
                password="shen124357689",
                host="127.0.0.1",
                port="5432")
    cursor = arkdb.cursor()
    #查询数量
    cursor.execute("""
    SELECT COUNT(*) FROM operators;""")
    count = cursor.fetchone()[0]
    #查询所有干员名字
    cursor.execute("""
    SELECT 干员 FROM operators
    ORDER BY 序号;""")
    name_list = []
    col_num = 1
    row_num = 0
    prt_str = ''
    for i in range(count):
        name = cursor.fetchone()[0]
        if name=='斯卡蒂'or name=='浊心斯卡蒂':#排除红蓝蒂
            continue
        elif name=='阿米娅（近卫）':#剑兔别名转换
            name='近卫阿米娅'
        name_list.append(name)
        if col_num == column:
            split_sign = '\n'
            col_num = 0
        else:
            split_sign = '	'
        prt_str += (name + split_sign)
        col_num += 1
        row_num += 1

    print(prt_str)


    with open(r'杂项/干员阵列({}×{}).txt'.format(row_num,column), 'w', encoding='utf-8') as f:
        f.write(prt_str)
    arkdb.close()



if __name__=='__main__':
    column=8 #在此处修改要限制的列数
    print_matrix(column)