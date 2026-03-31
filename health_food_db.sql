-- 健康饮食助手数据库表结构
-- 创建时间：2026-03-10

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS health_food DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE health_food;

-- 1. 用户信息表
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    openid VARCHAR(100) NOT NULL UNIQUE COMMENT '微信openid',
    nickname VARCHAR(50) DEFAULT '' COMMENT '用户昵称',
    avatar VARCHAR(255) DEFAULT '' COMMENT '用户头像',
    phone VARCHAR(20) DEFAULT '' COMMENT '手机号码',
    gender TINYINT DEFAULT 0 COMMENT '性别 0-未知 1-男 2-女',
    age INT DEFAULT 0 COMMENT '年龄',
    height DECIMAL(5,1) DEFAULT 0 COMMENT '身高(cm)',
    weight DECIMAL(5,1) DEFAULT 0 COMMENT '体重(kg)',
    health_goal VARCHAR(50) DEFAULT '' COMMENT '健康目标',
    dietary_preference VARCHAR(100) DEFAULT '' COMMENT '饮食偏好',
    token VARCHAR(255) DEFAULT '' COMMENT '登录令牌',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_openid (openid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

-- 2. 食材信息表
CREATE TABLE IF NOT EXISTS ingredient (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '食材ID',
    ingre_name VARCHAR(50) NOT NULL UNIQUE COMMENT '食材名称',
    calorie DECIMAL(10,2) DEFAULT 0 COMMENT '热量(大卡/100g)',
    protein DECIMAL(10,2) DEFAULT 0 COMMENT '蛋白质(g/100g)',
    carb DECIMAL(10,2) DEFAULT 0 COMMENT '碳水化合物(g/100g)',
    fat DECIMAL(10,2) DEFAULT 0 COMMENT '脂肪(g/100g)',
    category VARCHAR(30) DEFAULT '' COMMENT '食材类别',
    unit VARCHAR(10) DEFAULT 'g' COMMENT '计量单位',
    image VARCHAR(255) DEFAULT '' COMMENT '食材图片',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_ingre_name (ingre_name),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='食材信息表';

-- 3. 食谱信息表
CREATE TABLE IF NOT EXISTS recipe (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '食谱ID',
    recipe_name VARCHAR(100) NOT NULL UNIQUE COMMENT '食谱名称',
    calorie DECIMAL(10,2) DEFAULT 0 COMMENT '热量(大卡/份)',
    protein DECIMAL(10,2) DEFAULT 0 COMMENT '蛋白质(g/份)',
    carb DECIMAL(10,2) DEFAULT 0 COMMENT '碳水化合物(g/份)',
    fat DECIMAL(10,2) DEFAULT 0 COMMENT '脂肪(g/份)',
    flavor VARCHAR(20) DEFAULT '' COMMENT '口味',
    cook_type VARCHAR(20) DEFAULT '' COMMENT '烹饪方式',
    suitable_crowd VARCHAR(100) DEFAULT '' COMMENT '适合人群',
    cook_step TEXT COMMENT '烹饪步骤',
    image VARCHAR(255) DEFAULT '' COMMENT '食谱图片',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_recipe_name (recipe_name),
    INDEX idx_flavor (flavor),
    INDEX idx_cook_type (cook_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='食谱信息表';

-- 4. 食谱食材关联表
CREATE TABLE IF NOT EXISTS recipe_ingredient (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '关联ID',
    recipe_id INT NOT NULL COMMENT '食谱ID',
    ingredient_id INT NOT NULL COMMENT '食材ID',
    weight DECIMAL(10,2) DEFAULT 0 COMMENT '食材用量',
    unit VARCHAR(10) DEFAULT 'g' COMMENT '计量单位',
    FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(id) ON DELETE CASCADE,
    UNIQUE KEY uk_recipe_ingredient (recipe_id, ingredient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='食谱食材关联表';

-- 5. 饮食记录表
CREATE TABLE IF NOT EXISTS diet_record (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    food_name VARCHAR(100) NOT NULL COMMENT '食物名称',
    food_type VARCHAR(20) DEFAULT '' COMMENT '食物类型',
    meal_time VARCHAR(20) DEFAULT '' COMMENT '用餐时间',
    weight DECIMAL(10,2) DEFAULT 0 COMMENT '重量',
    unit VARCHAR(10) DEFAULT 'g' COMMENT '计量单位',
    calorie DECIMAL(10,2) DEFAULT 0 COMMENT '热量(大卡)',
    protein DECIMAL(10,2) DEFAULT 0 COMMENT '蛋白质(g)',
    carb DECIMAL(10,2) DEFAULT 0 COMMENT '碳水化合物(g)',
    fat DECIMAL(10,2) DEFAULT 0 COMMENT '脂肪(g)',
    recipe_id INT DEFAULT 0 COMMENT '关联食谱ID',
    image VARCHAR(255) DEFAULT '' COMMENT '食物图片',
    notes TEXT COMMENT '备注',
    create_date DATE NOT NULL COMMENT '记录日期',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_create_date (create_date),
    INDEX idx_meal_time (meal_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='饮食记录表';

-- 6. 用户食材表
CREATE TABLE IF NOT EXISTS user_ingredient (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    user_id INT NOT NULL COMMENT '用户ID',
    ingredient_id INT NOT NULL COMMENT '食材ID',
    weight DECIMAL(10,2) DEFAULT 0 COMMENT '库存重量',
    unit VARCHAR(10) DEFAULT 'g' COMMENT '计量单位',
    expiry_date DATE DEFAULT NULL COMMENT '过期日期',
    storage_location VARCHAR(50) DEFAULT '' COMMENT '存放位置',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_ingredient (user_id, ingredient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户食材表';

-- 7. 热点美食表
CREATE TABLE IF NOT EXISTS hot_food (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    food_name VARCHAR(100) NOT NULL COMMENT '美食名称',
    ingre_list VARCHAR(500) DEFAULT '' COMMENT '食材组成',
    link VARCHAR(255) NOT NULL COMMENT '小红书链接',
    hot_score INT DEFAULT 0 COMMENT '热度值',
    source VARCHAR(50) DEFAULT '小红书' COMMENT '来源',
    tags TEXT COMMENT '标签',
    image VARCHAR(255) DEFAULT '' COMMENT '图片链接',
    cook_type VARCHAR(20) DEFAULT '' COMMENT '烹饪方式',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '爬取时间',
    INDEX idx_hot_score (hot_score),
    INDEX idx_source (source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='热点美食表';

-- 8. 手帐信息表
CREATE TABLE IF NOT EXISTS hand_account (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '手帐ID',
    user_id INT NOT NULL COMMENT '用户ID',
    title VARCHAR(100) NOT NULL COMMENT '手帐标题',
    content TEXT COMMENT '手帐内容',
    image VARCHAR(255) DEFAULT '' COMMENT '手帐图片',
    is_public TINYINT DEFAULT 0 COMMENT '是否公开 0-私有 1-公开',
    likes INT DEFAULT 0 COMMENT '点赞数',
    comments INT DEFAULT 0 COMMENT '评论数',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_public (is_public),
    INDEX idx_likes (likes)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='手帐信息表';

-- 9. 论坛帖子表
CREATE TABLE IF NOT EXISTS forum_post (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '帖子ID',
    user_id INT NOT NULL COMMENT '用户ID',
    title VARCHAR(100) NOT NULL COMMENT '帖子标题',
    content TEXT COMMENT '帖子内容',
    image VARCHAR(255) DEFAULT '' COMMENT '帖子图片',
    category VARCHAR(30) DEFAULT '' COMMENT '帖子分类',
    views INT DEFAULT 0 COMMENT '浏览数',
    likes INT DEFAULT 0 COMMENT '点赞数',
    comments INT DEFAULT 0 COMMENT '评论数',
    is_top TINYINT DEFAULT 0 COMMENT '是否置顶',
    status TINYINT DEFAULT 1 COMMENT '状态 1-正常 0-禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_views (views),
    INDEX idx_likes (likes),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='论坛帖子表';

-- 10. 论坛评论表
CREATE TABLE IF NOT EXISTS comment (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评论ID',
    user_id INT NOT NULL COMMENT '用户ID',
    target_type TINYINT NOT NULL COMMENT '目标类型 1-帖子 2-手帐',
    target_id INT NOT NULL COMMENT '目标ID',
    content TEXT NOT NULL COMMENT '评论内容',
    parent_id INT DEFAULT 0 COMMENT '父评论ID',
    likes INT DEFAULT 0 COMMENT '点赞数',
    status TINYINT DEFAULT 1 COMMENT '状态 1-正常 0-禁用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_target (target_type, target_id),
    INDEX idx_user_id (user_id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='论坛评论表';

-- 11. 用户收藏表
CREATE TABLE IF NOT EXISTS user_collection (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '收藏ID',
    user_id INT NOT NULL COMMENT '用户ID',
    collection_type TINYINT NOT NULL COMMENT '收藏类型 1-食谱 2-手帐 3-帖子',
    target_id INT NOT NULL COMMENT '目标ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_collection (user_id, collection_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏表';

-- 12. 用户点赞表
CREATE TABLE IF NOT EXISTS user_like (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '点赞ID',
    user_id INT NOT NULL COMMENT '用户ID',
    like_type TINYINT NOT NULL COMMENT '点赞类型 1-帖子 2-手帐 3-评论',
    target_id INT NOT NULL COMMENT '目标ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_like (user_id, like_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户点赞表';

-- 初始化基础数据

-- 初始化用户数据（示例）
INSERT INTO user (openid, nickname, avatar, age, height, weight, health_goal) VALUES
('mock_openid_123', '测试用户', 'https://picsum.photos/seed/avatar/100/100', 25, 175.0, 65.0, '减脂')
ON DUPLICATE KEY UPDATE nickname = VALUES(nickname);

-- 初始化食材数据
INSERT INTO ingredient (ingre_name, calorie, protein, carb, fat, category) VALUES
('鸡胸肉', 165, 31.0, 0.0, 3.6, '肉类'),
('西兰花', 34, 2.8, 7.0, 0.4, '蔬菜'),
('燕麦', 389, 16.9, 66.0, 6.9, '谷物'),
('鲈鱼', 105, 18.6, 0.0, 3.1, '鱼类'),
('番茄', 18, 0.9, 3.9, 0.2, '蔬菜'),
('鸡蛋', 155, 13.0, 1.1, 11.0, '蛋类'),
('牛奶', 42, 3.4, 5.0, 1.0, '乳制品'),
('苹果', 52, 0.3, 13.8, 0.2, '水果'),
('香蕉', 89, 1.1, 22.8, 0.3, '水果'),
('大米', 130, 2.7, 28.2, 0.3, '谷物')
ON DUPLICATE KEY UPDATE calorie = VALUES(calorie), protein = VALUES(protein), carb = VALUES(carb), fat = VALUES(fat);

-- 初始化食谱数据
INSERT INTO recipe (recipe_name, calorie, protein, carb, fat, flavor, cook_type, suitable_crowd, cook_step) VALUES
('低脂鸡胸肉沙拉', 280, 32.0, 15.0, 8.0, '清淡', '凉拌', '减脂人群', '1. 鸡胸肉切块腌制10分钟\n2. 煎至两面金黄\n3. 与蔬菜混合，淋上橄榄油和柠檬汁'),
('清蒸鲈鱼', 180, 28.0, 5.0, 6.0, '清淡', '清蒸', '所有人群', '1. 鲈鱼洗净，划几刀\n2. 放入葱姜蒜，淋上料酒\n3. 大火蒸10-12分钟\n4. 出锅淋上蒸鱼豉油'),
('燕麦蓝莓粥', 220, 8.0, 42.0, 4.0, '清淡', '煮', '早餐', '1. 燕麦加水煮开\n2. 小火慢煮15分钟\n3. 加入蓝莓和蜂蜜\n4. 搅拌均匀即可'),
('西兰花炒虾仁', 200, 25.0, 10.0, 8.0, '清淡', '炒', '健身人群', '1. 虾仁去壳去虾线\n2. 西兰花切小朵焯水\n3. 热锅少油，先炒虾仁\n4. 加入西兰花翻炒，调味即可'),
('番茄牛腩', 350, 22.0, 18.0, 20.0, '酸甜', '炖', '增肌人群', '1. 牛腩切块焯水\n2. 番茄切块\n3. 热锅炒番茄出汁\n4. 加入牛腩炖煮1小时')
ON DUPLICATE KEY UPDATE calorie = VALUES(calorie), protein = VALUES(protein), carb = VALUES(carb), fat = VALUES(fat);

-- 初始化食谱食材关联
INSERT INTO recipe_ingredient (recipe_id, ingredient_id, weight, unit) VALUES
(1, 1, 100, 'g'),  -- 鸡胸肉沙拉 - 鸡胸肉
(1, 2, 150, 'g'),  -- 鸡胸肉沙拉 - 西兰花
(2, 4, 200, 'g'),  -- 清蒸鲈鱼 - 鲈鱼
(3, 3, 50, 'g'),   -- 燕麦蓝莓粥 - 燕麦
(4, 2, 100, 'g'),  -- 西兰花炒虾仁 - 西兰花
(4, 6, 50, 'g'),   -- 西兰花炒虾仁 - 鸡蛋
(5, 1, 150, 'g'),  -- 番茄牛腩 - 鸡胸肉
(5, 5, 100, 'g')   -- 番茄牛腩 - 番茄
ON DUPLICATE KEY UPDATE weight = VALUES(weight);

-- 初始化热点美食数据
INSERT INTO hot_food (food_name, ingre_list, link, hot_score, tags, cook_type) VALUES
('春季养生汤品推荐：银耳莲子汤', '银耳,莲子,红枣,冰糖', 'https://www.xiaohongshu.com/explore/123456', 1234, '["养生", "汤品"]', '炖'),
('低脂减肥餐食谱分享', '鸡胸肉,西兰花,橄榄油', 'https://www.xiaohongshu.com/explore/234567', 2345, '["减肥", "低脂"]', '凉拌'),
('高蛋白健身餐制作指南', '鸡蛋,牛奶,燕麦', 'https://www.xiaohongshu.com/explore/345678', 1890, '["健身", "高蛋白"]', '煮'),
('宝宝辅食：营养蔬菜泥', '胡萝卜,土豆,西兰花', 'https://www.xiaohongshu.com/explore/456789', 987, '["辅食", "营养"]', '蒸'),
('懒人快手菜：15分钟搞定晚餐', '番茄,鸡蛋,面条', 'https://www.xiaohongshu.com/explore/567890', 3456, '["快手菜", "晚餐"]', '炒')
ON DUPLICATE KEY UPDATE hot_score = VALUES(hot_score);

-- 初始化饮食记录数据
INSERT INTO diet_record (user_id, food_name, food_type, meal_time, weight, calorie, protein, carb, fat, create_date) VALUES
(1, '燕麦粥', '主食', '早餐', 200, 180, 6, 32, 3, CURDATE()),
(1, '鸡胸肉沙拉', '菜式', '午餐', 300, 280, 35, 15, 8, CURDATE()),
(1, '清蒸鲈鱼', '菜式', '晚餐', 250, 200, 28, 5, 6, CURDATE())
ON DUPLICATE KEY UPDATE weight = VALUES(weight), calorie = VALUES(calorie);

-- 初始化用户食材数据
INSERT INTO user_ingredient (user_id, ingredient_id, weight, unit) VALUES
(1, 1, 500, 'g'),  -- 鸡胸肉
(1, 2, 300, 'g'),  -- 西兰花
(1, 3, 1000, 'g'), -- 燕麦
(1, 4, 200, 'g'),  -- 鲈鱼
(1, 5, 500, 'g')   -- 番茄
ON DUPLICATE KEY UPDATE weight = VALUES(weight);

-- 初始化论坛帖子数据
INSERT INTO forum_post (user_id, title, content, category) VALUES
(1, '分享我的减脂餐食谱', '坚持了3个月，成功减了10斤，分享我的减脂餐食谱...', '减脂'),
(1, '健身增肌饮食指南', '增肌期如何安排饮食？分享我的经验...', '增肌'),
(1, '家常快手菜推荐', '上班党必备，15分钟搞定的健康晚餐...', '家常菜')
ON DUPLICATE KEY UPDATE content = VALUES(content);

-- 初始化手帐数据
INSERT INTO hand_account (user_id, title, content, is_public) VALUES
(1, '我的健康饮食日记', '今天开始记录我的健康饮食之旅...', 1),
(1, '一周减脂餐计划', '制定了一周的减脂餐计划，希望能坚持...', 1)
ON DUPLICATE KEY UPDATE content = VALUES(content);

-- 初始化评论数据
INSERT INTO comment (user_id, target_type, target_id, content) VALUES
(1, 1, 1, '很棒的分享，我也试试！'),
(1, 1, 2, '感谢分享，很有用！'),
(1, 2, 1, '加油！一起坚持！')
ON DUPLICATE KEY UPDATE content = VALUES(content);

-- 初始化用户收藏数据
INSERT INTO user_collection (user_id, collection_type, target_id) VALUES
(1, 1, 1),  -- 收藏食谱1
(1, 1, 2),  -- 收藏食谱2
(1, 2, 1)   -- 收藏手帐1
ON DUPLICATE KEY UPDATE create_time = CURRENT_TIMESTAMP;

-- 初始化用户点赞数据
INSERT INTO user_like (user_id, like_type, target_id) VALUES
(1, 1, 1),  -- 点赞帖子1
(1, 2, 1),  -- 点赞手帐1
(1, 3, 1)   -- 点赞评论1
ON DUPLICATE KEY UPDATE create_time = CURRENT_TIMESTAMP;

SELECT '数据库表结构创建完成！' AS message;
SELECT '基础数据初始化完成！' AS message;
