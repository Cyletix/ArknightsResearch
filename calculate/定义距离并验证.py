import pandas as pd


#定义参数空间的距离
def distance(m=[], n=[]):
    return ((m[0] - n[0])**2 + (m[1] - n[1])**2)**(0.5)


df = pd.read_csv('D:\Code\Python\Arknights\p_space.csv', index_col=0)
df.index = df.columns

a1, b1 = list(map(float, df['2907']['2704'][1:-1].split(',')))
a2, b2 = list(map(float, df['2907']['1806'][1:-1].split(',')))
a3, b3 = list(map(float, df['2704']['1806'][1:-1].split(',')))

a3_cal = a1 / a2
b3_cal = b1 - a3 * b2

distance([a3, b3], [a3_cal, b3_cal])

print()
