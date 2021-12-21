-- DROP TABLE IF EXISTS operators;--删库,慎用
-- DELETE FROM operators;--删库保留表结构,也慎用

--创建表结构
SELECT * FROM operators;

--查询表
CREATE TABLE operators(
    "干员" VARCHAR UNIQUE NOT NULL PRIMARY KEY,
    "稀有度" SMALLINT NOT NULL,
    "职业" VARCHAR NOT NULL,
    "职业编号" SMALLINT,
    "日本語" VARCHAR,
    "英语" VARCHAR,
    "序号" SMALLINT,
    "阻挡数" SMALLINT,
    "初始费用" SMALLINT,
    "生命值" SMALLINT,
    "攻击力" SMALLINT,
    "防御力" SMALLINT,
    "法抗" SMALLINT,
    "攻击间隔" FLOAT,
    "再部署时间" SMALLINT,
    "S1初动" SMALLINT,
    "S1消耗" SMALLINT,
    "S1持续" SMALLINT,
    "S2初动" SMALLINT,
    "S2消耗" SMALLINT,
    "S2持续" SMALLINT,
    "S3初动" SMALLINT,
    "S3消耗" SMALLINT,
    "S3持续" SMALLINT,
    "统计678章使用次数" SMALLINT,
    "技能2S2D" INTEGER,
    "S2技能DPS" SMALLINT,
    "S2普攻DPS" SMALLINT,
    "S2平均DPS" SMALLINT,
    "技能2S2H" SMALLINT,
    "S2技能HPS" SMALLINT,
    "S2普攻HPS" SMALLINT,
    "S2平均HPS" SMALLINT
);


--添加新列：职业编号
ALTER TABLE operators ADD 职业编号 smallint;

--修改职业列的名称为profession
ALTER TABLE operators RENAME profession TO 职业;

--插入新干员
INSERT INTO operators("干员","稀有度","职业")
VALUES('灵知',6,'辅助');

--删除干员
DELETE FROM operators WHERE 干员='测试干员2';

--清空整列数据
UPDATE operators SET s3初动=NULL;

--显示现有的模式搜寻顺序
SHOW search_path;
--修改模式搜寻顺序
SET search_path TO Arknights;

--按游戏内顺序查询表
SELECT * FROM operators
ORDER BY 稀有度 DESC,职业编号,干员;


--根据职业自动设置职业编号
UPDATE operators SET 职业编号=(CASE
    WHEN (职业='近卫') THEN 1
    WHEN (职业='狙击') THEN 2
    WHEN (职业='重装') THEN 3
    WHEN (职业='医疗') THEN 4
    WHEN (职业='辅助') THEN 5
    WHEN (职业='术士') THEN 6
    WHEN (职业='特种') THEN 7
    WHEN (职业='先锋') THEN 8 END)
WHERE 职业编号 IS NULL AND 职业 IS NOT NULL;


--根据游戏默认顺序重设"序号"
UPDATE operators AS o
SET "序号" = row_number
FROM (
    SELECT ROW_NUMBER() over(ORDER bY "稀有度" DESC,"职业编号","干员"),"干员"
    FROM operators) AS r
WHERE o."干员"=r."干员";


SELECT * FROM operators
ORDER BY "序号"