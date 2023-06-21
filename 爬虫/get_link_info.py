'''
Description: 无精二表辅助制表:传入url组,逐条返回{author,url,datetime}并复制到剪切板
Author: Cyletix
Date: 2021-07-17 22:08:59
LastEditTime: 2023-03-14 00:51:17
FilePath: \ArknightsResearch\爬虫\get_link_info.py
'''
from lxml import etree
from pyperclip import copy
from requests import get


def join(List,sep=None):
	return (sep or ' ' ).join(List)

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

    result='{0}\t{1}\t{2}'.format(video_author,url,video_time)
    # result='{}\t{}'.format(url,video_time)#仅复制url和日期
    print(result)
    return result


print('# 此程序用于获取ビリビリ動画信息,传入url 返回{author,url,datetime},用于无精二表制表\n\n输入单括号\'(\'触发多条目输入,再键入\')\'结束')


while True:
    link=input('# 请输入BV号或链接:\n')
    if link=='(':#多条目输入
        # print('# 多条目输入  请连续输入BV号或链接,回车分隔,输入)结束\n')
        link_list=[]
        result_list=[]
        while True:
            link=input('')
            if link==')':
                print('# 多条目输入  结束')
                break
            else:
                link_list.append(link)
        
        for link in link_list:
            result=get_link_info(link)
            result_list.append(result)
        result=join(result_list,'\n')
        copy(result)#将结果复制到剪切板
        input('# 已复制多条目结果到剪切板,请粘贴到表格,按任意键继续:\n')

    else:#单条目输入
        copy(get_link_info(link))#将结果复制到剪切板
        input('# 已复制此条目到剪切板,请粘贴到表格,按任意键继续:\n')
