import sqlite3

# 连接到数据库
conn = sqlite3.connect('health_food.db')
cursor = conn.cursor()

# 检查所有表
print("数据库中的表:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

# 检查热点美食表结构
print("\nhot_food表结构:")
cursor.execute("PRAGMA table_info(hot_food);")
columns = cursor.fetchall()
for column in columns:
    print(f"- {column[1]}: {column[2]}")

# 检查热点美食表中的数据
print("\nhot_food表中的数据:")
cursor.execute("SELECT COUNT(*) FROM hot_food;")
count = cursor.fetchone()[0]
print(f"共有 {count} 条记录")

# 查看前5条记录
if count > 0:
    print("\n前5条记录:")
    cursor.execute("SELECT id, food_name, hot_score FROM hot_food LIMIT 5;")
    records = cursor.fetchall()
    for record in records:
        print(f"ID: {record[0]}, 名称: {record[1]}, 热度: {record[2]}")

# 检查食谱表中的数据
print("\nrecipe表中的数据:")
cursor.execute("SELECT COUNT(*) FROM recipe;")
count = cursor.fetchone()[0]
print(f"共有 {count} 条记录")

# 查看前5条记录
if count > 0:
    print("\n前5条记录:")
    cursor.execute("SELECT id, recipe_name, calorie FROM recipe LIMIT 5;")
    records = cursor.fetchall()
    for record in records:
        print(f"ID: {record[0]}, 名称: {record[1]}, 热量: {record[2]}")

# 关闭连接
conn.close()
