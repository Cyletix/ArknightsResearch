import requests
import pandas as pd


def get_info(html):
    name = html.xpath('//*[@id="charname"]')[0].text  #干员
    english = html.xpath('//*[@id="charname-en"]')[0].text  #英文
    return [name, english]

def get_attribute(html):
    position = html.xpath('//*[@id="chartag2"]/div/a')[0].text  #部署位,近战/远程,新增词条
    block = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[2]/td[1]')[0].text[:-1]  #阻挡数
    cost = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[1]/td[2]')[0].text[:-1]  #初始部署费用
    life = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[2]/td[3]')[0].text[:-1]  #生命上限
    attack = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[3]/td[3]')[0].text[:-1]  #攻击
    defence = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[4]/td[3]')[0].text[:-1]  #防御
    antimagic = html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[5]/td[3]')[0].text[:-1]  #法术抗性
    atk_interval = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[2]/td[2]')[0].text[:-2]  #攻击间隔
    redeploy = html.xpath('//*[@id="mw-content-text"]/div/table[2]/tbody/tr[1]/td[1]')[0].text[:-2]  #再部署时间
    return [position,block,cost,life,attack,defence,antimagic,atk_interval,redeploy]

def get_rely(html):
    life_rely= html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[2]/td[5]')[0].text[:-1]
    attack_rely= html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[3]/td[5]')[0].text[:-1]
    defence_rely= html.xpath('//*[@id="mw-content-text"]/div/table[3]/tbody/tr[4]/td[5]')[0].text[:-1]
    return [life_rely,attack_rely,defence_rely]

def get_skill(html):
    try:s1_start = html.xpath('//*[@id="mw-content-text"]/div/table[10]/tbody/tr[9]/td[3]')[0].text[:-1]  #初动
    except IndexError:s1_start='NULL'
    try:s1_cost = html.xpath('//*[@id="mw-content-text"]/div/table[10]/tbody/tr[9]/td[4]')[0].text[:-1]  #消耗
    except IndexError:s1_cost='NULL'
    try:s1_durate = html.xpath('//*[@id="mw-content-text"]/div/table[10]/tbody/tr[9]/td[5]')[0].text[:-1]  #持续
    except IndexError:s1_durate='NULL'
    try:s2_start = html.xpath('//*[@id="mw-content-text"]/div/table[12]/tbody/tr[9]/td[3]')[0].text[:-1]
    except IndexError:s2_start='NULL'
    try:s2_cost = html.xpath('//*[@id="mw-content-text"]/div/table[12]/tbody/tr[9]/td[4]')[0].text[:-1]
    except IndexError:s2_cost='NULL'
    try:s2_durate = html.xpath('//*[@id="mw-content-text"]/div/table[12]/tbody/tr[9]/td[5]')[0].text[:-1]
    except IndexError:s2_durate='NULL'
    try:s3_start = html.xpath('//*[@id="mw-content-text"]/div/table[14]/tbody/tr[9]/td[3]')[0].text[:-1] 
    except IndexError:s3_start='NULL'
    try:s3_cost = html.xpath('//*[@id="mw-content-text"]/div/table[14]/tbody/tr[9]/td[4]')[0].text[:-1]
    except IndexError:s3_cost='NULL'
    try:s3_durate = html.xpath('//*[@id="mw-content-text"]/div/table[14]/tbody/tr[9]/td[5]')[0].text[:-1]
    except IndexError:s3_durate='NULL'
    return [s1_start,s1_cost,s1_durate,s2_start,s2_cost,s2_durate,s3_start,s3_cost,s3_durate]

def assemble(name, html):#没加信赖，后面还得改
    info = get_info(html)
    attribute = get_attribute(html)
    skill = get_skill(html)
    assemble = info + attribute + skill  #+dps+statistics
    return assemble

if __name__ == '__main__':
    name_list = ['灵知', '极光', '耶拉']
    columns=[  #这里设置字段
        #info
        '代号',
        '英语',
        #attribute
        '部署位',
        '阻挡数',
        '初始部署费用',
        '生命上限',
        '攻击',
        '防御',
        '法术抗性',
        '攻击间隔',
        '再部署时间',
        #skill
        '技能一初始',
        '技能一消耗',
        '技能一持续',
        '技能二初始',
        '技能二消耗',
        '技能二持续',
        '技能三初始',
        '技能三消耗',
        '技能三持续',]
    df = pd.DataFrame(columns=columns)

    for name in name_list:
        # name = name_list[0]
        from lxml import etree
        wiki_url = 'https://prts.wiki/w/'
        operator_url = wiki_url + name
        res = requests.get(operator_url)
        html = etree.HTML(res.text)
        
        # print(get_info(html))
        # print(get_attribute(html))
        # print(get_rely(html))
        # print(get_skill(html))
        # print(assemble(name, html))
        assemble(name, html)
        df = df.append(assemble(name, html), ignore_index=True)#这里有问题，插入的是转置的
    df.to_excel('杂项/wiki爬取干员信息5.xlsx',index=False)