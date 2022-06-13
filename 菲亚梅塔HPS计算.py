'''
Description: 用于计算红蒂加持下的菲亚梅塔血量能否稳定在触发二层天赋的80%血量
Author: Cyletix
Date: 2022-03-15 17:18:32
LastEditTime: 2022-03-27 11:51:52
FilePath: \ArknightsResearch\菲亚梅塔HPS计算.py
'''
import numpy as np
from matplotlib import pyplot as plt
#%% 变量
max_hp = 1540
skd_atk_base = 355
skd_atk_ptt = 27

#%% 不变量
hp_cost_ps = 0.05
max_hp_range = [1232, 1540]

#%% 导出量
hp = max_hp  # hp初始值
hp_nxt = hp
skd_atk = skd_atk_base + skd_atk_ptt  # 斯卡蒂攻击
skd_hlt_ps = skd_atk * 0.17
skd_hlt_pf = skd_atk * 0.1

#%% 模型

n = 10  # 迭代次数
hp_rcd = []

for i in range(n):
    hp = hp_nxt
    hp_nxt = hp + skd_hlt_pf
    if hp_nxt > max_hp:
        hp_nxt = max_hp

    # if n % 10 == 0:
    hp_nxt = np.ceil(hp_nxt - hp_nxt * hp_cost_ps)
    hp_rcd.append(hp)
    if hp_nxt <= 0:
        break
print(hp_rcd)
# %%
plt.plot(hp_rcd)
plt.show()
# %%
