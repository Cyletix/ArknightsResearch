import pandas as pd
from lxml import etree
import os
import pg_query as pgq
global df



def get_info(html):#info
    local_column=['干员','英文','上线时间']
    codename = html.xpath('//*[@id="charname"]')[0].text  #干员
    english = html.xpath('//*[@id="charname-en"]')[0].text  #英文
    join_time = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="上线时间\n"]/tbody/tr[2]/td')[0].text.strip('\n').replace('年','-').replace('月','-').replace('日','')
    return local_column,[codename, english, join_time]

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
    try:
        deploy_pos   = html.xpath('//*[@id="chartag2"]/div/a')[0].text  #部署位,近战/远程,新增词条
        life         = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[3]')[0].text.strip('\n')
        attack       = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[3]')[0].text.strip('\n')
        defence      = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[3]')[0].text.strip('\n')
        antimagic    = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="法术抗性\n"]/tbody/tr[th="法术抗性\n"]/td[3]')[0].text.strip('\n')
        redeploy     = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="再部署时间\n"]/tbody/tr[th="初始部署费用\n"]/td[1]')[0].text.strip('\n')
        cost         = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="初始部署费用\n"]/tbody/tr[th="初始部署费用\n"]/td[2]')[0].text.strip('\n')
        block        = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="阻挡数\n"]/tbody/tr[th="阻挡数\n"]/td[1]')[0].text.strip('\n')
        atk_interval = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击间隔\n"]/tbody/tr[th="攻击间隔\n"]/td[2]')[0].text.strip('\n')
        life_rely    = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[5]')[0].text.strip('\n')
        attack_rely  = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[5]')[0].text.strip('\n')
        defence_rely = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[5]')[0].text.strip('\n')
    except(IndexError):
        deploy_pos = life = attack = defence = antimagic = redeploy = cost = block = atk_interval = life_rely = attack_rely = defence_rely = None
    if life=='——':
        life         = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="生命上限\n"]/tbody/tr[th="生命上限\n"]/td[2]')[0].text.strip('\n')
        attack       = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="攻击\n"]/tbody/tr[th="攻击\n"]/td[2]')[0].text.strip('\n')
        defence      = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="防御\n"]/tbody/tr[th="防御\n"]/td[2]')[0].text.strip('\n')
        antimagic    = html.xpath('//*[@id="mw-content-text"]/div/table[tbody/tr/th="法术抗性\n"]/tbody/tr[th="法术抗性\n"]/td[2]')[0].text.strip('\n')
    #计算信赖
    if life_rely!='':
        life=str(int(life)+int(life_rely))
    if attack_rely!='':
        attack=str(int(attack)+int(attack_rely))
    if defence_rely!='':
        defence=str(int(defence)+int(defence_rely))
    return local_column,[deploy_pos,block,cost,life,attack,defence,antimagic,atk_interval,redeploy]
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
    try:
        s1_start  = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能1")]/following-sibling::table/tbody/tr[9]/td[3]')[0].text.strip('\n')#技能1
        s1_cost   = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能1")]/following-sibling::table/tbody/tr[9]/td[4]')[0].text.strip('\n')#技能1
        s1_durate = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能1")]/following-sibling::table/tbody/tr[9]/td[5]')[0].text.strip('\n')#技能1
    except(IndexError):
        s1_start=s1_cost=s1_durate=None
    try:
        s2_start  = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能2")]/following-sibling::table/tbody/tr[9]/td[3]')[0].text.strip('\n')#技能2
        s2_cost   = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能2")]/following-sibling::table/tbody/tr[9]/td[4]')[0].text.strip('\n')#技能2
        s2_durate = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能2")]/following-sibling::table/tbody/tr[9]/td[5]')[0].text.strip('\n')#技能2
    except(IndexError):
        s2_start=s2_cost=s2_durate=None
    try:
        s3_start  = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能3")]/following-sibling::table/tbody/tr[9]/td[3]')[0].text.strip('\n')#技能3
        s3_cost   = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能3")]/following-sibling::table/tbody/tr[9]/td[4]')[0].text.strip('\n')#技能3
        s3_durate = html.xpath('//*[@id="mw-content-text"]/div/p[contains(b,"技能3")]/following-sibling::table/tbody/tr[9]/td[5]')[0].text.strip('\n')#技能3
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
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[1]')[0].text.strip('\n'))
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[2]')[0].text.strip('\n'))
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[3]')[0].text.strip('\n'))
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[4]')[0].text.strip('\n'))
        ptt.append(html.xpath('//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/td[5]')[0].text.strip('\n'))
    except:
        ptt=[None,None,None,None,None]
    return local_column,ptt

def assemble(name, html):#没加信赖，后面还得改
    global df
    if 'df' not in globals():
        columns=get_info(html)[0]+get_attribute(html)[0]+get_skill(html)[0]+get_potential(html)[0]
        df = pd.DataFrame(columns=columns)
        
    info      = get_info      (html)[1]
    attribute = get_attribute (html)[1]
    # rely      = get_rely      (html)[1]
    skill     = get_skill     (html)[1]
    potential = get_potential (html)[1]
    assemble_data  = info + attribute + skill +potential
    # df=df.append(dict(zip(columns,assemble_data)), ignore_index=True)
    df.loc[len(df)] = assemble_data#插入一行list到不同列,可以原封不动执行多次插入多行
    return df

if __name__ == '__main__':
    # codename_list=['刻刀']#单项调试
    codename_list =pgq.pg_query('干员')
    codename_list[codename_list.index('阿米娅（近卫）')]='阿米娅(近卫)'
    # codename_list=codename_list[codename_list.index('安赛尔'):]#从此位置开始
    save_path='杂项/wiki爬取干员信息6.xlsx'
    for codename in codename_list:
        cache_path='cache/html_cache_{}.html'.format(codename)#缓存路径
        cache_flag=not os.path.isfile(cache_path)
        if len(codename)<4:
            prt_split='\t\t'
        elif len(codename)>=4:
            prt_split='\t'
        if cache_flag:#从网页爬取并保存为缓存
            wiki_url = 'https://prts.wiki/w/'
            operator_url = wiki_url + codename
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
            print('{0}{1}网页爬取成功({2}/{3})'.format(codename,prt_split,codename_list.index(codename)+1,len(codename_list)))
            time.sleep(5)
        else:#从缓存读取
            with open(cache_path,'r',encoding='utf-8') as f:
                res_text=f.read()
            print('{0}{1}缓存读取成功({2}/{3})'.format(codename,prt_split,codename_list.index(codename)+1,len(codename_list)))
        html = etree.HTML(res_text)
        df=assemble(codename, html)
    df[['上线时间']] = df[['上线时间']].apply(pd.to_datetime)#修改df单列的数据类型
    input('Press Enter to save data:')
    df.to_excel(save_path,index=False)