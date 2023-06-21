'''
Description: 文件描述
Author: Cyletix
Date: 2021-12-12 22:59:12
LastEditTime: 2021-12-27 11:03:40
FilePath: \ArknightsResearch\get_op_info_test.py
'''
import pandas as pd
from lxml import etree
import os
import pg_query as pgq
import time
global df



def get_info(html):#info
    local_column=['干员','英文']
    name = html.xpath('//*[@id="charname"]')[0].text  #干员
    english = html.xpath('//*[@id="charname-en"]')[0].text  #英文
    return local_column,[name, english]

def get_attribute(html):#attribute
    local_column=[
        '部署位',
        '阻挡数',
        '初始部署费用',
        '生命上限',
        '攻击',
        '防御',
        '法术抗性',
        '攻击间隔',
        '再部署时间',]
    #try:
    #    deploy_pos = html.xpath('//*[@id="chartag2"]/div/a')[0].text  #部署位,近战/远程,新增词条
    #    block        = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[2]/td[1]')[0].text[:-1]  #阻挡数
    #    cost         = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[1]/td[2]')[0].text[:-1]  #初始部署费用
    #    life         = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[2]/td[3]')[0].text[:-1]  #生命上限
    #    attack       = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[3]/td[3]')[0].text[:-1]  #攻击
    #    defence      = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[4]/td[3]')[0].text[:-1]  #防御
    #    antimagic    = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[5]/td[3]')[0].text[:-1]  #法术抗性
    #    atk_interval = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[2]/td[2]')[0].text[:-2]  #攻击间隔
    #    redeploy     = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[1]/td[1]')[0].text[:-2]  #再部署时间
    #except(IndexError):
    #    deploy_pos = html.xpath('//*[@id="chartag2"]/div/a')[0].text  #部署位,近战/远程,新增词条
    #    block        = html.xpath('//*[@id="mf-section-3"]/table[1]/tbody/tr[2]/td[1]')[0].text[:-1]
    #    cost         = html.xpath('//*[@id="mf-section-3"]/table[1]/tbody/tr[1]/td[2]')[0].text[:-1]
    #    life         = html.xpath('//*[@id="mf-section-3"]/table[2]/tbody/tr[2]/td[3]')[0].text[:-1]
    #    attack       = html.xpath('//*[@id="mf-section-3"]/table[2]/tbody/tr[3]/td[3]')[0].text[:-1]
    #    defence      = html.xpath('//*[@id="mf-section-3"]/table[2]/tbody/tr[4]/td[3]')[0].text[:-1]
    #    antimagic    = html.xpath('//*[@id="mf-section-3"]/table[2]/tbody/tr[5]/td[3]')[0].text[:-1]
    #    atk_interval = html.xpath('//*[@id="mf-section-3"]/table[1]/tbody/tr[2]/td[2]')[0].text[:-2]
    #    redeploy     = html.xpath('//*[@id="mf-section-3"]/table[1]/tbody/tr[1]/td[1]')[0].text[:-2]
    #except(IndexError):
    try:
        deploy_pos = html.xpath('//*[@id="chartag2"]/div/a')[0].text  #部署位,近战/远程,新增词条
        life         = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[3]')[0].text[:-1]
        attack       = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[3]')[0].text[:-1]
        defence      = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[3]')[0].text[:-1]
        antimagic    = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="法术抗性\n"]/tbody/tr[th="法术抗性\n"]/td[3]')[0].text[:-1]
        redeploy     = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="再部署时间\n"]/tbody/tr[th="初始部署费用\n"]/td[1]')[0].text[:-1]
        cost         = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="初始部署费用\n"]/tbody/tr[th="初始部署费用\n"]/td[2]')[0].text[:-1]
        block        = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="阻挡数\n"]/tbody/tr[th="阻挡数\n"]/td[1]')[0].text[:-1]
        atk_interval = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击间隔\n"]/tbody/tr[th="攻击间隔\n"]/td[2]')[0].text[:-1]
        life_rely    = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[5]')[0].text[:-1]
        attack_rely  = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[5]')[0].text[:-1]
        defence_rely = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[5]')[0].text[:-1]
    except(IndexError):
        deploy_pos = html.xpath('//*[@id="chartag2"]/div/a')[0].text  #部署位,近战/远程,新增词条
        block        = html.xpath('//*[@id="mf-section-3"]/table[1]/tbody/tr[2]/td[1]')[0].text[:-1]
        cost         = html.xpath('//*[@id="mf-section-3"]/table[1]/tbody/tr[1]/td[2]')[0].text[:-1]
        life         = html.xpath('//*[@id="mf-section-3"]/table[2]/tbody/tr[2]/td[3]')[0].text[:-1]
        attack       = html.xpath('//*[@id="mf-section-3"]/table[2]/tbody/tr[3]/td[3]')[0].text[:-1]
        defence      = html.xpath('//*[@id="mf-section-3"]/table[2]/tbody/tr[4]/td[3]')[0].text[:-1]
        antimagic    = html.xpath('//*[@id="mf-section-3"]/table[2]/tbody/tr[5]/td[3]')[0].text[:-1]
        atk_interval = html.xpath('//*[@id="mf-section-3"]/table[1]/tbody/tr[2]/td[2]')[0].text[:-2]
        redeploy     = html.xpath('//*[@id="mf-section-3"]/table[1]/tbody/tr[1]/td[1]')[0].text[:-2]
        life_rely    = html.xpath('//*[@id="mf-section-3"]/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[5]')[0].text[:-1]
        attack_rely  = html.xpath('//*[@id="mf-section-3"]/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[5]')[0].text[:-1]
        defence_rely = html.xpath('//*[@id="mf-section-3"]/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[5]')[0].text[:-1]
    if life=='——':
        life         = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[2]')[0].text[:-1]
        attack       = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[2]')[0].text[:-1]
        defence      = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[2]')[0].text[:-1]
        antimagic    = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="法术抗性\n"]/tbody/tr[th="法术抗性\n"]/td[2]')[0].text[:-1]
    #计算信赖
    if life_rely!='':
        life=str(int(life)+int(life_rely))
    if attack_rely!='':
        attack=str(int(attack)+int(attack_rely))
    if defence_rely!='':
        defence=str(int(defence)+int(defence_rely))    
    return local_column,[deploy_pos,block,cost,life,attack,defence,antimagic,atk_interval,redeploy]

#def get_rely(html):
#    local_column=[
#        '信赖生命加成',
#        '信赖攻击加成',
#        '信赖防御加成',]
#    try:
#        life_rely    = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[5]')[0].text[:-1]
#        attack_rely  = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[5]')[0].text[:-1]
#        defence_rely = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[5]')[0].text[:-1]
#    except(IndexError):
#        life_rely    = html.xpath('//*[@id="mf-section-3"]/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[5]')[0].text[:-1]
#        attack_rely  = html.xpath('//*[@id="mf-section-3"]/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[5]')[0].text[:-1]
#        defence_rely = html.xpath('//*[@id="mf-section-3"]/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[5]')[0].text[:-1]
#    return local_column,[life_rely,attack_rely,defence_rely]

def get_skill(html):#skill
    local_column=[
        '技能一初始',
        '技能一消耗',
        '技能一持续',
        '技能二初始',
        '技能二消耗',
        '技能二持续',
        '技能三初始',
        '技能三消耗',
        '技能三持续',]
    #    s1_start  = html.xpath('//*[@id="mw-content-text"]/div/table[10]/tbody/tr[9]/td[3]')[0].text[:-1]  #s1初动
    #    s1_cost   = html.xpath('//*[@id="mw-content-text"]/div/table[10]/tbody/tr[9]/td[4]')[0].text[:-1]  #s1消耗
    #    s1_durate = html.xpath('//*[@id="mw-content-text"]/div/table[10]/tbody/tr[9]/td[5]')[0].text[:-1]  #s1持续
    #except(IndexError):
    #    s1_start  = html.xpath('//*[@id="mf-section-7"]/table[1]/tbody/tr[9]/td[3]')[0].text[:-1]
    #    s1_cost   = html.xpath('//*[@id="mf-section-7"]/table[1]/tbody/tr[9]/td[4]')[0].text[:-1]
    #    s1_durate = html.xpath('//*[@id="mf-section-7"]/table[1]/tbody/tr[9]/td[5]')[0].text[:-1]
    #except(IndexError):
    try:
        s1_start  = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能1")]/following-sibling::table/tbody/tr[9]/td[3]')[0].text[:-1]#技能1
        s1_cost   = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能1")]/following-sibling::table/tbody/tr[9]/td[4]')[0].text[:-1]#技能1
        s1_durate = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能1")]/following-sibling::table/tbody/tr[9]/td[5]')[0].text[:-1]#技能1
    except(IndexError):
        try:
            s1_start  = html.xpath('//*[@id="mf-section-7"]/table[1]/tbody/tr[9]/td[3]')[0].text[:-1]
            s1_cost   = html.xpath('//*[@id="mf-section-7"]/table[1]/tbody/tr[9]/td[4]')[0].text[:-1]
            s1_durate = html.xpath('//*[@id="mf-section-7"]/table[1]/tbody/tr[9]/td[5]')[0].text[:-1]
        except:#空缺情况
            s1_start=s1_cost=s1_durate=None

    #    s2_start  = html.xpath('//*[@id="mw-content-text"]/div/table[12]/tbody/tr[9]/td[3]')[0].text[:-1]
    #    s2_cost   = html.xpath('//*[@id="mw-content-text"]/div/table[12]/tbody/tr[9]/td[4]')[0].text[:-1]
    #    s2_durate = html.xpath('//*[@id="mw-content-text"]/div/table[12]/tbody/tr[9]/td[5]')[0].text[:-1]
    #except(IndexError):
    #    s2_start  = html.xpath('//*[@id="mf-section-7"]/table[2]/tbody/tr[9]/td[3]')[0].text[:-1]
    #    s2_cost   = html.xpath('//*[@id="mf-section-7"]/table[2]/tbody/tr[9]/td[4]')[0].text[:-1]
    #    s2_durate = html.xpath('//*[@id="mf-section-7"]/table[2]/tbody/tr[9]/td[5]')[0].text[:-1]
    #except(IndexError):
    try:
        s2_start  = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能2")]/following-sibling::table/tbody/tr[9]/td[3]')[0].text[:-1]#技能2
        s2_cost   = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能2")]/following-sibling::table/tbody/tr[9]/td[4]')[0].text[:-1]#技能2
        s2_durate = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能2")]/following-sibling::table/tbody/tr[9]/td[5]')[0].text[:-1]#技能2
    except(IndexError):
        try:
            s2_start  = html.xpath('//*[@id="mf-section-7"]/table[2]/tbody/tr[9]/td[3]')[0].text[:-1]
            s2_cost   = html.xpath('//*[@id="mf-section-7"]/table[2]/tbody/tr[9]/td[4]')[0].text[:-1]
            s2_durate = html.xpath('//*[@id="mf-section-7"]/table[2]/tbody/tr[9]/td[5]')[0].text[:-1]
        except:#空缺情况
            s2_start=s2_cost=s2_durate=None

    #    s3_start  = html.xpath('//*[@id="mw-content-text"]/div/table[14]/tbody/tr[9]/td[3]')[0].text[:-1]
    #    s3_cost   = html.xpath('//*[@id="mw-content-text"]/div/table[14]/tbody/tr[9]/td[4]')[0].text[:-1]
    #    s3_durate = html.xpath('//*[@id="mw-content-text"]/div/table[14]/tbody/tr[9]/td[5]')[0].text[:-1]
    #except(IndexError):
    #    s3_start  = html.xpath('//*[@id="mf-section-7"]/table[3]/tbody/tr[9]/td[3]')[0].text[:-1]
    #    s3_cost   = html.xpath('//*[@id="mf-section-7"]/table[3]/tbody/tr[9]/td[4]')[0].text[:-1]
    #    s3_durate = html.xpath('//*[@id="mf-section-7"]/table[3]/tbody/tr[9]/td[5]')[0].text[:-1]
    try:
        s3_start  = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能3")]/following-sibling::table/tbody/tr[9]/td[3]')[0].text[:-1]#技能3
        s3_cost   = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能3")]/following-sibling::table/tbody/tr[9]/td[4]')[0].text[:-1]#技能3
        s3_durate = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能3")]/following-sibling::table/tbody/tr[9]/td[5]')[0].text[:-1]#技能3
    except(IndexError):
        try:
            s3_start  = html.xpath('//*[@id="mf-section-7"]/table[3]/tbody/tr[9]/td[3]')[0].text[:-1]
            s3_cost   = html.xpath('//*[@id="mf-section-7"]/table[3]/tbody/tr[9]/td[4]')[0].text[:-1]
            s3_durate = html.xpath('//*[@id="mf-section-7"]/table[3]/tbody/tr[9]/td[5]')[0].text[:-1]
        except(IndexError):#空缺情况
            s3_start=s3_cost=s3_durate=None
    return local_column,[s1_start,s1_cost,s1_durate,s2_start,s2_cost,s2_durate,s3_start,s3_cost,s3_durate]

def get_potential(html):
    local_column=[
        '潜能2',
        '潜能3',
        '潜能4',
        '潜能5',
        '潜能6',]
    ptt=[]
    try:
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[1]')[0].text[:-1])
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[2]')[0].text[:-1])
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[3]')[0].text[:-1])
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[4]')[0].text[:-1])
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[5]')[0].text[:-1])
    except(IndexError):
        ptt.append(html.xpath('//*[@id="mf-section-6"]/table/tbody/tr[1]/td')[0].text[:-1])
        ptt.append(html.xpath('//*[@id="mf-section-6"]/table/tbody/tr[2]/td')[0].text[:-1])
        ptt.append(html.xpath('//*[@id="mf-section-6"]/table/tbody/tr[3]/td')[0].text[:-1])
        ptt.append(html.xpath('//*[@id="mf-section-6"]/table/tbody/tr[4]/td')[0].text[:-1])
        ptt.append(html.xpath('//*[@id="mf-section-6"]/table/tbody/tr[5]/td')[0].text[:-1])
    except(TypeError):
        ptt=[None,None,None,None,None]
    return local_column,ptt

def assemble(name, html):#没加信赖，后面还得改
    global df
    if 'df' not in globals():
        columns=get_info(html)[0]+get_attribute(html)[0]+get_skill(html)[0]+get_potential(html)[0]
        df = pd.DataFrame(columns=columns)
    info      = get_info      (html)[1]
    attribute = get_attribute (html)[1]
    #rely      = get_rely      (html)[1]
    skill     = get_skill     (html)[1]
    potential = get_potential (html)[1]
    assemble_data  = info + attribute + skill +potential
    #df=df.append(dict(zip(columns,assemble_data)), ignore_index=True)
    df.loc[len(df)] = assemble_data#插入一行list到不同列,可以原封不动执行多次插入多行
    return df

if __name__ == '__main__':
    #name_list = ['灵知', '极光', '耶拉']
    name_list =pgq.pg_query('干员')
    name_list[name_list.index('阿米娅（近卫）')]='阿米娅(近卫)'
    save_path='result/wiki爬取干员信息6.xlsx'
    for name in name_list:
        cache_path='cache/html_cache_{}.html'.format(name)#缓存路径
        cache_flag=not os.path.isfile(cache_path)
        #cache_flag=False
        if cache_flag:#从网页爬取并保存为缓存
            wiki_url = 'https://prts.wiki/w/'
            operator_url = wiki_url + name
            import time
            from requests import get
            from requests.models import ChunkedEncodingError
            while(True):
                try:
                    res = get(operator_url)
                    break
                except NameError:
                    time.sleep(60)
                    continue
                except ChunkedEncodingError:
                    time.sleep(60)
                    continue
            res_text=res.text
            html_cache = open(cache_path, 'w', encoding='utf-8')
            html_cache.write(res_text)
            html_cache.close()
            print('{0}\t网页爬取成功({1}/{2})'.format(name,name_list.index(name)+1,len(name_list)))
            time.sleep(5)
        else:#从缓存读取
            with open(cache_path,'r',encoding='utf-8') as f:
                res_text=f.read()
            print('{0}\t缓存读取成功({1}/{2})'.format(name,name_list.index(name)+1,len(name_list)))
        html = etree.HTML(res_text)
        df=assemble(name, html)
    df.to_excel(save_path,index=False)


# columns=[  #这里设置字段
#        #info
#        '代号',
#        '英语',
#        #attribute
#        '部署位',
#        '阻挡数',
#        '初始部署费用',
#        '生命上限',
#        '攻击',
#        '防御',
#        '法术抗性',
#        '攻击间隔',
#        '再部署时间',
#        #skill
#        '技能一初始',
#        '技能一消耗',
#        '技能一持续',
#        '技能二初始',
#        '技能二消耗',
#        '技能二持续',
#        '技能三初始',
#        '技能三消耗',
#        '技能三持续',
#        #potantial
#        '潜能2',
#        '潜能3',
#        '潜能4',
#        '潜能5',
#        '潜能6',]


##网页第一次
#html.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr[1]/td[2]')[0].text[:-1]

##网页第二次
#html.xpath('//*[@id="mf-section-3"]/table[1]/tbody/tr[2]/td[1]')[0].text[:-1]

##网页第三次/本地网页:(目前生效)
#html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[2]/td[1]')[0].text[:-1]

#html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/td[3]="7\n"]/tbody/tr[td[1]="7\n"]/td[3]')[0].text[:-1]


##自定义
#html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="再部署时间\n"]/tbody/tr[th="初始部署费用\n"]/td[1]')[0].text[:-1]
#html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="初始部署费用\n"]/tbody/tr[th="初始部署费用\n"]/td[2]')[0].text[:-1]
#html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="阻挡数\n"]/tbody/tr[th="阻挡数\n"]/td[1]')[0].text[:-1]
#html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击间隔\n"]/tbody/tr[th="攻击间隔\n"]/td[2]')[0].text[:-1]


##网页
#html.xpath('//*[@id="mw-content-text"]/div/table[11]/tbody/tr[2]/th[3]/span/span/text()')[0].text[:-1]
#html.xpath('//*[@id="mw-content-text"]/div/p[7]/b')[0].text[:-1]#技能1
#html.xpath('//*[@id="mw-content-text"]/div/p[8]/b')[0].text[:-1]#技能2
#html.xpath('//*[@id="mw-content-text"]/div/p[9]/b')[0].text[:-1]#技能3


##缓存
#html.xpath('//*[@id="mw-content-text"]/div/p[b="技能1（精英0开放）"]/following-sibling::table/tbody/tr[9]/td[3]')[0].text[:-1]#技能1
#html.xpath('//*[@id="mw-content-text"]/div/p[b="技能1（精英0开放）"]/following-sibling::table/tbody/tr[9]/td[4]')[0].text[:-1]#技能1
#html.xpath('//*[@id="mw-content-text"]/div/p[b="技能1（精英0开放）"]/following-sibling::table/tbody/tr[9]/td[5]')[0].text[:-1]#技能1


#html.xpath('')[0].text[:-1]

##following-sibling::table[1]


#df = pd.DataFrame(columns=list("ABC"))
#df.loc[len(df)] = [1,4,3]
