# -*- coding:utf-8 -*-

'''
Description: 文件描述
Author: Cyletix
Date: 2022-08-11 23:42:00
FilePath: \ArknightsResearch\爬虫\get_op_info.py
'''
import os
import re
import sys
import time
from datetime import datetime

import pandas as pd
from lxml import etree
from requests import get
from requests.models import ChunkedEncodingError

from mypgsql import pandas_sqlalchemy, search_sql

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
    # def get_data_by_code(field:str,expresion:str):
    #     try:
    #         exec("data_dict[{0}] = {1}".format(field,expresion))
    #     except:
    #         failed_list.append(codename)
    #         data_dict[field] = None
    #     return data_dict[field]
    # get_data_by_code('干员','''html.xpath('//*[@id="charname"]/text()')[0]''')
    # get_data_by_code('稀有度','''int(html.xpath('//*[@id="rare"]/text()')[0]) + 1''')
    # get_data_by_code('职业','''html.xpath('//*[@id="charclasstxt"]/div/a[1]/text()')[0]''')
    # get_data_by_code('子职业','''html.xpath('//*[@id="charclasstxt"]/div/a[2]/text()')[0]''')
    # get_data_by_code('英文','''html.xpath('//*[@id="charname-en"]/text()')[0] ''')
    # get_data_by_code('上线时间','''datetime.strptime(html.xpath('//table[tbody/tr/th="上线时间\n"]/tbody/tr[2]/td/text()')[0],'%Y年%m月%d日 %H:%M\n').strftime('%Y-%m-%d %H:%M:%S') ''')
    # get_data_by_code('部署位','''html.xpath('//*[@title="近战位" or @title="远程位"]/text()')[0]''')

    data_dict['干员'] = html.xpath('//*[@id="charname" or @class="charname"]/text()')[0]  #干员
    try:
        data_dict['稀有度'] = re.search('\d',html.xpath('//div[@class="charstar"]/img/@src')[0].split('/')[-1]).group()  #稀有度
        
    except:pass
    try:
        # data_dict['职业'] = [x for x in html.xpath('//div[@id="mw-normal-catlinks"]/ul/li/a/text()') if re.search('先锋|近卫|重装|医疗|术师|辅助|特种',x)][0]   #职业
        data_dict['职业'] = html.xpath('//div[@id="mw-normal-catlinks"]/ul/li/a/text()')[1][:2]
    except:
        data_dict['职业'] = html.xpath('//div[a/text()="分类"]/li[2]/a/text()')[0]
    try:
        data_dict['子职业'] =  html.xpath('//div[@class="branch-text"]/a/text()')[0]
    except:pass
    try:
        data_dict['英文'] = html.xpath('//*[@class="charname-en"]/text()')[0].replace('\\','')  #英文
    except:pass
    try:
        date_str=html.xpath('//table[tbody/tr/th="上线时间\n"]/tbody/tr[2]/td/text()')[0]
    except:pass
    try:
        data_dict['上线时间'] = datetime.strptime(date_str,'%Y年%m月%d日 %H:%M\n').strftime('%Y-%m-%d %H:%M:%S') 
    except:pass
    try:
        data_dict['部署位'] = html.xpath('//div[@class="char-pos-text"]/a/text()')[0]  #部署位,近战/远程,新增词条
    except:pass

    #attribute
    data_dict['再部署时间'] = html.xpath('//*[th="再部署时间\n" or th="初始部署费用\n"]/td[1]/text()')[0].strip('\n|s')
    data_dict['初始部署费用'] = html.xpath('//*[th="再部署时间\n" or th="初始部署费用\n"]/td[2]/text()')[0].strip('\n|s')
    data_dict['阻挡数'] = html.xpath('//*[th="阻挡数\n" or th="攻击间隔\n"]/td[1]/text()')[0].strip('\n')
    data_dict['攻击间隔'] = html.xpath('//*[th="阻挡数\n" or th="攻击间隔\n"]/td[2]/text()')[0].strip('\n|s')


    data_dict['生命上限-精英0 1级'] = html.xpath('//*[tbody/tr/th="生命上限\n"]/tbody/tr[2]/td[1]/text()')[0].strip('\n')
    data_dict['生命上限-精英0 满级'] = html.xpath('//*[tbody/tr/th="生命上限\n"]/tbody/tr[2]/td[2]/text()')[0].strip('\n')
    data_dict['生命上限-精英1 满级'] = html.xpath('//*[tbody/tr/th="生命上限\n"]/tbody/tr[2]/td[3]/text()')[0].strip('\n')
    data_dict['生命上限-精英2 满级'] = html.xpath('//*[tbody/tr/th="生命上限\n"]/tbody/tr[2]/td[4]/text()')[0].strip('\n')
    data_dict['生命上限-信赖加成上限'] = html.xpath('//*[tbody/tr/th="生命上限\n"]/tbody/tr[2]/td[5]/text()')[0].strip('\n')

    data_dict['攻击-精英0 1级'] = html.xpath('//*[tbody/tr/th="攻击\n"]/tbody/tr[3]/td[1]/text()')[0].strip('\n')
    data_dict['攻击-精英0 满级'] = html.xpath('//*[tbody/tr/th="攻击\n"]/tbody/tr[3]/td[2]/text()')[0].strip('\n')
    data_dict['攻击-精英1 满级'] = html.xpath('//*[tbody/tr/th="攻击\n"]/tbody/tr[3]/td[3]/text()')[0].strip('\n')
    data_dict['攻击-精英2 满级'] = html.xpath('//*[tbody/tr/th="攻击\n"]/tbody/tr[3]/td[4]/text()')[0].strip('\n')
    data_dict['攻击-信赖加成上限'] = html.xpath('//*[tbody/tr/th="攻击\n"]/tbody/tr[3]/td[5]/text()')[0].strip('\n')

    data_dict['防御-精英0 1级'] = html.xpath('//*[tbody/tr/th="防御\n"]/tbody/tr[4]/td[1]/text()')[0].strip('\n')
    data_dict['防御-精英0 满级'] = html.xpath('//*[tbody/tr/th="防御\n"]/tbody/tr[4]/td[2]/text()')[0].strip('\n')
    data_dict['防御-精英1 满级'] = html.xpath('//*[tbody/tr/th="防御\n"]/tbody/tr[4]/td[3]/text()')[0].strip('\n')
    data_dict['防御-精英2 满级'] = html.xpath('//*[tbody/tr/th="防御\n"]/tbody/tr[4]/td[4]/text()')[0].strip('\n')
    data_dict['防御-信赖加成上限'] = html.xpath('//*[tbody/tr/th="防御\n"]/tbody/tr[4]/td[5]/text()')[0].strip('\n')

    data_dict['法术抗性-精英0 1级'] = html.xpath('//*[tbody/tr/th="法术抗性\n"]/tbody/tr[5]/td[1]/text()')[0].strip('\n')
    data_dict['法术抗性-精英0 满级'] = html.xpath('//*[tbody/tr/th="法术抗性\n"]/tbody/tr[5]/td[2]/text()')[0].strip('\n')
    data_dict['法术抗性-精英1 满级'] = html.xpath('//*[tbody/tr/th="法术抗性\n"]/tbody/tr[5]/td[3]/text()')[0].strip('\n')
    data_dict['法术抗性-精英2 满级'] = html.xpath('//*[tbody/tr/th="法术抗性\n"]/tbody/tr[5]/td[4]/text()')[0].strip('\n')
    data_dict['法术抗性-信赖加成上限'] = html.xpath('//*[tbody/tr/th="法术抗性\n"]/tbody/tr[5]/td[5]/text()')[0].strip('\n')


    #skill
    def get_skill(field:str,sk_no:int,expresion:str):
        #获取技能并插入
        try:
            data_dict[field] = html.xpath(expresion)[0].strip('\n')
        except:
            data_dict[field] = None
        return data_dict[field]

#技能1（精英0开放）
    get_skill('技能1 技能名称',1,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[1]/td[2]/big/text()')
    get_skill('技能1 回复类型',1,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[1]/span/text()')
    get_skill('技能1 触发类型',1,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[2]/span/text()')
    get_skill('技能1 LV7 初始',1,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[9]/td[3]/text()')
    get_skill('技能1 LV7 消耗',1,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[9]/td[4]/text()')
    get_skill('技能1 LV7 持续',1,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[9]/td[5]/text()')


    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[1]/td[2]/big/text()')[0].strip('\n')#技能名称
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[1]/span/text()')[0].strip('\n')#回复类型
    # html.xpath('//*[@id="mw-content-text"]/div[1]/p[b/text()="技能1（精英0开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[2]/span/text()')[0].strip('\n')#触发类型

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
    get_skill('技能2 技能名称',2,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[1]/td[2]/big/text()')
    get_skill('技能2 回复类型',2,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[1]/span/text()')
    get_skill('技能2 触发类型',2,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[2]/span/text()')
    get_skill('技能2 LV7 初始',2,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[9]/td[3]/text()')
    get_skill('技能2 LV7 消耗',2,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[9]/td[4]/text()')
    get_skill('技能2 LV7 持续',2,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能2（精英1开放）"]/following-sibling::table[1]/tbody/tr[9]/td[5]/text()')

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
    get_skill('技能3 技能名称',3,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[1]/td[2]/big/text()')
    get_skill('技能3 回复类型',3,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[1]/span/text()')
    get_skill('技能3 触发类型',3,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[1]/td[3]/span[2]/span/text()')
    get_skill('技能3 LV7 初始',3,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[9]/td[3]/text()')
    get_skill('技能3 LV7 消耗',3,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[9]/td[4]/text()')
    get_skill('技能3 LV7 持续',3,'//*[@id="mw-content-text"]/div[1]/p[b/text()="技能3（精英2开放）"]/following-sibling::table[1]/tbody/tr[9]/td[5]/text()')

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
    if codename=='断罪者':
        pass
    else:
        try:
            potential_uni_path='//*[span[@id="潜能提升"]]/following-sibling::table/tbody/tr[2]/{rp}/text()'
            data_dict['潜能2'] = html.xpath(potential_uni_path.replace('{rp}','td[1]'))[0].strip('\n')
            data_dict['潜能3'] = html.xpath(potential_uni_path.replace('{rp}','td[2]'))[0].strip('\n')
            data_dict['潜能4'] = html.xpath(potential_uni_path.replace('{rp}','td[3]'))[0].strip('\n')
            data_dict['潜能5'] = html.xpath(potential_uni_path.replace('{rp}','td[4]'))[0].strip('\n')
            data_dict['潜能6'] = html.xpath(potential_uni_path.replace('{rp}','td[5]'))[0].strip('\n')
        except:
            data_dict['潜能2'] = html.xpath('//*[span[@id="潜能提升"]]/following-sibling::section/table/tbody/tr[th/text()="潜能2\n"]/td/text()')[0]
            data_dict['潜能3'] = html.xpath('//*[span[@id="潜能提升"]]/following-sibling::section/table/tbody/tr[th/text()="潜能3\n"]/td/text()')[0]
            data_dict['潜能4'] = html.xpath('//*[span[@id="潜能提升"]]/following-sibling::section/table/tbody/tr[th/text()="潜能4\n"]/td/text()')[0]
            data_dict['潜能5'] = html.xpath('//*[span[@id="潜能提升"]]/following-sibling::section/table/tbody/tr[th/text()="潜能5\n"]/td/text()')[0]
            data_dict['潜能6'] = html.xpath('//*[span[@id="潜能提升"]]/following-sibling::section/table/tbody/tr[th/text()="潜能6\n"]/td/text()')[0]
    return data_dict
####################################################################
#导出到excel
def result_to_file(type):
    from time import localtime, strftime
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

def type_convert(df):
    df[['上线时间']] = df[['上线时间']].apply(pd.to_datetime)  #修改df单列的数据类型
    df[['再部署时间']] = df[['再部署时间']].apply(pd.to_numeric)
    df[['攻击间隔']] = df[['攻击间隔']].apply(pd.to_numeric)
    




if __name__ == '__main__':
    codename_list = [
       #'缄默德克萨斯','谜图','和弦','焰影苇草','石英','雪绒','子月','伺夜','斥罪',
        ]
    codename_list=search_sql(codename_list) # 自动搜索筛选不在数据库中的干员,
    
    #codename_list =pgq.pg_query('干员')
    if '阿米娅（近卫）' in codename_list:#对升变阿米娅进行特殊处理
        codename_list[codename_list.index('阿米娅（近卫）')]='阿米娅(近卫)'
    #codename_list=codename_list[codename_list.index('安赛尔'):]#从中间截取位置开始
    df = pd.DataFrame([])
    #干员循环
    for codename in codename_list:
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
            df=df.append(data_dict, ignore_index=True)
        except:
            failed_list.append(codename)
    print('失败列表：' , set(failed_list))

    type_convert(df)

    order = ['干员','稀有度','职业','子职业','英文','上线时间','部署位','再部署时间','初始部署费用','阻挡数','攻击间隔','生命上限-精英0 1级','生命上限-精英0 满级','生命上限-精英1 满级','生命上限-精英2 满级','生命上限-信赖加成上限','攻击-精英0 1级','攻击-精英0 满级','攻击-精英1 满级','攻击-精英2 满级','攻击-信赖加成上限','防御-精英0 1级','防御-精英0 满级','防御-精英1 满级','防御-精英2 满级','防御-信赖加成上限','法术抗性-精英0 1级','法术抗性-精英0 满级','法术抗性-精英1 满级','法术抗性-精英2 满级','法术抗性-信赖加成上限','技能1 技能名称','技能1 回复类型','技能1 触发类型','技能1 LV7 初始','技能1 LV7 消耗','技能1 LV7 持续','技能2 技能名称','技能2 回复类型','技能2 触发类型','技能2 LV7 初始','技能2 LV7 消耗','技能2 LV7 持续','技能3 技能名称','技能3 回复类型','技能3 触发类型','技能3 LV7 初始','技能3 LV7 消耗','技能3 LV7 持续','潜能2','潜能3','潜能4','潜能5','潜能6']
    df = df[order] #调整column顺序
    df=df.replace('——',None) #替换'——'属性缺失项为空值(此项会报警,不用管)
    # result_to_file('csv')  #导出到excel/csv
    pandas_sqlalchemy(df)  #插入到sql





# '干员'
# '稀有度'
# '职业'
# '子职业'
# '英文'
# '上线时间'
# '部署位'
# '再部署时间'
# '初始部署费用'
# '阻挡数'
# '攻击间隔'
# '生命上限-精英0 1级'
# '生命上限-精英0 满级'
# '生命上限-精英1 满级'
# '生命上限-精英2 满级'
# '生命上限-信赖加成上限'
# '攻击-精英0 1级'
# '攻击-精英0 满级'
# '攻击-精英1 满级'
# '攻击-精英2 满级'
# '攻击-信赖加成上限'
# '防御-精英0 1级'
# '防御-精英0 满级'
# '防御-精英1 满级'
# '防御-精英2 满级'
# '防御-信赖加成上限'
# '法术抗性-精英0 1级'
# '法术抗性-精英0 满级'
# '法术抗性-精英1 满级'
# '法术抗性-精英2 满级'
# '法术抗性-信赖加成上限'
# '技能1 技能名称'
# '技能1 回复类型'
# '技能1 触发类型'
# '技能1 LV7 初始'
# '技能1 LV7 消耗'
# '技能3 触发类型'
# '技能3 LV7 初始'
# '技能3 LV7 消耗'
# '技能3 LV7 持续'
# '潜能2'
# '潜能3'
# '潜能4'
# '潜能5'
# '潜能6'