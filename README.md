# 简介

这是个人兴趣发起的一些关于明日方舟的一些数值计算、统计、回归分析和实用小工具，不定期更新，可能会一直鸽下去，一切取决于我的心情和工作是否忙。如有兴趣可以一起制作或根据此项目发起一个分支等方式，都是可以接受的。

This is some numerical calculations, statistics, regression analysis and practical gadgets about Tomorrow’s Ark initiated by personal interest. It is updated from time to time and may be shelved forever, it all depends on my mood and whether my work is busy. If you are interested, you can make it together or initiate a branch based on this project etc., all acceptable.

目前有以下子项目在开发计划中(无限咕咕咕...):

1. 自动辅助制表(Automatic Auxiliary Tabulation)

2. 爬取干员信息(Operator Information Database)

3. 对应理论(Correspondence Theory)

4. 地图难度计算(Map Difficulty Calculation)

# 1.自动辅助制表

* [x] av/BV/https地址之间的转换

* [x] 根据BV或链接获取视频发布时间/作者信息

* [ ] 自动填写腾讯在线文档(difficult)

* [ ] 在arkrec.com提交信息(difficult)

# 2.干员数据库

* [x] 建立数据库，确认数据库字段

* [x] 从PRTS获取干员信息的html文件

* [ ] 处理html文件得到干员信息

* [x] 从数据库导出信息到Excel表格

* [ ] DPS计算(difficult)

  ## 老入库流程

* [ ] get_op_info.py    获取干员信息

* [ ] 手动填写到    明日方舟.xlsx    表格

* [ ] 运行kettle工程，导入PostgreSQL数据库

  ## 新入库流程

* [ ] get_op_info_new.py 获取干员信息后自动插入到Arknights.sd.source_data数据库

* [ ] 用kettle工程/SQL语句/Python脚本对sd数据二次处理

* [ ] 插入到public业务表

# 3.对应理论

* [x] 收集不同流派的极限人数信息

* [x] 两两组合线性回归

* [ ] 假定新的对应关系(difficult)

* [x] 根据对应关系进行回归计算

* [ ] 评估准确性与合理性,找到最优方案(difficult)

# 4.地图难度计算

* [ ] 导入地图信息(difficult)

* [ ] 随机生成地图(difficult)

* [ ] 分析，量化影响因素(difficult)

* [ ] 根据所有影响因素得出总难度

* [ ] 评估准确性与合理性,找到最优方案(difficult)