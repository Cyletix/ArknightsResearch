import pandas as pd
from mypgsql import pg_query


def ACfuck(op_num:str,url:str,doctor:str,operator_list:list):
    temp_str1=r'[{0}] ({1}) #{2}'.format(op_num,url,doctor)

    temp_str2=r''
    for i in range(len(operator_list)):
        temp_str2=temp_str2+r'[['+str(operator_list[i])+r']] '

    while temp_str2.strip(' ')[-8:]==r'[[None]]':
        temp_str2=temp_str2.strip(' ')[:-8]

    rt_str=temp_str1+'\n'+temp_str2

    return rt_str


# temp_str2='''[1].(https://www.bilibili.com/video/BV1FZ4y1p7RD). #Au霍乌
# [[凯尔希]] [[None]] [[傀影]] [[泥岩]] [[None]] [[None]] [[None]] [[None]] [[None]] [[None]] [[None]] [[None]] '''




if __name__=='__main__':
    # print('hello')
    # op_num='3+1'
    # url='https://www.bilibili.com/video/BV19b4y1Y7n6?p=16&vd source=e016e29a26a85d1b1271ef1d5063100f'
    # doctor='血白'
    # operator_list=['极境','龙舌兰','伊芙利特']
    # ACfuck(op_num,url,doctor,operator_list)

    sql_list=pg_query("""SELECT * FROM "Arknights"."无精二表";""")

    for i in range(len(sql_list)):
        Stage=sql_list[i][1]
        op_num=sql_list[i][2]
        doctor=sql_list[i][3]
        url=sql_list[i][4]
        operator_list=list(sql_list[i][7:])

        print(ACfuck(op_num,url,doctor,operator_list)+'\n')

        with open(r'result/ACfuck3/{}.md'.format(Stage), 'a', encoding='utf-8') as f:
            f.write(ACfuck(op_num,url,doctor,operator_list)+'\n')

    