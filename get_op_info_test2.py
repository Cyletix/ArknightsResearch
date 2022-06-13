'''
Description: 文件描述
Author: Cyletix
Date: 2022-03-17 20:28:30
LastEditTime: 2022-05-09 02:32:00
FilePath: \ArknightsResearch\get_op_info.py
'''
from ast import keyword
import sys
import pandas as pd
from lxml import etree
import os
import re
from datetime import datetime
# import pg_query as pgq

global data_dict,codename,failed_list
failed_list=[]


def insert_into_dict(field:str,evaluation):
    try:
        data_dict[field] = evaluation
    except:
        failed_list.append(codename)
        data_dict[field] = None


###########################################################################################
def get_data(html):
    data_dict = {}

    #base_info
    def get_data_by_code(field:str,expresion:str):
        try:
            exec("data_dict[{0}] = {1}".format(field,expresion))
        except:
            failed_list.append(codename)
            data_dict[field] = None
        return data_dict[field]
    # get_data_by_code('干员','''html.xpath('//*[@id="charname"]/text()')[0]''')
    # get_data_by_code('稀有度','''int(html.xpath('//*[@id="rare"]/text()')[0]) + 1''')
    # get_data_by_code('职业','''html.xpath('//*[@id="charclasstxt"]/div/a[1]/text()')[0]''')
    # get_data_by_code('子职业','''html.xpath('//*[@id="charclasstxt"]/div/a[2]/text()')[0]''')
    # get_data_by_code('英文','''html.xpath('//*[@id="charname-en"]/text()')[0] ''')
    # get_data_by_code('上线时间','''datetime.strptime(html.xpath('//table[tbody/tr/th="上线时间\n"]/tbody/tr[2]/td/text()')[0],'%Y年%m月%d日 %H:%M\n').strftime('%Y-%m-%d %H:%M:%S') ''')
    # get_data_by_code('部署位','''html.xpath('//*[@title="近战位" or @title="远程位"]/text()')[0]''')

    data_dict['干员'] = html.xpath('//*[@id="charname"]/text()')[0]  #干员
    data_dict['稀有度'] = int(html.xpath('//*[@id="rare"]/text()')[0]) + 1  #稀有度
    data_dict['职业'] = html.xpath('//*[@id="charclasstxt"]/div/a[1]/text()')[0]  #职业
    data_dict['子职业'] = html.xpath('//*[@id="charclasstxt"]/div/a[2]/text()')[0]
    data_dict['英文'] = html.xpath('//*[@id="charname-en"]/text()')[0]  #英文
    date_str=html.xpath('//table[tbody/tr/th="上线时间\n"]/tbody/tr[2]/td/text()')[0]
    data_dict['上线时间'] = datetime.strptime(date_str,'%Y年%m月%d日 %H:%M\n').strftime('%Y-%m-%d %H:%M:%S') 
    data_dict['部署位'] = html.xpath('//*[@title="近战位" or @title="远程位"]/text()')[0]  #部署位,近战/远程,新增词条
    
    #attribute
    def get_attrubute1(field:str,field_group,expresion:str):
        #获取再部署时间,初始部署费用,阻挡数,攻击间隔
        query_str='//*[@id="mw-content-text"]/div[1]/table[2]/tbody/tr[th="{0}\n" or th="{1}\n"]/{2}/text()'.format(field_group.split('-')[0],field_group.split('-')[1],expresion)
        try:
            data_dict[field] = html.xpath(query_str)[0].strip('\n|s')
        except:
            failed_list.append(codename)
            data_dict[field] = None
        return data_dict[field]
    get_attrubute1('再部署时间','再部署时间-初始部署费用','td[1]')
    get_attrubute1('初始部署费用','再部署时间-初始部署费用','td[2]')
    get_attrubute1('阻挡数','阻挡数-攻击间隔','td[1]')
    get_attrubute1('攻击间隔','阻挡数-攻击间隔','td[2]')
    # data_dict['再部署时间'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[2]/tbody/tr[th="再部署时间\n" or th="初始部署费用\n"]/td[1]/text()')[0].strip('\n|s')
    # data_dict['初始部署费用'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[2]/tbody/tr[th="再部署时间\n" or th="初始部署费用\n"]/td[2]/text()')[0].strip('\n')
    # data_dict['阻挡数'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[2]/tbody/tr[th="阻挡数\n" or th="攻击间隔\n"]/td[1]/text()')[0].strip('\n')
    # data_dict['攻击间隔'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[2]/tbody/tr[th="阻挡数\n" or th="攻击间隔\n"]/td[2]/text()')[0].strip('\n|s')

    def get_attrubute2(field:str,expresion:str):
        #获取生命上限,攻击,防御,法术抗性
        query_str='//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="{0}\n"]/tbody/{1}/text()'.format(field.split('-')[0],expresion)
        try:
            data_dict[field] = html.xpath(query_str)[0].strip('\n')
        except:
            failed_list.append(codename)
            data_dict[field] = None
        return data_dict[field]
    get_attrubute2('生命上限-精英0 1级','tr[2]/td[1]')
    get_attrubute2('生命上限-精英0 满级','tr[2]/td[2]')
    get_attrubute2('生命上限-精英1 满级','tr[2]/td[3]')
    get_attrubute2('生命上限-精英2 满级','tr[2]/td[4]')
    get_attrubute2('生命上限-信赖加成上限','tr[2]/td[5]')

    get_attrubute2('攻击-精英0 1级','tr[3]/td[1]')
    get_attrubute2('攻击-精英0 满级','tr[3]/td[2]')
    get_attrubute2('攻击-精英1 满级','tr[3]/td[3]')
    get_attrubute2('攻击-精英2 满级','tr[3]/td[4]')
    get_attrubute2('攻击-信赖加成上限','tr[3]/td[5]')

    get_attrubute2('防御-精英0 1级','tr[4]/td[1]')
    get_attrubute2('防御-精英0 满级','tr[4]/td[2]')
    get_attrubute2('防御-精英1 满级','tr[4]/td[3]')
    get_attrubute2('防御-精英2 满级','tr[4]/td[4]')
    get_attrubute2('防御-信赖加成上限','tr[4]/td[5]')

    get_attrubute2('法术抗性-精英0 1级','tr[5]/td[1]')
    get_attrubute2('法术抗性-精英0 满级','tr[5]/td[2]')
    get_attrubute2('法术抗性-精英1 满级','tr[5]/td[3]')
    get_attrubute2('法术抗性-精英2 满级','tr[5]/td[4]')
    get_attrubute2('法术抗性-信赖加成上限','tr[5]/td[5]')




#老获取方法,直接获取
    # data_dict['生命上限-精英0 1级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="生命上限\n"]/tbody/tr[2]/td[1]/text()')[0].strip('\n')
    # data_dict['生命上限-精英0 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="生命上限\n"]/tbody/tr[2]/td[2]/text()')[0].strip('\n')
    # data_dict['生命上限-精英1 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="生命上限\n"]/tbody/tr[2]/td[3]/text()')[0].strip('\n')
    # data_dict['生命上限-精英2 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="生命上限\n"]/tbody/tr[2]/td[4]/text()')[0].strip('\n')
    # data_dict['生命上限-信赖加成上限'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="生命上限\n"]/tbody/tr[2]/td[5]/text()')[0].strip('\n')

    # data_dict['攻击-精英0 1级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="攻击\n"]/tbody/tr[3]/td[1]/text()')[0].strip('\n')
    # data_dict['攻击-精英0 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="攻击\n"]/tbody/tr[3]/td[2]/text()')[0].strip('\n')
    # data_dict['攻击-精英1 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="攻击\n"]/tbody/tr[3]/td[3]/text()')[0].strip('\n')
    # data_dict['攻击-精英2 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="攻击\n"]/tbody/tr[3]/td[4]/text()')[0].strip('\n')
    # data_dict['攻击-信赖加成上限'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="攻击\n"]/tbody/tr[3]/td[5]/text()')[0].strip('\n')

    # data_dict['防御-精英0 1级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="防御\n"]/tbody/tr[4]/td[1]/text()')[0].strip('\n')
    # data_dict['防御-精英0 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="防御\n"]/tbody/tr[4]/td[2]/text()')[0].strip('\n')
    # data_dict['防御-精英1 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="防御\n"]/tbody/tr[4]/td[3]/text()')[0].strip('\n')
    # data_dict['防御-精英2 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="防御\n"]/tbody/tr[4]/td[4]/text()')[0].strip('\n')
    # data_dict['防御-信赖加成上限'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="防御\n"]/tbody/tr[4]/td[5]/text()')[0].strip('\n')

    # data_dict['法术抗性-精英0 1级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="法术抗性\n"]/tbody/tr[5]/td[1]/text()')[0].strip('\n')
    # data_dict['法术抗性-精英0 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="法术抗性\n"]/tbody/tr[5]/td[2]/text()')[0].strip('\n')
    # data_dict['法术抗性-精英1 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="法术抗性\n"]/tbody/tr[5]/td[3]/text()')[0].strip('\n')
    # data_dict['法术抗性-精英2 满级'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="法术抗性\n"]/tbody/tr[5]/td[4]/text()')[0].strip('\n')
    # data_dict['法术抗性-信赖加成上限'] = html.xpath('//*[@id="mw-content-text"]/div[1]/table[tbody/tr/th="法术抗性\n"]/tbody/tr[5]/td[5]/text()')[0].strip('\n')


    #skill
    def get_skill(field:str,sk_no:int,expresion:str):
        #获取技能
        
        try:
            data_dict[field] = html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能{0}（精英{1}开放）"]/following-sibling::table[1]/tbody/{2}/text()'.format(str(sk_no),str(sk_no-1),expresion))[0].strip('\n')
        except:
            data_dict[field] = None
        return data_dict[field]

    html.xpath('//*[@id="mw-content-text"]/div[1]/p/b/text()')
#技能1（精英0开放）
    get_skill('技能1 技能名称',1,'tr[1]/td[2]/big')
    get_skill('技能1 回复类型',1,'tr[1]/td[3]/span[1]')
    get_skill('技能1 触发类型',1,'tr[1]/td[3]/span[2]')
    get_skill('技能1 LV7 初始',1,'tr[9]/td[3]')
    get_skill('技能1 LV7 消耗',1,'tr[9]/td[4]')
    get_skill('技能1 LV7 持续',1,'tr[9]/td[5]')

    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[1]/td[2]/big/text()')[0].strip('\n')#技能名称
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[1]/text()')[0].strip('\n')#回复类型
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[2]/text()')[0].strip('\n')#触发类型

    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[3]/td[3]/text()')[0].strip('\n')#技能1 LV1 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[3]/td[4]/text()')[0].strip('\n')#技能1 LV1 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[3]/td[5]/text()')[0].strip('\n')#技能1 LV1 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[4]/td[3]/text()')[0].strip('\n')#技能1 LV2 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[4]/td[4]/text()')[0].strip('\n')#技能1 LV2 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[4]/td[5]/text()')[0].strip('\n')#技能1 LV2 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[5]/td[3]/text()')[0].strip('\n')#技能1 LV3 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[5]/td[4]/text()')[0].strip('\n')#技能1 LV3 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[5]/td[5]/text()')[0].strip('\n')#技能1 LV3 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[6]/td[3]/text()')[0].strip('\n')#技能1 LV4 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[6]/td[4]/text()')[0].strip('\n')#技能1 LV4 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[6]/td[5]/text()')[0].strip('\n')#技能1 LV4 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[7]/td[3]/text()')[0].strip('\n')#技能1 LV5 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[7]/td[4]/text()')[0].strip('\n')#技能1 LV5 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[7]/td[5]/text()')[0].strip('\n')#技能1 LV5 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[8]/td[3]/text()')[0].strip('\n')#技能1 LV6 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[8]/td[4]/text()')[0].strip('\n')#技能1 LV6 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[8]/td[5]/text()')[0].strip('\n')#技能1 LV6 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[9]/td[3]/text()')[0].strip('\n')#技能1 LV7 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[9]/td[4]/text()')[0].strip('\n')#技能1 LV7 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[9]/td[5]/text()')[0].strip('\n')#技能1 LV7 持续

    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[10]/td[3]/text()')[0].strip('\n')#技能1 LV8 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[10]/td[4]/text()')[0].strip('\n')#技能1 LV8 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[10]/td[5]/text()')[0].strip('\n')#技能1 LV8 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[11]/td[3]/text()')[0].strip('\n')#技能1 LV9 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[11]/td[4]/text()')[0].strip('\n')#技能1 LV9 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[11]/td[5]/text()')[0].strip('\n')#技能1 LV9 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[12]/td[3]/text()')[0].strip('\n')#技能1 LV10 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[12]/td[4]/text()')[0].strip('\n')#技能1 LV10 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[12]/td[5]/text()')[0].strip('\n')#技能1 LV10 持续

#技能2（精英1开放）
    get_skill('技能2 技能名称',2,'tr[1]/td[2]/big')
    get_skill('技能2 回复类型',2,'tr[1]/td[3]/span[1]')
    get_skill('技能2 触发类型',2,'tr[1]/td[3]/span[2]')
    get_skill('技能2 LV7 初始',2,'tr[9]/td[3]')
    get_skill('技能2 LV7 消耗',2,'tr[9]/td[4]')
    get_skill('技能2 LV7 持续',2,'tr[9]/td[5]')

    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[1]/td[2]/big/text()')[0].strip('\n')#技能名称
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[1]/text()')[0].strip('\n')#回复类型
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[2]/text()')[0].strip('\n')#触发类型

    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[3]/td[3]/text()')[0].strip('\n')#技能2 LV1 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[3]/td[4]/text()')[0].strip('\n')#技能2 LV1 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[3]/td[5]/text()')[0].strip('\n')#技能2 LV1 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[4]/td[3]/text()')[0].strip('\n')#技能2 LV2 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[4]/td[4]/text()')[0].strip('\n')#技能2 LV2 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[4]/td[5]/text()')[0].strip('\n')#技能2 LV2 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[5]/td[3]/text()')[0].strip('\n')#技能2 LV3 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[5]/td[4]/text()')[0].strip('\n')#技能2 LV3 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[5]/td[5]/text()')[0].strip('\n')#技能2 LV3 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[6]/td[3]/text()')[0].strip('\n')#技能2 LV4 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[6]/td[4]/text()')[0].strip('\n')#技能2 LV4 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[6]/td[5]/text()')[0].strip('\n')#技能2 LV4 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[7]/td[3]/text()')[0].strip('\n')#技能2 LV5 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[7]/td[4]/text()')[0].strip('\n')#技能2 LV5 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[7]/td[5]/text()')[0].strip('\n')#技能2 LV5 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[8]/td[3]/text()')[0].strip('\n')#技能2 LV6 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[8]/td[4]/text()')[0].strip('\n')#技能2 LV6 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[8]/td[5]/text()')[0].strip('\n')#技能2 LV6 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[9]/td[3]/text()')[0].strip('\n')#技能2 LV7 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[9]/td[4]/text()')[0].strip('\n')#技能2 LV7 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[9]/td[5]/text()')[0].strip('\n')#技能2 LV7 持续

    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[10]/td[3]/text()')[0].strip('\n')#技能2 LV8 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[10]/td[4]/text()')[0].strip('\n')#技能2 LV8 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[10]/td[5]/text()')[0].strip('\n')#技能2 LV8 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[11]/td[3]/text()')[0].strip('\n')#技能2 LV9 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[11]/td[4]/text()')[0].strip('\n')#技能2 LV9 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[11]/td[5]/text()')[0].strip('\n')#技能2 LV9 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[12]/td[3]/text()')[0].strip('\n')#技能2 LV10 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[12]/td[4]/text()')[0].strip('\n')#技能2 LV10 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[12]/td[5]/text()')[0].strip('\n')#技能2 LV10 持续

#技能3（精英2开放）
    get_skill('技能3 技能名称',3,'tr[1]/td[2]/big')
    get_skill('技能3 回复类型',3,'tr[1]/td[3]/span[1]')
    get_skill('技能3 触发类型',3,'tr[1]/td[3]/span[2]')
    get_skill('技能3 LV7 初始',3,'tr[9]/td[3]')
    get_skill('技能3 LV7 消耗',3,'tr[9]/td[4]')
    get_skill('技能3 LV7 持续',3,'tr[9]/td[5]')

    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[1]/td[2]/big/text()')[0].strip('\n')#技能名称
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[1]/text()')[0].strip('\n')#回复类型
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[2]/text()')[0].strip('\n')#触发类型

    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[3]/td[3]/text()')[0].strip('\n')#技能2 LV1 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[3]/td[4]/text()')[0].strip('\n')#技能2 LV1 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[3]/td[5]/text()')[0].strip('\n')#技能2 LV1 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[4]/td[3]/text()')[0].strip('\n')#技能2 LV2 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[4]/td[4]/text()')[0].strip('\n')#技能2 LV2 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[4]/td[5]/text()')[0].strip('\n')#技能2 LV2 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[5]/td[3]/text()')[0].strip('\n')#技能2 LV3 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[5]/td[4]/text()')[0].strip('\n')#技能2 LV3 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[5]/td[5]/text()')[0].strip('\n')#技能2 LV3 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[6]/td[3]/text()')[0].strip('\n')#技能2 LV4 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[6]/td[4]/text()')[0].strip('\n')#技能2 LV4 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[6]/td[5]/text()')[0].strip('\n')#技能2 LV4 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[7]/td[3]/text()')[0].strip('\n')#技能2 LV5 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[7]/td[4]/text()')[0].strip('\n')#技能2 LV5 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[7]/td[5]/text()')[0].strip('\n')#技能2 LV5 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[8]/td[3]/text()')[0].strip('\n')#技能2 LV6 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[8]/td[4]/text()')[0].strip('\n')#技能2 LV6 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[8]/td[5]/text()')[0].strip('\n')#技能2 LV6 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[9]/td[3]/text()')[0].strip('\n')#技能2 LV7 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[9]/td[4]/text()')[0].strip('\n')#技能2 LV7 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[9]/td[5]/text()')[0].strip('\n')#技能2 LV7 持续

    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[10]/td[3]/text()')[0].strip('\n')#技能2 LV8 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[10]/td[4]/text()')[0].strip('\n')#技能2 LV8 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[10]/td[5]/text()')[0].strip('\n')#技能2 LV8 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[11]/td[3]/text()')[0].strip('\n')#技能2 LV9 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[11]/td[4]/text()')[0].strip('\n')#技能2 LV9 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[11]/td[5]/text()')[0].strip('\n')#技能2 LV9 持续
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[12]/td[3]/text()')[0].strip('\n')#技能2 LV10 初始
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[12]/td[4]/text()')[0].strip('\n')#技能2 LV10 消耗
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[12]/td[5]/text()')[0].strip('\n')#技能2 LV10 持续


    #potential
    def get_potential(field:str,expresion:str):
        if codename=='断罪者':
             pass
        #获取技能
        potential_uni_path='//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/{rp}/text()'
        try:
            data_dict[field] = html.xpath(potential_uni_path.replace('{rp}',expresion))[0].strip('\n')
        except:
            data_dict[field] = None
        return data_dict[field]
    get_potential('潜能2','td[1]')
    get_potential('潜能3','td[2]')
    get_potential('潜能4','td[3]')
    get_potential('潜能5','td[4]')
    get_potential('潜能6','td[5]')
    
    # potential_uni_path='//*[@id="mw-content-text"]/div/h2[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/{rp}/text()'
    # data_dict['潜能2'] = html.xpath(potential_uni_path.replace('{rp}','td[1]'))[0].strip('\n')
    # data_dict['潜能3'] = html.xpath(potential_uni_path.replace('{rp}','td[2]'))[0].strip('\n')
    # data_dict['潜能4'] = html.xpath(potential_uni_path.replace('{rp}','td[3]'))[0].strip('\n')
    # data_dict['潜能5'] = html.xpath(potential_uni_path.replace('{rp}','td[4]'))[0].strip('\n')
    # data_dict['潜能6'] = html.xpath(potential_uni_path.replace('{rp}','td[5]'))[0].strip('\n')

    return data_dict
####################################################################





#导出到excel
def result_to_file(type):
    from time import strftime,localtime
    now=strftime('%Y-%m-%d %H-%M-%S',localtime())
    save_path = 'result/PRTS爬取结果{0}.{1}'.format(now,type)
    if sys.gettrace():  #判断程序是否在终端执行
        # input('Press Enter to save data:')
        pass
    if type=='xlsx':
        df.to_excel(save_path, index=False)
    elif type=='csv':
        df.to_csv(save_path, index=False, encoding='utf-8-sig')

    if os.path.exists(save_path):  #判断是否保存成功
        print('Saved success!')
        print(save_path)


#插入到sql
def result_to_sql(df):
    #1.查询"Arknights".sd_test中属性为空的干员,返回干员名列表
    #2.根据列表插入df中的数据
    #3.


    
    from psycopg2 import connect
    arkdb = connect(database="postgres",user="postgres",password="shen124357689", host="127.0.0.1", port="5432")
    cursor = arkdb.cursor()

    column = '生命'


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


    '''
        INSERT INTO public.base_info (id, codename, star, profession, codename_jp, codename_en, add_time, order_id)
        VALUES (DEFAULT, '令', 6, '辅助', NULL, 'Ling', '2022-01-25 16:00:00.000000', NULL);
        未完成
    '''
#df.loc[2]['干员']


if __name__ == '__main__':
    codename_list = ['黑键','车尔尼','濯尘芙蓉','埃拉托','归溟幽灵鲨', '艾丽妮', '流明', '掠风','泥岩','白雪','卡缇','红云','铃兰','星极','阿米娅（近卫）','铸铁','温蒂','贾维','风笛','阿米娅','布洛卡','霜叶','早露','猎蜂','赫拉格','拉普兰德','斯卡蒂','棘刺','真理','安洁莉娜','斑点','伊桑','断崖','断罪者','黑','槐琥','石棉','翎羽','微风','砾','拜松','格雷伊','森蚺','深靛','清流','杰克','蛇屠箱','松果','古米','苦艾','梅','卡夫卡','安赛尔','炎狱炎熔','米格鲁','贝娜','瑕光','绮良','战车','泡普卡','燧石','普罗旺斯','桃金娘','山','格劳克斯','泡泡','宴','夜莺','薄绿','浊心斯卡蒂','伊芙利特','乌有','巡林者','刻刀','波登可','空','红','芙蓉','灵知','凛冬','流星','天火','黑角','暗索','白金','暴行','克洛丝','狮蝎','吽','爱丽丝','嘉维尔','赤冬','可颂','苇草','极境','食铁兽','12F','月见夜','雷蛇','暴雨','罗宾','讯使','夕','闪击','雪雉','梅尔','年','野鬃','能天使','阿消','惊蛰','蜜蜡','麦哲伦','空弦','异客','傀影','巫恋','霜华','焰尾','Lancet-2','深海色','灰喉','坚雷','杜宾','桑葚','THRM-EX','安德切尔','罗比菈塔','特米米','塞雷娅','清道夫','德克萨斯','慕斯','柏喙','缠丸','末药','月禾','熔泉','崖心','四月','芬','卡达','杰西卡','嵯峨','帕拉斯','因陀罗','阿','火神','香草','陈','送葬人','艾雅法拉','锡兰','凯尔希','豆苗','絮雨','史都华德','诗怀雅','假日威龙陈','安哲拉','炎客','杜林','蓝毒','羽毛笔','苏苏洛','歌蕾蒂娅','推进之王','夜刀','幽灵鲨','格拉尼','银灰','水月','亚叶','华法琳','远牙','芳汀','煌','Castle-3','角峰','迷迭香','梓兰','稀音','灰毫','赫默','陨星','慑砂','艾丝黛尔','蚀清','炎熔','鞭刃','玫兰莎','调香师','红豆','临光','夜烟','蜜莓','夜魔','守林人','W','孑','莱恩哈特','芙兰卡','极光','远山','白面鸮','闪灵','耶拉','卡涅利安','初雪','莫斯提马','奥斯塔','空爆','灰烬','史尔特尔','琴柳','酸糖','龙舌兰','耀骑士临光','星熊','地灵','图耶','安比尔','布丁','刻俄柏','正义骑士号',]
    #codename_list =pgq.pg_query('干员')
    # if '阿米娅（近卫）' in codename_list:#对升变阿米娅进行特殊处理
    #     codename_list[codename_list.index('阿米娅（近卫）')]='阿米娅(近卫)'
    #codename_list=codename_list[codename_list.index('安赛尔'):]#从中间截取位置开始
    df = pd.DataFrame([])
    for codename in codename_list:#干员的循环
        # codename='黑键'
        cache_path = 'cache/{} - PRTS - 玩家自由构筑的明日方舟中文Wiki.html'.format(codename)  #缓存路径
        cache_flag = not os.path.isfile(cache_path)  #决定读取方式为缓存或网页爬取
        if len(codename) < 4:
            prt_split = '\t\t'
        elif len(codename) >= 4:
            prt_split = '\t'
        # cache_flag = True  #debug选项,强制从网页爬取
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
            time.sleep(10)
        else:  #从缓存读取
            with open(cache_path, 'r', encoding='utf-8') as f:    
                res_text = f.read()
            
            try:
                print('{0}{1}缓存读取成功({2}/{3})'.format(
                    codename, prt_split,
                    codename_list.index(codename) + 1, len(codename_list)))
            except:
                print('正在调试指定列表外的干员...')
        html = etree.HTML(res_text)
        # df = assemble(html)
        try:
            data_dict=get_data(html)
        except:
            failed_list.append(codename)
        df=df.append(data_dict, ignore_index=True)

    print('失败列表：' , set(failed_list))

    df[['上线时间']] = df[['上线时间']].apply(pd.to_datetime)  #修改df单列的数据类型
    order = ['干员','稀有度','职业','子职业','英文','上线时间','部署位','再部署时间','初始部署费用','阻挡数','攻击间隔','生命上限-精英0 1级','生命上限-精英0 满级','生命上限-精英1 满级','生命上限-精英2 满级','生命上限-信赖加成上限','攻击-精英0 1级','攻击-精英0 满级','攻击-精英1 满级','攻击-精英2 满级','攻击-信赖加成上限','防御-精英0 1级','防御-精英0 满级','防御-精英1 满级','防御-精英2 满级','防御-信赖加成上限','法术抗性-精英0 1级','法术抗性-精英0 满级','法术抗性-精英1 满级','法术抗性-精英2 满级','法术抗性-信赖加成上限','技能1 技能名称','技能1 回复类型','技能1 触发类型','技能1 LV7 初始','技能1 LV7 消耗','技能1 LV7 持续','技能2 技能名称','技能2 回复类型','技能2 触发类型','技能2 LV7 初始','技能2 LV7 消耗','技能2 LV7 持续','技能3 技能名称','技能3 回复类型','技能3 触发类型','技能3 LV7 初始','技能3 LV7 消耗','技能3 LV7 持续','潜能2','潜能3','潜能4','潜能5','潜能6']
    df = df[order]#调整column顺序
                      
    result_to_file('csv')  #导出到excel/csv
    result_to_sql(df)  #插入到sql
