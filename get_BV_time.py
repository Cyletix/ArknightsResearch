import pandas as pd

domain = 'https://www.bilibili.com/video/'

def get_BV_time(BV):
    import requests
    import time

    url = domain+BV

    r = requests.get(url)

    start_pos = r.text.find('content="20')+9
    time_str = r.text[start_pos:start_pos+19]

    '''判断是否是一个有效的日期字符串'''
    try:
        time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return time_str
    except:
        return False




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


# 转换格式
link_type='link'

if link_type=='link':
    # BV号转链接
    link_list = []
    for BV in BV_link_list:
        if (len(BV)==12):
            link_list.append(domain+BV)
        else:
            link_list.append(BV)
    for link in link_list:
        print(link)

elif link_type=='BV':
    # 链接转BV号
    BV_list = []
    for BV in BV_link_list:
        if (BV.find(domain) == 0):
            BV_list.append(BV.split('/')[-1])
        else:
            BV_list.append(BV)



# 自动获取视频发布日期,不过操作太频繁可能会被拦截，需要手动访问输入验证码
for BV in BV_link_list:
    try:
        if (BV.find(domain) == 0):
            BV = BV.split('/')[-1]
        print(get_BV_time(BV))
    except:
        print('啊叻？视频不见了？视频内容已被UP主删除，视频无法观看，敬请谅解。')
        continue


