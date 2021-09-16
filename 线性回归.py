# 线性回归
import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from torch import nn, optim
from torch.autograd import Variable
import torch
import pandas as pd

plt.rcParams["font.family"] = "SimHei"  #中文显示


# 构建神经网模型
class LineraRegression(nn.Module):
    # 定义网络结构,一般把网络中具有可学习参数的层放在__init__()中
    def __init__(self):
        # 初始化nn.Module
        super(LineraRegression, self).__init__()
        self.fc = nn.Linear(1, 1)

    # 定义网络计算
    def forward(self, x):  # 前向计算，一般不写反向传播的函数，pytorch可以自动计算
        out = self.fc(x)
        return out


# 导入数据
df = pd.read_excel(r'C:\Users\ASUS\OneDrive\文档\明日方舟.xlsx', sheet_name='原始数据')
genre_list = df.columns.tolist()[1:]
temp = len(genre_list)

# 参数空间
p_space = pd.DataFrame(np.zeros([temp, temp]), dtype='int')
for i in range(8):
    p_space.iloc[i, i] = '(1,0)'
p_space.index = p_space.columns = genre_list
# 误差空间
loss_space = pd.DataFrame(np.zeros([temp, temp]))
for i in range(8):
    loss_space.iloc[i, i] = 0
loss_space.index = loss_space.columns = genre_list
# 标准对照表
# std_space = pd.DataFrame(np.zeros([24,1]))

combine_genre_list = list(itertools.combinations(genre_list, 2))

# std_space.append({combine_genre_list[0]:[1,2,3]}, ignore_index=True)

# 循环体
for genre in combine_genre_list:

    # 筛选要对比的两个流派的数据
    x_name = genre[0]
    y_name = genre[1]

    df1 = df[[x_name, y_name]]
    for i in range(len(df)):
        if np.isnan(df[x_name][i]) or np.isnan(df[y_name][i]):
            df1 = df1.drop(i)
    x_data = np.array(df1[x_name])
    y_data = np.array(df1[y_name])

    # # 画图
    # 设置xy轴刻度
    # x_major_locator = MultipleLocator(1)
    # y_major_locator = MultipleLocator(1)
    # plt.scatter(x_data, y_data, s=70, alpha=0.3)
    # plt.xlabel(str(x_name))
    # plt.ylabel(str(y_name))
    # plt.xlim(0, 14)
    # plt.ylim(0, 14)
    # ax = plt.gca()
    # ax.xaxis.set_major_locator(x_major_locator)
    # ax.yaxis.set_major_locator(y_major_locator)

    # 训练模型准备工作
    x_data = x_data.reshape(-1, 1)  # -1是自动匹配任意行，这里是100
    y_data = y_data.reshape(-1, 1)  # 也就是得到100行1列的数据
    # 把numpy数据变成tensor
    x_data = torch.FloatTensor(x_data)
    y_data = torch.FloatTensor(y_data)
    inputs = Variable(x_data)
    target = Variable(y_data)

    # 定义实例模型
    model = LineraRegression()
    # 定义代价函数
    mse_loss = nn.MSELoss()
    # 定义优化器
    optimizer = optim.SGD(model.parameters(), lr=0.01)  # 随机梯度下降法，lr是学习率

    # 训练模型
    model.train()
    for i in range(1001):
        out = model(inputs)
        # 计算loss
        loss = mse_loss(out, target)
        # 梯度清零,否则梯度会累加
        optimizer.zero_grad()
        # 计算梯度
        loss.backward()
        # 修改权值
        optimizer.step()
        if i % 200 == 0:
            print(i, loss.item())  # 训练1000次后，loss越来越小

    # 保存参数
    temp = []
    for name, parameter in model.named_parameters():
        print(name, ':', parameter)
        temp.append(parameter.item())
        # y=1.26*x+2.25
        print(parameter.item())
    a, b = "%.1f" % temp[0], "%.1f" % temp[1]
    c, d = "%.1f" % (1 / temp[0]), "%.1f" % (-temp[1] / temp[0])
    p_space[x_name][y_name] = '({},{})'.format(a, b)
    p_space[y_name][x_name] = '({},{})'.format(c, d)

    loss_num = "%.2f" % loss.item()
    loss_space[x_name][y_name] = loss_num
    loss_space[y_name][x_name] = loss_num

    temp = np.linspace(0, 24, 25)
    temp = temp.reshape(-1, 1)
    x_std = torch.FloatTensor(temp)
    y_std = model(x_std)

    # 画图(带回归直线)
    y_pred = model(inputs)
    plt.scatter(x_data, y_data, s=70, alpha=0.3)
    plt.plot(x_data,
             y_pred.data.numpy(),
             'r-',
             lw=3,
             label='y={0}x+{1}'.format(a, b))
    # 设置xy轴刻度
    x_major_locator = MultipleLocator(1)
    y_major_locator = MultipleLocator(1)

    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    ax.yaxis.set_major_locator(y_major_locator)
    plt.xlim(0, 13)
    plt.ylim(0, 20)
    plt.xlabel(str(x_name))
    plt.ylabel(str(y_name))
    plt.legend()
    plt.title('{}-{} 散点图  N={}'.format(x_name, y_name, len(df1)))
    plt.savefig('D:\Code\Python\Arknights\output_ori_gama\{}-{} 散点图'.format(
        x_name, y_name))
    # plt.show()
    plt.close()  # 防止数据重叠

p_space.to_excel(r'D:\Code\Python\Arknights\result', sheet_name=p_space)
loss_space.to_excel(r'D:\Code\Python\Arknights\result', sheet_name=loss)
loss_space.to_excel(r'D:\Code\Python\Arknights\result', sheet_name=loss)
print('finished')
