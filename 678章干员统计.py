import pandas as pd

None2elitism_excel = "E:\下载\无精二表 (9).xlsx"
chapter8 = pd.read_excel(None2elitism_excel, sheet_name='第八章')
chapter7 = pd.read_excel(None2elitism_excel, sheet_name='第七章')
chapter6 = pd.read_excel(None2elitism_excel, sheet_name='第六章')


# 选择干员列
chapter8.iloc[:, 6:]

# 拼接干员列


def tongji(chapter):
    tongji = pd.DataFrame([])  # 长度=(行数+1)*8
    for x in range(6, 14):
        tongji = pd.concat([tongji, chapter.iloc[:, x]])
    return tongji


# 统计
result = pd.concat([tongji(chapter6), tongji(chapter7), tongji(chapter8)])
print(result.value_counts())
result.value_counts().to_excel(r"E:\Desktop\result.xlsx")
