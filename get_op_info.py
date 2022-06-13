'''
Description: 文件描述
Author: Cyletix
Date: 2022-03-17 20:28:30
LastEditTime: 2022-05-09 02:32:00
FilePath: \ArknightsResearch\get_op_info.py
'''
import sys
import pandas as pd
from lxml import etree
import os
global df
# import pg_query as pgq




#这里都是定义的获取单项数据的函数
def get_info(html):  #info
    local_column = ['干员','稀有度', '职业','英文', '上线时间']
    codename = html.xpath('//*[@id="charname"]')[0].text  #干员
    english = html.xpath('//*[@id="charname-en"]')[0].text  #英文
    profession = html.xpath('//*[@id="charclasstxt"]/div/a[1]')[0].text  #职业
    rare = int(html.xpath('//*[@id="rare"]')[0].text) + 1  #稀有度
    try:
        join_time = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="上线时间\n"]/tbody/tr[2]/td')[0].text.strip('\n').replace('年', '-').replace('月','-').replace('日', '')
    except (IndexError):
        join_time = html.xpath('//*[@id="mf-section-2"]/table/tbody/tr[2]/td')[0].text.strip('\n').replace('年', '-').replace('月', '-').replace('日', '')

    # base_info = {}
    # base_info['干员'] = codename
    # base_info['英文'] = english
    # base_info['职业'] = profession
    # base_info['稀有度'] = rare
    # base_info['上线时间'] = join_time

    return local_column, [codename,rare,profession, english, join_time]


def get_attribute(html):  #attribute
    local_column = [
        '部署位',
        '阻挡数',
        '初始部署费用',
        '生命上限',
        '攻击',
        '防御',
        '法术抗性',
        '攻击间隔',
        '再部署时间',
    ]
    try:
        deploy_pos = html.xpath('//*[@id="chartag2"]/div/a')[0].text  #部署位,近战/远程,新增词条
        life = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[3]')[0].text.strip('\n')
        attack = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[3]')[0].text.strip('\n')
        defence = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[3]')[0].text.strip('\n')
        antimagic = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="法术抗性\n"]/tbody/tr[th="法术抗性\n"]/td[3]')[0].text.strip('\n')
        redeploy = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="再部署时间\n"]/tbody/tr[th="初始部署费用\n"]/td[1]')[0].text.strip('\n')
        cost = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="初始部署费用\n"]/tbody/tr[th="初始部署费用\n"]/td[2]')[0].text.strip('\n')
        block = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="阻挡数\n"]/tbody/tr[th="阻挡数\n"]/td[1]')[0].text.strip('\n')
        atk_interval = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击间隔\n"]/tbody/tr[th="攻击间隔\n"]/td[2]')[0].text.strip('\n')
        life_rely = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[5]')[0].text.strip('\n')
        attack_rely = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[5]')[0].text.strip('\n')
        defence_rely = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[5]')[0].text.strip('\n')
    except (IndexError):
        deploy_pos = life = attack = defence = antimagic = redeploy = cost = block = atk_interval = life_rely = attack_rely = defence_rely = None
    if life == '——':  #低星干员空缺情况
        life = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[2]')[0].text.strip('\n')
        attack = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[2]')[0].text.strip('\n')
        defence = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[2]')[0].text.strip('\n')
        antimagic = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="法术抗性\n"]/tbody/tr[th="法术抗性\n"]/td[2]')[0].text.strip('\n')

    #是否计算信赖
    rely_flag = 0
    if rely_flag == 1:
        if life_rely != '':life = str(int(life) + int(life_rely))
        if attack_rely != '':attack = str(int(attack) + int(attack_rely))
        if defence_rely != '':defence = str(int(defence) + int(defence_rely))
        return local_column, [deploy_pos, block, cost, life, attack, defence, antimagic,atk_interval, redeploy
        ]
    elif rely_flag == 0:
        local_column.append('生命信赖加成')
        local_column.append('攻击信赖加成')
        local_column.append('防御信赖加成')
        return local_column, [deploy_pos, block, cost, life, attack, defence, antimagic,atk_interval, redeploy, life_rely, attack_rely, defence_rely
        ]


def get_skill(html):  #skill
    local_column = [
        '技能一初始',
        '技能一消耗',
        '技能一持续',
        '技能二初始',
        '技能二消耗',
        '技能二持续',
        '技能三初始',
        '技能三消耗',
        '技能三持续',
    ]
    try:
        s1_start = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能1")]/following-sibling::table/tbody/tr[9]/td[3]')[0].text.strip('\n')  #技能1
        s1_cost = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能1")]/following-sibling::table/tbody/tr[9]/td[4]')[0].text.strip('\n')  #技能1
        s1_durate = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能1")]/following-sibling::table/tbody/tr[9]/td[5]')[0].text.strip('\n')  #技能1
    except (IndexError):
        s1_start = s1_cost = s1_durate = None
    try:
        s2_start = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能2")]/following-sibling::table/tbody/tr[9]/td[3]')[0].text.strip('\n')  #技能2
        s2_cost = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能2")]/following-sibling::table/tbody/tr[9]/td[4]')[0].text.strip('\n')  #技能2
        s2_durate = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能2")]/following-sibling::table/tbody/tr[9]/td[5]')[0].text.strip('\n')  #技能2
    except (IndexError):
        s2_start = s2_cost = s2_durate = None
    try:
        s3_start = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能3")]/following-sibling::table/tbody/tr[9]/td[3]')[0].text.strip('\n')  #技能3
        s3_cost = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能3")]/following-sibling::table/tbody/tr[9]/td[4]')[0].text.strip('\n')  #技能3
        s3_durate = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能3")]/following-sibling::table/tbody/tr[9]/td[5]')[0].text.strip('\n')  #技能3
    except (IndexError):  #空缺情况
        s3_start = s3_cost = s3_durate = None
    return local_column, [
        s1_start, s1_cost, s1_durate, s2_start, s2_cost, s2_durate, s3_start,
        s3_cost, s3_durate
    ]


def get_potential(html):
    local_column = [
        '潜能2',
        '潜能3',
        '潜能4',
        '潜能5',
        '潜能6',]
    ptt = []
    try:
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[1]')[0].text.strip('\n'))
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[2]')[0].text.strip('\n'))
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[3]')[0].text.strip('\n'))
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[4]')[0].text.strip('\n'))
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[5]')[0].text.strip('\n'))
    except:
        ptt = [None, None, None, None, None]
    return local_column, ptt


#这个是组装函数,调用前面的所有单项函数,把数据拼接起来
def assemble(html):  #没加信赖，后面还得改
    global df
    if 'df' not in globals():#若没有定义df,则上面的声明无效
        columns = get_info(html)[0] + get_attribute(html)[0] + get_skill(html)[0] + get_potential(html)[0]
        df = pd.DataFrame(columns=columns)

    info = get_info(html)[1]
    attribute = get_attribute(html)[1]
    #rely      = get_rely      (html)[1]
    skill = get_skill(html)[1]
    potential = get_potential(html)[1]
    assemble_data = info + attribute + skill + potential
    #df=df.append(dict(zip(columns,assemble_data)), ignore_index=True)
    df.loc[len(df)] = assemble_data  #插入一行list到不同列,可以原封不动执行多次插入多行
    return df


#导出到excel
def result_to_excel():
    from time import strftime,localtime
    now=strftime('%Y-%m-%d %H-%M-%S',localtime())
    save_path = 'result/PRTS爬取结果{0}.xlsx'.format(now)
    if sys.gettrace():  #判断程序是否在终端执行
        # input('Press Enter to save data:')
        pass
    df.to_excel(save_path, index=False)
    if os.path.exists(save_path):  #判断是否保存成功
        print('Saved success!')
        print(save_path)


#插入到sql
def result_to_sql():
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


    '''
        INSERT INTO public.base_info (id, codename, star, profession, codename_jp, codename_en, add_time, order_id)
        VALUES (DEFAULT, '令', 6, '辅助', NULL, 'Ling', '2022-01-25 16:00:00.000000', NULL);
        未完成
    '''
#df.loc[2]['干员']


if __name__ == '__main__':
    codename_list = ['归溟幽灵鲨', '艾丽妮', '流明', '掠风','埃拉托']  #'归溟幽灵鲨', '艾丽妮', '流明', '掠风'
    #codename_list =pgq.pg_query('干员')
    if '阿米娅（近卫）' in codename_list:#对升变阿米娅进行特殊处理
        codename_list[codename_list.index('阿米娅（近卫）')]='阿米娅(近卫)'
    #codename_list=codename_list[codename_list.index('安赛尔'):]#从中间截取位置开始
    
    for codename in codename_list:#干员的循环
        cache_path = 'cache/{} - PRTS - 玩家自由构筑的明日方舟中文Wiki.html'.format(codename)  #缓存路径
        cache_flag = not os.path.isfile(cache_path)  #决定读取方式为缓存或网页爬取
        if len(codename) < 4:prt_split = '\t\t'
        elif len(codename) >= 4:prt_split = '\t'
        #cache_flag = 1  #强制从网页爬取
        if cache_flag:  #从网页爬取并保存为缓存
            wiki_url = 'https://prts.wiki/w/'
            operator_url = wiki_url + codename
            import time 
            from requests import get 
            from requests.models import ChunkedEncodingError
            while (True):
                try:
                    res = get(operator_url)
                    break
                except NameError:
                    time.sleep(60)
                    continue
                except ChunkedEncodingError:
                    time.sleep(60)
                    continue
            res_text = res.text
            html_cache = open(cache_path, 'w', encoding='utf-8')
            html_cache.write(res_text)
            html_cache.close()
            print('{0}{1}网页爬取成功({2}/{3})'.format(
                codename, prt_split,    
            codename_list.index(codename) + 1, len(codename_list)))
            time.sleep(5)
        else:  #从缓存读取
            with open(cache_path, 'r', encoding='utf-8') as f:    
                res_text = f.read()
            print('{0}{1}缓存读取成功({2}/{3})'.format(
                codename, prt_split,
                codename_list.index(codename) + 1, len(codename_list)))
        html = etree.HTML(res_text)
        df = assemble(html)
    df[['上线时间']] = df[['上线时间']].apply(pd.to_datetime)  #修改df单列的数据类型

    # result_to_excel()  #导出到excel
    # result_to_sql()  #插入到sql
