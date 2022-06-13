def result_to_sql():
    from psycopg2 import connect
    try:
        arkdb = connect(database="postgres",
                        user="postgres",
                        password="shen124357689",
                        host="127.0.0.1",
                        port="5432")

        column = '生命'

        #筛选要插入的数据
        no_data_operator=[]
        with arkdb.cursor() as curs:
            curs.execute("""SELECT * FROM "Arknights".sd_test;""")
            for record in curs:
                if record[1] is None:
                    no_data_operator.append(record[0])
        print(no_data_operator)


# %%获取表中所有数据
        with arkdb.cursor() as curs:
            curs.execute("""SELECT * FROM "Arknights".sd_test;""")
            rows=curs.fetchall()
        with arkdb.cursor() as curs:
            curs.executemany("""
            UPDATE "Arknights".sd_test
            SET "稀有度" = 6,
                "职业"  = '重装' 
            WHERE "干员" LIKE '泥岩'
            """)




        cursor.execute("""
        INSERT INTO "Arknights".sd_test
        VALUES (%s);
        """%( tuple(df[df['干员']==codename].iloc[0]._values)))


        curs.executemany(
        """INSERT INTO "%s" (data) VALUES (%%s)""" % (args.tableName),op_row)

        op_row=rows[8]
        sql="""INSERT INTO "%s" (data) VALUES (%%s)""" % '"Arknights".sd_test',op_row
        curs.executemany(sql)



        with arkdb.cursor() as curs:
            curs.execute(
                """INSERT INTO %s (data)
                SELECT data FROM Table1
                WHERE lat=-20.004189 AND lon=-63.848004""" % (args.tableName))

        #插入数据
        codename='泥岩'
        df[df['干员']=='泥岩']
        with arkdb.cursor() as curs:
            curs.executemany(
            """INSERT INTO "%s" VALUES (%%s)""" % ('"Arknights".sd_test'),list(df[df['干员']==codename].iloc[0]._values))




            """INSERT INTO "Arknights".sd_test VALUES({})""".format(','.join('%s' for x in list(df.keys())), list(df[df['干员']==codename].iloc[0]._values))
            curs.execute("""INSERT INTO "Arknights".sd_test VALUES({})""".format(','.join('%s' for x in list(df.keys())), list(df[df['干员']==codename].iloc[0]._values)))
            for record in curs:
                print




        #查询数量
        cursor.execute("""
        SELECT COUNT(*) FROM "Arknights".sd_test;""")
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





    finally:
        arkdb.close()#查询完不论如何一定要关闭连接

# %%
if __name__ == '__main__':
    # result_to_sql()
    import pandas as pd 
    df=pd.read_csv(r"D:\OneDrive\Code\GitHub\ArknightsResearch\result\PRTS爬取结果2022-06-12 16-15-52.csv")

    result_to_sql()
# %%
    """INSERT INTO "Arknights".sd_test
    VALUES (%s);"""%



    test_tuple=('不',',','这是两个测试')
    """这是一个测试%%s"""%test_tuple


    codename='泥岩'
    tuple_data=(tuple(df[df['干员']==codename].iloc[0]._values))
    """INSERT INTO "Arknights".sd_test 
    VALUES (%s)""" % tuple_data



    """INSERT INTO "%s" VALUES (%%s)""" % ('"Arknights".sd_test'),tuple(df[df['干员']==codename].iloc[0]._values)


    """INSERT INTO "Arknights".sd_test VALUES({})""".format(','.join('%s' for x in list(df.keys())), list(df[df['干员']==codename].iloc[0]._values))

