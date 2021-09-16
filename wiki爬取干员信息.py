import pandas as pd
import numpy as np
import time
excel_path=r"C:\Users\ASUS\OneDrive\文档\明日方舟.xlsx"

name_list=pd.read_excel(excel_path,sheet_name='干员信息')['干员']

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

df=pd.DataFrame(columns = ['代号','阻挡数','攻击间隔','生命上限','攻击','防御','法术抗性','再部署时间','初始部署费用','技能一初始','技能一消耗','技能一持续','技能二初始','技能二消耗','技能二持续'])

for i in range(len(name_list)):
    name=name_list[i]
    # name='棘刺'
    operator_url=wiki_url+name
    r = requests.get(operator_url)
            # 基本属性
    Attribute_list=['生命上限','攻击','防御','法术抗性']
    attribute_list=[]
    for Attribute in Attribute_list:
        Attribute_str='<th>{}\n</th>'.format(Attribute)

        #大标题定位
        r_pos=r.text[r.text.find(Attribute_str):][:500]
        #属性值
        attribute=int(r_pos[findSubStr('<td>',r_pos,3)+len('<td>'):].split('\n')[0])
        #对应信赖加成
        attribute_reliance=r_pos[findSubStr('<td>',r_pos,5)+len('<td>'):].split('\n')[0]
        if attribute_reliance=='':
            attribute_reliance=0
        else:
            attribute_reliance=int(attribute_reliance)
        attribute+=attribute_reliance
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
    df['技能一初始'][i]=temp[0]
    df['技能一消耗'][i]=temp[1]
    df['技能一持续'][i]=temp[2]

    skill2='<p><b>技能2（精英1开放）</b>'
    r_pos=r.text[r.text.find(skill2):]
    temp=[]
    temp.append(r_pos[findSubStr('<td>',r_pos,26)+len('<td>'):].split('\n')[0])#初始
    temp.append(r_pos[findSubStr('<td>',r_pos,27)+len('<td>'):].split('\n')[0])#消耗
    temp.append(r_pos[findSubStr('<td>',r_pos,28)+len('<td>'):].split('\n')[0])#持续
    for x in temp:
        if x=='':
            temp[temp.index(x)]=str(0)
    df['技能二初始'][i]=temp[0]
    df['技能二消耗'][i]=temp[1]
    df['技能二持续'][i]=temp[2]

    # 再部署时间，部署费用,阻挡数,攻击间隔
    string='<td width="33.4%">'
    r_pos=r.text[r.text.find(string):]
    a=r_pos[findSubStr('>',r_pos,1)+len('>'):].split('s')[0]
    b=r_pos[findSubStr('>',r_pos,5)+len('>'):].split('\n')[0].split('→')[1]
    c=r_pos[findSubStr('>',r_pos,11)+len('>'):].split('\n')[0]
    if len(c.split('→'))==3:
        c=c.split('→')[1]
    d=r_pos[findSubStr('>',r_pos,15)+len('>'):].split('s')[0]
    df['再部署时间'][i]=a
    df['初始部署费用'][i]=b
    df['阻挡数'][i]=c
    df['攻击间隔'][i]=d
    df['代号'][i]=name

    print(i,':',name,'finished')
    # time.sleep(5)

df[['阻挡数','生命上限','攻击','防御','法术抗性','再部署时间','初始部署费用','技能一初始','技能一消耗','技能一持续','技能二初始','技能二消耗','技能二持续']]=df[['阻挡数','生命上限','攻击','防御','法术抗性','再部署时间','初始部署费用','技能一初始','技能一消耗','技能一持续','技能二初始','技能二消耗','技能二持续']].astype('int')
df.to_excel('wiki爬取干员信息.xlsx',index=False)

