'''
Description: 文件描述

Author: Cyletix
Date: 2021-07-17 22:08:59
LastEditTime: 2022-02-08 21:28:10
FilePath: \ArknightsResearch\get_link_info.py
'''
from requests import get
from lxml import etree
import pyperclip

def get_link_info(link):
    domain = 'https://www.bilibili.com/video/'
    split_list=link.split('/')
    if len(split_list)==5:
        link_type='link'
        url=link
        #link='https://www.bilibili.com/video/BV1db4y1e7R6'
    elif len(split_list)==1 and split_list[0][:2].upper()=='BV':
        link_type='BV'
        url=domain+link
        #link='BV1db4y1e7R6'
    elif len(split_list)==1 and split_list[0][:2].lower()=='av':
        link_type='av'
        url=domain+link
        #link='av83562606'
    elif len(split_list)==3:
        link_type='link without https'
        url='https//'+link
        #link='www.bilibili.com/video/BV1db4y1e7R6' 
    else:
        return '链接类型好怪哦,你是不是填错了'
        print(link_type)
    
    res = get(url)
    res_text=res.text
    html = etree.HTML(res_text)
    
    # video_time=html.xpath('//*[@id="viewbox_report"]/div[@class="video-data"]/span[@class="pudate item"]/text()')[0].strip('\n ')
    # video_time=html.xpath('//*[@id="viewbox_report"]/div/div/span[3]/span/span/text()')[0].strip('\n ')
    video_time=html.xpath('//*[@class="pudate-text"]/text()')[0].strip('\n ')

    video_author=html.xpath('//*[@id="v_upinfo"]/div[@class="up-info_right"]/div[@class="name"]/a[@target]/text()')[0].strip('\n ')

    # result='{0}\t{1}\t{2}'.format(video_author,url,video_time)
    result='{}\t{}'.format(url,video_time)#仅复制url和日期
    print(result)
    return result


if __name__=='__main__':
    link_list=[
'BV1i44y137J5',
'BV1Su411C76E',
'BV1iF411g7j7',
'BV1Y94y1d7Zd',
'BV1c3411T71m',
'BV1US4y1h7FR',
'BV1ra411Y7Xe',
'BV1g5411m7rw',
'BV1Ha411Y7nY',
'BV1HL4y1V7To',
'BV1tF411g7S6',
'BV1CY4y1e7ud',
'BV1G5411m7LC',
'BV1DF411j76C',
'BV11Y4y1e7hk',
'https://www.bilibili.com/video/BV1m3411K7jr?p=5',
'BV1VZ4y1m77y',
'BV1kY4y187Qj',
'https://www.bilibili.com/video/BV1m3411K7jr?p=6',
'https://www.bilibili.com/video/BV1HR4y1K7q1',
'BV1CS4y1Y7xm',
'BV1Hu41167rZ',
'BV1iS4y1h7ek',
'BV1V44y1G7of',
'BV1Wi4y1U7DY',
'https://www.bilibili.com/video/BV1Sa411Y7xJ',
'BV163411T7iK',
'BV163411T7iK',
'BV1H5411m7Bd',
'BV1Dr4y1t7iG',
]
    for link in link_list:
        pyperclip.copy(get_link_info(link))#将结果复制到剪切板
        input('已复制此条目到剪切板,请粘贴到表格后按任意键继续:')
