import numpy as np
import matplotlib.pyplot as plt


while(True):
    #生成随机二值矩阵
    arr = np.random.randint(0, 2, size=(8, 11))

    #1.洞穴生成
    # for i in range(2, len(arr) - 2):
    #     for j in range(2, len(arr) - 2):
    #         if arr[i-1][j]+arr[i+1][j]+arr[i][j-1]+arr[i][j+1]<1:
    #             arr[i][j]=0

    #2.柏林噪声
    #固定的输入必须有固定的输出
    #不同尺度噪声的叠加
    plt.imshow(arr, interpolation='nearest', cmap='bone', origin='lower')
    input('按任意键继续')
    plt.close()
#根据像素绘制图片 origin表示渐变程度
# plt.colorbar()
#显示像素与数据对比
# plt.xticks(())
# plt.yticks(())
#不显示坐标轴刻度
print()