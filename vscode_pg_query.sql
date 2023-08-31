--这是在vscode创建的sql文件,通过pg插件服务可以直接在vscode中使用PostgreSQL数据库
SELECT *
FROM arknights.character_table;
SELECT *
FROM arknights.source_data;
SELECT column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'source_data';