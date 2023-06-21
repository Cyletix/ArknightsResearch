'''
Description: 文件描述
Author: Cyletix
Date: 2021-12-24 15:17:41
LastEditTime: 2023-01-27 18:20:43
FilePath: \ArknightsResearch\干员名阵列打印.py
'''


# 从PostgreSQL获取
def print_matrix(column):  
    from mypgsql import get_tuple
    name_tuple=get_tuple()
    name_list = []
    col_num = 1
    row_num = 0
    row = 1
    prt_str = ''
    for name in name_tuple:
        name=name[0]
        if name == '斯卡蒂' or name == '浊心斯卡蒂':  # 排除红蓝蒂
            continue
        elif name == '阿米娅（近卫）':  # 剑兔别名转换
            name = '近卫阿米娅'
        name_list.append(name)
        if col_num == column:
            split_sign = '\n'
            col_num = 0
            row += 1
        else:
            split_sign = '	'
        prt_str += (name + split_sign)
        col_num += 1
        row_num += 1

    print(prt_str)

    with open(r'result/干员阵列({}×{}).txt'.format(row, column), 'w', encoding='utf-8') as f:
        f.write(prt_str)


# 从excel获取
def print_matrix_from_xls(column): 
    import pandas as pd
    df = pd.read_excel(
        'D:\OneDrive\Code\Github\ArknightsResearch\明日方舟.xlsx', sheet_name='干员信息')
    name_list = list(df['干员'])
    count = len(name_list)
    col_num = 1
    row_num = 0
    row = 1
    prt_str = ''
    add_explain = ''
    for name in name_list:
        # add_explain=' 排除红蓝蒂'
        # if name == '斯卡蒂' or name == '浊心斯卡蒂':  # 排除红蓝蒂
        #     continue
        if name == '阿米娅（近卫）':  # 剑兔别名转换
            name = '近卫阿米娅'
        if col_num == column:
            split_sign = '\n'
            col_num = 0
            row += 1
        else:
            split_sign = '	'
        prt_str += (name + split_sign)
        col_num += 1
        row_num += 1

    with open(r'result/干员阵列({0}×{1}-{2}){3}.txt'.format(row, column, count, add_explain), 'w', encoding='utf-8') as f:
        f.write(prt_str)




#最新版
def copy_to_clipboard(column):
    from pyperclip import copy
    from mypgsql import pg_query
    query_str='''
        SELECT 干员 FROM arknights.sd 
        JOIN arknights."职业编号" pn USING("职业")
        WHERE 上线时间 BETWEEN '2019-04-30' AND '2022/8/11 16:00:00'
        ORDER BY 稀有度 DESC,pn.职业编号,干员
    '''
    query_result=[x[0] for x in pg_query(query_str)]
    col_num = 1
    row_num = 0
    row = 1
    prt_str = ''

    print('总数为:',len(query_result))
    

    for name in query_result:
        # add_explain=' 排除红蓝蒂'
        # if name == '斯卡蒂' or name == '浊心斯卡蒂':  # 排除红蓝蒂
        #     continue
        if name == '阿米娅(近卫)':  # 剑兔别名转换
            name = '近卫阿米娅'
        if col_num == column: #到头换行,一般一行是13/10/8列
            split_sign = '\n'
            col_num = 0
            row += 1 
        else:
            split_sign = '	'
        prt_str += (name + split_sign)
        col_num += 1
        row_num += 1
    copy(prt_str)
    return query_result





if __name__ == '__main__':
    column = 13  # 在此处修改要限制的列数
    # print_matrix(column)
    # print_matrix_from_xls(column)
    copy_to_clipboard(column)




############################结果展示###################################
# 伺夜	嵯峨	风笛	琴柳	推进之王	焰尾	艾丽妮	百炼嘉维尔	陈	赫拉格	煌	棘刺	玛恩纳
# 帕拉斯	山	史尔特尔	斯卡蒂	耀骑士临光	银灰	斥罪	号角	泥岩	年	塞雷娅	森蚺	瑕光
# 星熊	W	菲亚梅塔	黑	鸿雪	灰烬	假日威龙陈	空弦	迷迭香	能天使	远牙	早露	艾雅法拉
# 澄闪	黑键	卡涅利安	刻俄柏	莫斯提马	夕	伊芙利特	异客	凯尔希	流明	闪灵	夜莺	安洁莉娜
# 白铁	灵知	铃兰	令	麦哲伦	浊心斯卡蒂	阿	多萝西	歌蕾蒂娅	归溟幽灵鲨	傀影	老鲤	水月
# 温蒂	德克萨斯	格拉尼	极境	贾维	凛冬	谜图	苇草	晓歌	野鬃	夜半	近卫阿米娅	柏喙
# 暴行	鞭刃	布洛卡	赤冬	达格达	断崖	芙兰卡	海沫	拉普兰德	龙舌兰	诗怀雅	燧石	星极
# 炎客	因陀罗	幽灵鲨	羽毛笔	战车	铸铁	拜松	暴雨	车尔尼	吽	灰毫	火神	极光
# 可颂	雷蛇	临光	暮落	闪击	石棉	埃拉托	安哲拉	奥斯塔	白金	承曦格雷伊	寒芒克洛丝	灰喉
# 蓝毒	普罗旺斯	熔泉	慑砂	守林人	四月	送葬人	陨星	子月	阿米娅	爱丽丝	薄绿	和弦
# 惊蛰	苦艾	莱恩哈特	洛洛	蜜蜡	蚀清	特米米	天火	星源	雪绒	炎狱炎熔	耶拉	夜魔
# 至简	白面鸮	赫默	华法琳	蜜莓	明椒	桑葚	图耶	微风	锡兰	絮雨	亚叶	濯尘芙蓉
# 初雪	但书	格劳克斯	海蒂	九色鹿	空	掠风	梅尔	巫恋	稀音	夏栎	月禾	真理
# 贝娜	风丸	红	槐琥	见行者	卡夫卡	罗宾	绮良	狮蝎	食铁兽	霜华	乌有	雪雉
# 崖心	豆苗	红豆	清道夫	桃金娘	讯使	艾丝黛尔	缠丸	杜宾	断罪者	芳汀	杰克	刻刀
# 猎蜂	罗小黑	慕斯	石英	霜叶	宴	古米	坚雷	角峰	泡泡	蛇屠箱	安比尔	白雪
# 红云	杰西卡	流星	梅	铅踝	松果	酸糖	布丁	格雷伊	卡达	深靛	夜烟	远山
# 调香师	褐果	嘉维尔	末药	清流	苏苏洛	波登可	地灵	罗比菈塔	深海色	阿消	暗索	孑
# 砾	伊桑	芬	翎羽	香草	玫兰莎	泡普卡	月见夜	斑点	卡缇	米格鲁	安德切尔	克洛丝
# 空爆	史都华德	炎熔	安赛尔	芙蓉	梓兰	夜刀	黑角	巡林者	12F	杜林	Castle-3	正义骑士号
# Lancet-2	THRM-EX	
