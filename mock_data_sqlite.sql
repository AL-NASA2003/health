-- 健康饮食助手模拟数据（SQLite版本）
-- 创建时间：2026-03-10

-- 初始化用户数据（示例）
INSERT OR IGNORE INTO user (openid, nickname, avatar, age, height, weight, health_goal) VALUES
('mock_openid_123', '测试用户', 'https://picsum.photos/seed/avatar/100/100', 25, 175.0, 65.0, '减脂');

-- 初始化食材数据
INSERT OR IGNORE INTO ingredient (ingre_name, calorie, protein, carb, fat, category) VALUES
('鸡胸肉', 165, 31.0, 0.0, 3.6, '肉类'),
('西兰花', 34, 2.8, 7.0, 0.4, '蔬菜'),
('燕麦', 389, 16.9, 66.0, 6.9, '谷物'),
('鲈鱼', 105, 18.6, 0.0, 3.1, '鱼类'),
('番茄', 18, 0.9, 3.9, 0.2, '蔬菜'),
('鸡蛋', 155, 13.0, 1.1, 11.0, '蛋类'),
('牛奶', 42, 3.4, 5.0, 1.0, '乳制品'),
('苹果', 52, 0.3, 13.8, 0.2, '水果'),
('香蕉', 89, 1.1, 22.8, 0.3, '水果'),
('大米', 130, 2.7, 28.2, 0.3, '谷物');

-- 初始化食谱数据
INSERT OR IGNORE INTO recipe (recipe_name, calorie, protein, carb, fat, flavor, cook_type, suitable_crowd, cook_step) VALUES
('低脂鸡胸肉沙拉', 280, 32.0, 15.0, 8.0, '清淡', '凉拌', '减脂人群', '1. 鸡胸肉切块腌制10分钟\n2. 煎至两面金黄\n3. 与蔬菜混合，淋上橄榄油和柠檬汁'),
('清蒸鲈鱼', 180, 28.0, 5.0, 6.0, '清淡', '清蒸', '所有人群', '1. 鲈鱼洗净，划几刀\n2. 放入葱姜蒜，淋上料酒\n3. 大火蒸10-12分钟\n4. 出锅淋上蒸鱼豉油'),
('燕麦蓝莓粥', 220, 8.0, 42.0, 4.0, '清淡', '煮', '早餐', '1. 燕麦加水煮开\n2. 小火慢煮15分钟\n3. 加入蓝莓和蜂蜜\n4. 搅拌均匀即可'),
('西兰花炒虾仁', 200, 25.0, 10.0, 8.0, '清淡', '炒', '健身人群', '1. 虾仁去壳去虾线\n2. 西兰花切小朵焯水\n3. 热锅少油，先炒虾仁\n4. 加入西兰花翻炒，调味即可'),
('番茄牛腩', 350, 22.0, 18.0, 20.0, '酸甜', '炖', '增肌人群', '1. 牛腩切块焯水\n2. 番茄切块\n3. 热锅炒番茄出汁\n4. 加入牛腩炖煮1小时');

-- 初始化食谱食材关联
INSERT OR IGNORE INTO recipe_ingredient (recipe_id, ingredient_id, weight, unit) VALUES
(1, 1, 100, 'g'),  -- 鸡胸肉沙拉 - 鸡胸肉
(1, 2, 150, 'g'),  -- 鸡胸肉沙拉 - 西兰花
(2, 4, 200, 'g'),  -- 清蒸鲈鱼 - 鲈鱼
(3, 3, 50, 'g'),   -- 燕麦蓝莓粥 - 燕麦
(4, 2, 100, 'g'),  -- 西兰花炒虾仁 - 西兰花
(4, 6, 50, 'g'),   -- 西兰花炒虾仁 - 鸡蛋
(5, 1, 150, 'g'),  -- 番茄牛腩 - 鸡胸肉
(5, 5, 100, 'g');   -- 番茄牛腩 - 番茄

-- 初始化热点美食数据
INSERT OR IGNORE INTO hot_food (food_name, ingre_list, link, hot_score, tags, cook_type) VALUES
('春季养生汤品推荐：银耳莲子汤', '银耳,莲子,红枣,冰糖', 'https://www.xiaohongshu.com/explore/123456', 1234, '["养生", "汤品"]', '炖'),
('低脂减肥餐食谱分享', '鸡胸肉,西兰花,橄榄油', 'https://www.xiaohongshu.com/explore/234567', 2345, '["减肥", "低脂"]', '凉拌'),
('高蛋白健身餐制作指南', '鸡蛋,牛奶,燕麦', 'https://www.xiaohongshu.com/explore/345678', 1890, '["健身", "高蛋白"]', '煮'),
('宝宝辅食：营养蔬菜泥', '胡萝卜,土豆,西兰花', 'https://www.xiaohongshu.com/explore/456789', 987, '["辅食", "营养"]', '蒸'),
('懒人快手菜：15分钟搞定晚餐', '番茄,鸡蛋,面条', 'https://www.xiaohongshu.com/explore/567890', 3456, '["快手菜", "晚餐"]', '炒');

-- 初始化饮食记录数据
INSERT OR IGNORE INTO diet_record (user_id, food_name, food_type, meal_time, weight, calorie, protein, carb, fat, create_date) VALUES
(1, '燕麦粥', '主食', '早餐', 200, 180, 6, 32, 3, date('now')),
(1, '鸡胸肉沙拉', '菜式', '午餐', 300, 280, 35, 15, 8, date('now')),
(1, '清蒸鲈鱼', '菜式', '晚餐', 250, 200, 28, 5, 6, date('now'));

-- 初始化用户食材数据
INSERT OR IGNORE INTO user_ingredient (user_id, ingredient_id, weight, unit) VALUES
(1, 1, 500, 'g'),  -- 鸡胸肉
(1, 2, 300, 'g'),  -- 西兰花
(1, 3, 1000, 'g'), -- 燕麦
(1, 4, 200, 'g'),  -- 鲈鱼
(1, 5, 500, 'g');   -- 番茄

-- 初始化论坛帖子数据
INSERT OR IGNORE INTO forum_post (user_id, title, content, category) VALUES
(1, '分享我的减脂餐食谱', '坚持了3个月，成功减了10斤，分享我的减脂餐食谱...', '减脂'),
(1, '健身增肌饮食指南', '增肌期如何安排饮食？分享我的经验...', '增肌'),
(1, '家常快手菜推荐', '上班党必备，15分钟搞定的健康晚餐...', '家常菜');

-- 初始化手帐数据
INSERT OR IGNORE INTO hand_account (user_id, title, content, is_public) VALUES
(1, '我的健康饮食日记', '今天开始记录我的健康饮食之旅...', 1),
(1, '一周减脂餐计划', '制定了一周的减脂餐计划，希望能坚持...', 1);

-- 初始化评论数据
INSERT OR IGNORE INTO comment (user_id, target_type, target_id, content) VALUES
(1, 1, 1, '很棒的分享，我也试试！'),
(1, 1, 2, '感谢分享，很有用！'),
(1, 2, 1, '加油！一起坚持！');

-- 初始化用户收藏数据
INSERT OR IGNORE INTO user_collection (user_id, recipe_id) VALUES
(1, 1),  -- 收藏食谱1
(1, 2);  -- 收藏食谱2

INSERT OR IGNORE INTO user_collection (user_id, hand_account_id) VALUES
(1, 1);  -- 收藏手帐1

-- 初始化用户点赞数据
INSERT OR IGNORE INTO user_like (user_id, post_id) VALUES
(1, 1);  -- 点赞帖子1

INSERT OR IGNORE INTO user_like (user_id, hand_account_id) VALUES
(1, 1);  -- 点赞手帐1

INSERT OR IGNORE INTO user_like (user_id, comment_id) VALUES
(1, 1);  -- 点赞评论1
