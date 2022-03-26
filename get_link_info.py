'''
Description: 文件描述

Author: Cyletix
Date: 2021-07-17 22:08:59
LastEditTime: 2022-02-08 21:28:10
FilePath: \ArknightsResearch\get_link_info.py
'''
from requests import get
from time import strptime
from lxml import etree
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
    video_time=html.xpath('//*[@id="viewbox_report"]/div[@class="video-data"]/span[3]')[0].text
    video_author=html.xpath('//*[@id="v_upinfo"]/div[@class="up-info_right"]/div[@class="name"]/a[@target]')[0].text.strip('\n ')
    result='{0}\t{1}\t{2}'.format(video_author,url,video_time)
    print(result)
    return result








# def get_BV_time(BV):
#     import requests
#     from time import strptime
#     domain = 'https://www.bilibili.com/video/'
#     url = domain+BV
    
#         # 转换格式
#     link_type='link'

#     if link_type=='link':
#         # BV号转链接
#         link_list = []
#         for BV in BV_link_list:
#             if (len(BV)==12):
#                 link_list.append(domain+BV)
#             else:
#                 link_list.append(BV)
#         for link in link_list:
#             print(link)

#     elif link_type=='BV':
#         # 链接转BV号
#         BV_list = []
#         for BV in BV_link_list:
#             if (BV.find(domain) == 0):
#                 BV_list.append(BV.split('/')[-1])
#             else:
#                 BV_list.append(BV)


#     r = requests.get(url)

#     start_pos = r.text.find('content="20')+9
#     time_str = r.text[start_pos:start_pos+19]

#     '''判断是否是一个有效的日期字符串'''
#     try:
#         strptime(time_str, "%Y-%m-%d %H:%M:%S")
#         return time_str
#     except:
#         return False


if __name__=='__main__':
    link_list=['https://www.bilibili.com/video/BV1N44y1W78g',
               'https://www.bilibili.com/video/BV1F3411E7XD',
               'https://www.bilibili.com/video/BV1kq4y1h77B',
               'https://www.bilibili.com/video/BV1fT4y1k7gM']
    for link in link_list:
        get_link_info(link)
'''
    import pandas as pd
    while(True):
        get_way=input("请输入获取BV号方式：1为从excel获取，2为命令行手动输入\n")
        if get_way=='1':
            print("从excel获取BV号:")
            excel_path = "E:\下载\无精二表 (8).xlsx"

            df = pd.read_excel(excel_path, sheet_name='14.密林悍将归来')
            BV_link_list = df['链接']        
            break
        elif get_way=='2':
            print("手动输入BV和link,以end结尾:")
            BV_link_list=[]
            while(True):
                temp=input()
                if temp=='end':
                    break
                BV_link_list.append(temp)
            break
        else:
            print("输入错误，请重新输入")
            continue
    domain = 'https://www.bilibili.com/video/'  
    # 自动获取视频发布日期,不过操作太频繁可能会被拦截，需要手动访问输入验证码
    for BV in BV_link_list:
        try:
            if (BV.find(domain) == 0):
                BV = BV.split('/')[-1]
            print(get_BV_time(BV))
        except:
            print('啊叻？视频不见了？视频内容已被UP主删除，视频无法观看，敬请谅解。')
            continue
'''

