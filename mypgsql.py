# 此文件用于连接本地pg数据库,包含敏感信息,一定不要上传到GitHub

def get_tuple():
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
    name_tuple = cursor.fetchall()[0]
    arkdb.close()
    return name_tuple


def result_to_sql():
    from psycopg2 import connect
    try:
        arkdb = connect(database="postgres",
                        user="postgres",
                        password="shen124357689",
                        host="127.0.0.1",
                        port="5432")
        #筛选要插入的数据
        no_data_operator=[]
        with arkdb.cursor() as curs:
            curs.execute("""SELECT * FROM "Arknights".sd_test;""")
            for record in curs:
                if record[1] is None:
                    no_data_operator.append(record[0])
        print(no_data_operator)

        #获取表中所有数据
        with arkdb.cursor() as curs:
            curs.execute("""SELECT * FROM "Arknights".sd_test;""")
            rows=curs.fetchall()
        # with arkdb.cursor() as curs:
        #     curs.executemany("""
        #     UPDATE "Arknights".sd_test
        #     SET "稀有度" = 6,
        #         "职业"  = '重装' 
        #     WHERE "干员" LIKE '泥岩'
        #     """)

        op_row=rows[8]
        sql="""INSERT INTO "%s" (data) VALUES (%%s)""" % '"Arknights".sd_test'
        curs.executemany(sql,op_row)


        #插入数据
        codename='泥岩'
        df[df['干员']=='泥岩']
        with arkdb.cursor() as curs:
            curs.executemany(
            """INSERT INTO "%s" VALUES (%%s)""" % ('"Arknights".sd_test'),list(df[df['干员']==codename].iloc[0]._values))
    finally:
        arkdb.close()#查询完不论如何一定要关闭连接





# get_op_info.py使用的插入到sql
def result_to_sql2():
    from psycopg2 import connect
    arkdb = connect(database="Arknights",user="postgres",password="shen124357689", host="127.0.0.1", port="5432")
    cursor = arkdb.cursor()

    column = '生命'

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



def insertManyRow(strings):
    from psycopg2 import connect
    # 这里就不需要遍历了，因为executemany接受
    try:
        arkdb = connect(database="postgres",
                        user="postgres",
                        password="shen124357689",
                        host="127.0.0.1",
                        port="5432")
        curs = arkdb.cursor()

        sql2 = "INSERT INTO test(干员,稀有度,职业) VALUES(%(text)s,%(num)d,%(text)s)"
        curs.executemany(sql2, strings)
        arkdb.commit()
        arkdb.close()

    except Exception as e:
        print("执行sql时出错：%s" % (e))
        arkdb.rollback()
    finally:
        arkdb.close()


def pandas_sqlalchemy(df):
    from sqlalchemy import create_engine
    engine = create_engine('postgresql://postgres:shen124357689@127.0.0.1:5432/postgres')
    conn = engine.connect()
    df.to_sql(schema = 'Arknights', name='sd2', con=conn, if_exists='append',index=False)
    conn.close()

def search_sql(codename_list):
    from sqlalchemy import create_engine
    engine = create_engine('postgresql://postgres:shen124357689@127.0.0.1:5432/postgres')
    conn = engine.connect()
    sql_list=conn.execute("""SELECT "干员" FROM "Arknights".sd;""").all()
    sql_list=[a[0] for a in sql_list]
    valid_list = [a for a in codename_list if a not in sql_list]
    return valid_list


def pg_query(query_str):
    from sqlalchemy import create_engine
    engine = create_engine('postgresql://postgres:shen124357689@127.0.0.1:5432/postgres')
    conn = engine.connect()
    sql_result=conn.execute(query_str).all()
    return sql_result



#2021-12-24 14:35:31 写的垃圾代码,查询本地数据库中 所有干员的 指定单列信息，按序号排列，以list形式返回结果
# class pg_connect():
#     from psycopg2 import connect
#     # def dblink():
#     # def __init__(self) -> None:
#     arkdb = connect(database="Arknights",user="postgres",password="shen124357689",host="127.0.0.1",port="5432")

#     # 查询某字段
#     def query(self,column: str):
#         cursor = arkdb.cursor()
#         #查询数量
#         cursor.execute("""
#         SELECT COUNT(*) FROM operators;""")
#         count = cursor.fetchone()[0]
#         #查询干员信息
#         cursor.execute("""
#         SELECT {0} FROM operators
#         ORDER BY 序号;""".format(column))

#         column_list = []
#         for i in range(count):
#             row = cursor.fetchone()[0]
#             column_list.append(row)

#         return column_list

#     # 插入
#     def insert(column: str):
#         cursor = arkdb.cursor()
#         #查询数量
#         cursor.execute("""
#         SELECT COUNT(*) FROM operators;""")
#         count = cursor.fetchone()[0]
#         #查询干员信息
#         cursor.execute("""
#         SELECT {0} FROM operators
#         ORDER BY 序号;""".format(column))

#         cursor.execute('''
#         INSERT INTO public.base_info (id, codename, star, profession, codename_jp, codename_en, add_time, order_id)
#         VALUES (DEFAULT, '令', 6, '辅助', NULL, 'Ling', '2022-01-25 16:00:00.000000', NULL);
#         '''.format(column))

#         column_list = []
#         for i in range(count):
#             row = cursor.fetchone()[0]
#             column_list.append(row)
#         return column_list

#     # 自由查询
#     def execute(sql_str: str):
#         cursor = arkdb.cursor()
#         cursor.execute("{}".format(sql_str))





if __name__ == '__main__':
    codename_list2=['黑键','白垩']


    # result_to_sql()
    import pandas as pd
    df=pd.read_csv(r"D:\OneDrive\Code\GitHub\ArknightsResearch\result\PRTS爬取结果2022-06-12 16-15-52.csv")
    codename='泥岩'


# result_to_sql()
    a="""INSERT INTO "Arknights".sd_test({0}) VALUES({1})""".format(
        ','.join('\"%s\"'%x for x in list(df.keys())), 
        ','.join('\'%s\''%x for x in df[df['干员']==codename].iloc[0].tolist()))
    result_to_sql()

        
# insertManyRow()
    # 第一种：strings可以是
    strings = {'干员': '泥岩', '稀有度': 6}

    # curs.executemany("INSERT INTO test VALUES ( %(text)s,%(num)d)", strings)
    
    # # 第二种：strings可以是，我测试的时候是第二种速度更快，但是应该没有快多少
    # strings = [['泥岩','干员'],[6,'稀有度']]
    # sql2 = "INSERT INTO \"Arknights\".sd_test(干员,稀有度) VALUES(%s,%s)"
    # curs.executemany(sql2,strings)

    # curs.executemany('INSERT INTO \"Arknights\".sd_test(干员,稀有度,职业) VALUES(%s,%d,%s)',strings)



    # #成功
    # curs.execute("""INSERT INTO "Arknights".sd_test("干员","稀有度","职业") VALUES('测试干员1',7,'程序员')""")
    # arkdb.commit()

    # #测试一下tuple能否成功
    # curs.execute("""INSERT INTO "Arknights".sd_test("干员","稀有度","职业") VALUES('测试干员1',7,'程序员')""")
    # arkdb.commit()



    # title=df.columns.to_list()
    # strings=df[df['干员']=='泥岩'].iloc[0].tolist()
    # sql = "INSERT INTO \"Arknights\".sd_test VALUES(%s)"
    # curs.executemany(sql,strings)
    # arkdb.commit()


    # insertManyRow(string)



    #     arkdb=pg_connect()
    # arkdb.query('SELECT * FROM "Arknights".source_data')
    # # print(pg_query('阿米娅'))