import pyperclip
import pandas as pd
import os


# https://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88

# 获取剪贴板中的文本数据
data = pyperclip.paste()

# data='''塑心
# Virtuosa
# LT22
# 巫役
# 拉特兰
# 拉特兰
# 萨科塔
# 1201
# 485
# 109
# 15
# 70s
# 16
# 1
# 1.6s
# 女
# 远程位
# 限定寻访
# 元素
# 支援
# 攻击造成法术伤害，可以造成元素损伤
# '''



# 获取当前操作系统的换行符
newline = os.linesep

# 将文本按换行符拆分成行
lines = data.strip().split(newline)


# 固定的表头
headers = [
    '中文', 'english', 'japanese', 'codename', '子职业', '势力', '出身地', '种族', '生命值',
    '攻击', '防御', '法术抗性', '再部署时间', '部署费用', '阻挡', '攻击间隔', '性别', '位置', '获取方式', '标签', '标签2', '标签3', '标签4', '特性'
]

# 获取数据行
rows = [group.split('\n') for group in '\n'.join(lines).split('\n\n')]

# 将数据转换为字典列表
dict_list = []
for row_group in rows:

    # 判断第一个纯数字的位置
    num_index = next((i for i, field in enumerate(row_group) if field.isdigit()), None)
    # 如果有缺失 'japanese' 字段，则在对应位置插入 -
    if num_index == 7:
        row_group.insert(2, '-')

    # 判断标签列的个数
    tags_count = len(row_group)-19
    # 调整字段
    # tags=list(row_group[-tags_count:-1])
    # del row_group[-tags_count:-1]
    # row_group.insert(-1,tags)

    # 压缩为字典
    dict_row = dict(zip(headers, row_group))
    dict_list.append(dict_row)

print(dict_list)

# 将字典列表转换为 DataFrame
df = pd.DataFrame(dict_list)

# 复制 DataFrame 到剪贴板
df.to_clipboard(index=False, header=True, sep='\t')






# 塑心
# Virtuosa
# LT22
# 巫役
# 拉特兰
# 拉特兰
# 萨科塔
# 1201
# 485
# 109
# 15
# 70s
# 16
# 1
# 1.6s
# 女
# 远程位
# 限定寻访
# 元素
# 支援
# 攻击造成法术伤害，可以造成元素损伤