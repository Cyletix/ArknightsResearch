'''
Description: 
Author: Cyletix/ChatGPT
LastEditTime: 2023-08-07 22:20:08
FilePath: \ArknightsResearche:\OneDrive\Code\GitHub\ArknightsResearch\get_op_info_chatgpt.py
'''
# -*- coding:utf-8 -*-

import os
import re
import time
from datetime import datetime

import pandas as pd
from lxml import etree
from requests import get, models
from requests.exceptions import ChunkedEncodingError

from mypgsql import pandas_sqlalchemy, search_sql
from bs4 import BeautifulSoup

def get_rarity(soup):
    rarity_element = soup.find('div', class_='charstar')
    if rarity_element:
        img_src = rarity_element.find('img')['src']
        rarity = re.search(r'\d', img_src.split('/')[-1]).group()
        return rarity
    return None


def get_base_info(soup):
    data_dict = {}

    # 获取干员名字
    charname_element = soup.find(id='charname') or soup.find(class_='charname')
    data_dict['干员'] = charname_element.get_text() if charname_element else ''

    # 获取稀有度
    rarity_element = soup.select_one('div.charstar')
    if rarity_element and 'star_' in rarity_element['src']:
        rarity = rarity_element['src'].split('star_')[1].split('.png')[0]
        data_dict['稀有度'] = int(rarity)
    else:
        data_dict['稀有度'] = None

    rarity_element = soup.find('div', class_='charstar')
    if rarity_element:
        img_src = rarity_element.find('img')['src']
        rarity = re.search(r'\d', img_src.split('/')[-1]).group()
        return rarity

    # 获取职业和子职业
    catlinks_element = soup.find(id='mw-normal-catlinks')
    if catlinks_element:
        catlinks = catlinks_element.find_all('a')
        data_dict['职业'] = catlinks[1].get_text()[:2] if len(catlinks) > 1 else ''
        data_dict['子职业'] = catlinks[-1].get_text() if len(catlinks) > 2 else ''

    # 获取英文名字
    charname_en_element = soup.find(class_='charname-en')
    data_dict['英文'] = charname_en_element.get_text().replace('\\', '') if charname_en_element else ''

    # 获取上线时间
    try:
        date_str=html.xpath('//table[tbody/tr/th="上线时间\n"]/tbody/tr[2]/td/text()')[0]
        data_dict['上线时间'] = datetime.strptime(date_str,'%Y年%m月%d日 %H:%M\n').strftime('%Y-%m-%d %H:%M:%S') 
    except:pass

    # 获取部署位
    char_pos_element = soup.find(class_='char-pos-text')
    data_dict['部署位'] = char_pos_element.get_text() if char_pos_element else ''

    return data_dict


# def get_attribute(html_tree):
#     data_dict = {}
#     data_dict['再部署时间'] = get_attribute_value(html_tree, '再部署时间\n', '初始部署费用\n', index=0)
#     data_dict['初始部署费用'] = get_attribute_value(html_tree, '再部署时间\n', '初始部署费用\n', index=1)
#     data_dict['阻挡数'] = get_attribute_value(html_tree, '阻挡数\n', '攻击间隔\n', index=0)
#     data_dict['攻击间隔'] = get_attribute_value(html_tree, '阻挡数\n', '攻击间隔\n', index=1)
#     # ... 其他属性数据获取
#     return data_dict

# def get_skill(html_tree):
#     data_dict = {}
#     get_skill_data(html_tree, data_dict, '技能1（精英0开放）', 1)
#     get_skill_data(html_tree, data_dict, '技能2（精英1开放）', 2)
#     get_skill_data(html_tree, data_dict, '技能3（精英2开放）', 3)
#     # ... 其他技能数据获取
#     return data_dict

# def get_potential(html_tree):
#     data_dict = {}
#     if data_dict['干员'] != '断罪者':
#         get_potential_data(html_tree, data_dict)
#     return data_dict

# # Helper functions (同之前的代码)
# # ...

# def get_data(html_tree):
#     base_info = get_base_info(html_tree)
#     attribute = get_attribute(html_tree)
#     skill = get_skill(html_tree)
#     potential = get_potential(html_tree)

#     # Merge all data into a single dictionary
#     data_dict = {**base_info, **attribute, **skill, **potential}
#     return data_dict

def get_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    base_info = get_base_info(soup)
    # attribute_data = get_attribute_data(soup)
    # skill_data = get_skill_data(soup)
    # potential_data = get_potential_data(soup)

    # Combine the extracted data into a dictionary
    operator_data = {
        'Base Info': base_info,
        # 'Attribute': attribute_data,
        # 'Skill': skill_data,
        # 'Potential': potential_data,
    }
    return operator_data




def get_html_by_codename(codename):
    # 构建干员对应的URL
    wiki_url = 'https://prts.wiki/w/'
    operator_url = wiki_url + codename

    cache_path = 'cache/{} - PRTS - 玩家自由构筑的明日方舟中文Wiki.html'.format(codename)
    cache_flag = not os.path.isfile(cache_path)
    cache_flag = True ###################调试用,用完记得删掉
    if cache_flag:  # 从网页爬取并保存为缓存
        while True:
            try:
                res = get(operator_url)
                break
            except (NameError, ChunkedEncodingError):
                time.sleep(60)
                continue

        res_text = res.text
        html_cache = open(cache_path, 'w', encoding='utf-8')
        html_cache.write(res_text)
        html_cache.close()
        print('{0} 网页爬取成功'.format(codename))
        time.sleep(5)
    else:  # 从缓存读取
        with open(cache_path, 'r', encoding='utf-8') as f:
            res_text = f.read()

        print('{0} 缓存读取成功'.format(codename))

    return res_text




if __name__ == '__main__':
    # codename_list = [
    #     # '缄默德克萨斯', '谜图', '和弦', '焰影苇草', '石英', '雪绒', '子月', '伺夜', '斥罪',
    # ]
    
    from read_character_data import get_name_list
    codename_list=get_name_list()
    codename_list = search_sql(codename_list)


    if '阿米娅（近卫）' in codename_list:
        codename_list[codename_list.index('阿米娅（近卫）')] = '阿米娅(近卫)'
    df = pd.DataFrame([])
    dict_list = []
    failed_list=[]

    #干员循环开始
    for codename in codename_list:
        
        try:
            html = get_html_by_codename(codename)
            data_dict = get_data(html)
            # df = df.append(data_dict, ignore_index=True)
            dict_list.append(data_dict)
        except Exception as e:
            print(f"处理 {codename} 时出错：{e}")
            failed_list.append(codename)

    print('失败列表：', set(codename_list) - set(failed_list))



    # df输出到sql
    if input('是否使用df输出到sql?(Y/N)\n')=='Y':
        order = [...]  # 列名顺序
        df = df[order]  # 调整column顺序
        df[['上线时间']] = df[['上线时间']].apply(pd.to_datetime)  #修改df单列的数据类型
        df[['再部署时间']] = df[['再部署时间']].apply(pd.to_numeric)
        df[['攻击间隔']] = df[['攻击间隔']].apply(pd.to_numeric)
        df = df.replace('——', None)  # 替换'——'属性缺失项为空值
        # result_to_file('csv')  # 导出到excel/csv
        pandas_sqlalchemy(df)  # 插入到sql






