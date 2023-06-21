'''
Description: 正在向get_op_info.py迁移,重写逻辑ing...

Author: Cyletix
Date: 2021-09-12 12:43:04
LastEditTime: 2021-11-02 11:07:16
FilePath: \Code\GitHub\ArknightsResearch\wiki爬取干员信息.py
'''
import pandas as pd
# import xlwings as xw
# from lxml import etree
# excel_path=r"C:\Users\ASUS\OneDrive\文档\明日方舟.xlsx"
# name_list=pd.read_excel(excel_path,sheet_name='干员信息')['干员']

name_list=[
    '灵知',
    '极光',
    '耶拉'
    # '正义骑士号',
]

import requests
wiki_url='http://prts.wiki/w/'
operator_url=''

def findSubStr(substr, str, i):#查找子字符串第i次出现的位置
    count = 0 
    while i > 0:
        index = str.find(substr)
        if index == -1:
            return -1
        else:
            str = str[index+1:]   #第一次出现的位置截止后的字符串
            i -= 1
            count = count + index + 1   #字符串位置数累加
    return count - 1

df=pd.DataFrame(columns = [#这里调整顺序
    '代号',
    '阻挡数',
    '初始部署费用',
    '生命上限',
    '攻击',
    '防御',
    '法术抗性',
    '攻击间隔',
    '再部署时间',
    '技能一初始',
    '技能一消耗',
    '技能一持续',
    '技能二初始',
    '技能二消耗',
    '技能二持续',
])

for i in range(len(name_list)):
    name=name_list[i]
    # name='棘刺'
    operator_url=wiki_url+name
    r = requests.get(operator_url)
    # 基本属性

    # html = etree.HTML(r.text)
    # html_tree = etree.tostring(html)#补全了缺胳膊少腿的标签
            
    Attribute_list=['生命上限','攻击','防御','法术抗性']
    attribute_list=[]
    for Attribute in Attribute_list:
        Attribute_str='<th>{}\n</th>'.format(Attribute)

        #大标题定位
        r_pos=r.text[r.text.find(Attribute_str):][:500]
        #属性值
        attribute=int(r_pos[findSubStr('<td>',r_pos,3)+len('<td>'):].split('\n')[0])
        #对应信赖加成
        attribute_rely=r_pos[findSubStr('<td>',r_pos,5)+len('<td>'):].split('\n')[0]
        if attribute_rely=='':
            attribute_rely=0
        else:
            attribute_rely=int(attribute_rely)
        attribute+=attribute_rely
        attribute_list.append(attribute)
    df=df.append(dict(zip(Attribute_list,attribute_list)), ignore_index=True)

    # 技能
    skill1='<p><b>技能1（精英0开放）</b>'
    r_pos=r.text[r.text.find(skill1):]
    temp=[]
    temp.append(r_pos[findSubStr('<td>',r_pos,26)+len('<td>'):].split('\n')[0])#初始
    temp.append(r_pos[findSubStr('<td>',r_pos,27)+len('<td>'):].split('\n')[0])#消耗
    temp.append(r_pos[findSubStr('<td>',r_pos,28)+len('<td>'):].split('\n')[0])#持续
    for x in temp:
        if x=='':
            temp[temp.index(x)]=str(0)
    # df['技能一初始'][i]=temp[0]
    # df['技能一消耗'][i]=temp[1]
    # df['技能一持续'][i]=temp[2]
    df.loc[:,'技能一初始'][i]=temp[0]
    df.loc[:,'技能一消耗'][i]=temp[1]
    df.loc[:,'技能一持续'][i]=temp[2]
    print(name)

    skill2='<p><b>技能2（精英1开放）</b>'
    r_pos=r.text[r.text.find(skill2):]
    temp=[]
    temp.append(r_pos[findSubStr('<td>',r_pos,26)+len('<td>'):].split('\n')[0])#初始
    temp.append(r_pos[findSubStr('<td>',r_pos,27)+len('<td>'):].split('\n')[0])#消耗
    temp.append(r_pos[findSubStr('<td>',r_pos,28)+len('<td>'):].split('\n')[0])#持续
    for x in temp:
        if x=='':
            temp[temp.index(x)]=str(0)
    # df['技能二初始'][i]=temp[0]
    # df['技能二消耗'][i]=temp[1]
    # df['技能二持续'][i]=temp[2]
    df.loc[:,'技能二初始'][i]=temp[0]
    df.loc[:,'技能二消耗'][i]=temp[1]
    df.loc[:,'技能二持续'][i]=temp[2]
    print(name)

    # 再部署时间，部署费用,阻挡数,攻击间隔
    string='<td width="33.4%">'
    r_pos=r.text[r.text.find(string):]
    a=r_pos[findSubStr('>',r_pos,1)+len('>'):].split('s')[0]
    b=r_pos[findSubStr('>',r_pos,5)+len('>'):].split('\n')[0].split('→')[1]
    c=r_pos[findSubStr('>',r_pos,11)+len('>'):].split('\n')[0]
    if len(c.split('→'))==3:
        c=c.split('→')[1]
    d=r_pos[findSubStr('>',r_pos,15)+len('>'):].split('s')[0]
    # df['再部署时间'][i]=a
    # df['初始部署费用'][i]=b
    # df['阻挡数'][i]=c
    # df['攻击间隔'][i]=d
    # df['代号'][i]=name
    df.loc[:,'再部署时间'][i]=a
    df.loc[:,'初始部署费用'][i]=b
    df.loc[:,'阻挡数'][i]=c
    df.loc[:,'攻击间隔'][i]=d
    df.loc[:,'代号'][i]=name

    print(i,':',name,'finished')
    # time.sleep(5)

df[['阻挡数','初始部署费用','生命上限','攻击','防御','法术抗性','再部署时间','技能一初始','技能一消耗','技能一持续','技能二初始','技能二消耗','技能二持续']]=df[['阻挡数','初始部署费用','生命上限','攻击','防御','法术抗性','再部署时间','技能一初始','技能一消耗','技能一持续','技能二初始','技能二消耗','技能二持续']].astype('int')

output_path='D:\Code\GitHub\ArknightsResearch\wiki爬取干员信息.py'

# wb = xw.Book(output_path)#相当于直接模拟人的操作打开excel
# sht = wb.sheets.add(name="第3次",before=None,after=None)
# sht.range("A1").value = df.values
# wb.save()
# wb.close()

df.to_excel('result/wiki爬取干员信息5.xlsx',index=False)

# 解决pandas .to_excel不覆盖已有sheet的问题
# https://www.jb51.net/article/152453.htm
# https://zhuanlan.zhihu.com/p/85918022

# 解决A value is trying to be set on a copy of a slice from a DataFrame问题
# https://stackoverflow.com/questions/31468176/setting-values-on-a-copy-of-a-slice-from-a-dataframe?rq=1



# 修改方向
# 1.使用xpath解析HTML
# 2.新增干员英语日语背景等信息的获取
# 3.使用psycopg2向pgsql中插入数据
df = pd.read_sql_query(
    """SELECT DISTINCT *
       FROM operators
       ORDER BY 交易日期 DESC, 交易时间 DESC LIMIT 1;"""
       ,)



#架构:
# 1.选择干员名称
# 2.在数据库中判断如果不存在则创建新干员,并重新排序
# 3.从wiki查询数据,如果存在则直接插入数据库,失败则不管
