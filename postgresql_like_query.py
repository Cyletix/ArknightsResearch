"""
Author: Cyletix 1016120209@qq.com
Date: 2024-05-13 18:34:25
LastEditors: Cyletix 1016120209@qq.com
LastEditTime: 2024-05-13 23:37:08
FilePath: \ArknightsResearch\postgresql_like_query.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
"""

import pandas as pd
import duckdb

# 定义 Excel 文件路径
file_path = "D:/OneDrive/Code/Project/ArknightsResearch/result/干员信息.xlsx"

# 读取指定的 Sheets
sheets = ["干员信息", "googlesheet", "tencentsheet", "character_table", "result"]
dfs = pd.read_excel(file_path, sheet_name=sheets)

# 创建 DuckDB 连接
conn = duckdb.connect(database=":memory:")  # 使用内存数据库

# 将每个 DataFrame 注册为虚拟表
for sheet, df in zip(sheets, dfs.values()):
    conn.register("{}".format(sheet), df)

# 执行 SQL 查询，假设我们要从干员信息表中选取某些数据
# query = """
# SELECT
#     干员,
#     MAX(稀有度) AS 稀有度,
#     MAX(职业) AS 职业,
#     MAX(子职业) AS 子职业,
#     MAX(势力) AS 势力,
#     MAX(出身地) AS 出身地,
#     MAX(种族) AS 种族,
#     MAX(职业编号) AS 职业编号,
#     MAX(部署位) AS 部署位,
#     MAX(日本語) AS 日本語,
#     MAX(英语) AS 英语,
#     MAX(序号) AS 序号,
#     MAX(阻挡数) AS 阻挡数,
#     MAX(初始部署费用) AS 初始部署费用,
#     MAX(生命上限) AS 生命上限,
#     MAX(攻击) AS 攻击,
#     MAX(防御) AS 防御,
#     MAX(法术抗性) AS 法术抗性,
#     MAX(攻击间隔) AS 攻击间隔,
#     MAX(再部署时间) AS 再部署时间,
#     MAX(生命信赖加成) AS 生命信赖加成,
#     MAX(攻击信赖加成) AS 攻击信赖加成,
#     MAX(防御信赖加成) AS 防御信赖加成,
#     MAX(潜能2) AS 潜能2,
#     MAX(潜能3) AS 潜能3,
#     MAX(潜能4) AS 潜能4,
#     MAX(潜能5) AS 潜能5,
#     MAX(潜能6) AS 潜能6,
#     MAX(技能一初始) AS 技能一初始,
#     MAX(技能一消耗) AS 技能一消耗,
#     MAX(技能一持续) AS 技能一持续,
#     MAX(技能二初始) AS 技能二初始,
#     MAX(技能二消耗) AS 技能二消耗,
#     MAX(技能二持续) AS 技能二持续,
#     MAX(技能三初始) AS 技能三初始,
#     MAX(技能三消耗) AS 技能三消耗,
#     MAX(技能三持续) AS 技能三持续,
#     MAX(技能2s2d) AS 技能2s2d,
#     MAX(s2技能dps) AS s2技能dps,
#     MAX(s2普攻dps) AS s2普攻dps,
#     MAX(s2平均dps) AS s2平均dps,
#     MAX(技能2s2h) AS 技能2s2h,
#     MAX(s2技能hps) AS s2技能hps,
#     MAX(s2普攻hps) AS s2普攻hps,
#     MAX(s2平均hps) AS s2平均hps,
#     MAX(上线时间) AS 上线时间,
#     MAX(统计678章使用次数) AS 统计678章使用次数,
#     MAX(总使用次数) AS 总使用次数,
#     MAX(首字母) AS 首字母,
#     MAX(codename) AS codename,
#     MAX(获取方式) AS 获取方式,
#     MAX(获取方式2) AS 获取方式2,
#     MAX(获取方式3) AS 获取方式3,
#     MAX(获取方式4) AS 获取方式4,
#     MAX(标签) AS 标签,
#     MAX(标签2) AS 标签2,
#     MAX(标签3) AS 标签3,
#     MAX(特性) AS 特性,
#     MAX(特性2) AS 特性2
# FROM googlesheet
# GROUP BY 干员;

# """

query = """
SELECT
    COALESCE(r.干员, o.干员) AS 干员,
    COALESCE(o.序号, r.序号) AS 序号,
    COALESCE(r.稀有度, o.稀有度) AS 稀有度,
    COALESCE(r.职业, o.职业) AS 职业,
    r.子职业 AS 子职业,
    r.势力 AS 势力,
    r.出身地 AS 出身地,
    r.种族 AS 种族,
    COALESCE(r.职业编号, o.职业编号) AS 职业编号,
    r.部署位 AS 部署位,
    COALESCE(r.日本語, o.日本語) AS 日本語,
    COALESCE(r.英语, o.英语) AS 英语,
    COALESCE(r.阻挡数,CAST(o.阻挡数 AS VARCHAR)) AS 阻挡数,
    COALESCE(r.初始部署费用,CAST(o.初始费用 AS VARCHAR)) AS 初始部署费用,
    COALESCE(o.生命值, r.生命上限) AS 生命上限,
    COALESCE(o.攻击力, r.攻击) AS 攻击,
    COALESCE(o.防御力, r.防御) AS 防御,
    COALESCE(o.法抗, r.法术抗性) AS 法术抗性,
    COALESCE(o.攻击间隔, r.攻击间隔) AS 攻击间隔,
    COALESCE(o.再部署时间, r.再部署时间) AS 再部署时间,
    COALESCE(o.s1初动, r.技能一初始) AS 技能一初始,
    COALESCE(o.s1消耗, r.技能一消耗) AS 技能一消耗,
    COALESCE(o.s1持续, r.技能一持续) AS 技能一持续,
    COALESCE(o.s2初动, r.技能二初始) AS 技能二初始,
    COALESCE(o.s2消耗, r.技能二消耗) AS 技能二消耗,
    COALESCE(o.s2持续, r.技能二持续) AS 技能二持续,
    COALESCE(o.s3初动, r.技能三初始) AS 技能三初始,
    COALESCE(o.s3消耗, r.技能三消耗) AS 技能三消耗,
    COALESCE(o.s3持续, r.技能三持续) AS 技能三持续,
    COALESCE(o.统计678章使用次数, r.统计678章使用次数) AS 统计678章使用次数,
    COALESCE(o.总使用次, r.总使用次数) AS 总使用次数,
    r.首字母,
    r.codename,
    r.获取方式,
    r.获取方式2,
    r.获取方式3,
    r.获取方式4,
    r.标签,
    r.标签2,
    r.标签3,
    r.特性,
    r.特性2,
    r.潜能2,
    r.潜能3,
    r.潜能4,
    r.潜能5,
    r.潜能6,
    r.攻击信赖加成,
    r.防御信赖加成,
    r.生命信赖加成,
    r.技能2s2d,
    r.s2技能dps,
    r.s2普攻dps,
    r.s2平均dps,
    r.技能2s2h,
    r.s2技能hps,
    r.s2普攻hps,
    r.s2平均hps,
    r.上线时间
FROM result r
FULL OUTER JOIN 干员信息 o ON r.干员 = o.干员
GROUP BY r.干员, o.干员;
"""


# 执行查询并获取结果
result = conn.execute(query).fetchdf()

# 显示结果
print(result)

# 关闭 DuckDB 连接
conn.close()

if input("输入Y确认写入 Excel 文件") == "Y":
    # 将 DataFrame 写入 Excel 文件的 'result' sheet
    with pd.ExcelWriter(file_path, engine="openpyxl", mode="a") as writer:
        result.to_excel(writer, sheet_name="result", index=False)
