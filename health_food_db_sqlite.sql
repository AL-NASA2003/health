-- 健康饮食助手数据库表结构（SQLite版本）
-- 创建时间：2026-03-10

-- 1. 用户信息表
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    openid VARCHAR(100) NOT NULL UNIQUE,
    nickname VARCHAR(50) DEFAULT '',
    avatar VARCHAR(255) DEFAULT '',
    phone VARCHAR(20) DEFAULT '',
    gender TINYINT DEFAULT 0,
    age INT DEFAULT 0,
    height DECIMAL(5,1) DEFAULT 0,
    weight DECIMAL(5,1) DEFAULT 0,
    health_goal VARCHAR(50) DEFAULT '',
    dietary_preference VARCHAR(100) DEFAULT '',
    token VARCHAR(255) DEFAULT '',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_openid ON user(openid);

-- 2. 食材信息表
CREATE TABLE IF NOT EXISTS ingredient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingre_name VARCHAR(50) NOT NULL UNIQUE,
    calorie DECIMAL(10,2) DEFAULT 0,
    protein DECIMAL(10,2) DEFAULT 0,
    carb DECIMAL(10,2) DEFAULT 0,
    fat DECIMAL(10,2) DEFAULT 0,
    category VARCHAR(30) DEFAULT '',
    stock DECIMAL(10,2) DEFAULT 0,
    unit VARCHAR(10) DEFAULT 'g',
    image VARCHAR(255) DEFAULT '',
    expire_date DATE DEFAULT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_ingre_name ON ingredient(ingre_name);
CREATE INDEX IF NOT EXISTS idx_category ON ingredient(category);

-- 3. 食谱信息表
CREATE TABLE IF NOT EXISTS recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name VARCHAR(100) NOT NULL UNIQUE,
    calorie DECIMAL(10,2) DEFAULT 0,
    protein DECIMAL(10,2) DEFAULT 0,
    carb DECIMAL(10,2) DEFAULT 0,
    fat DECIMAL(10,2) DEFAULT 0,
    flavor VARCHAR(20) DEFAULT '',
    cook_type VARCHAR(20) DEFAULT '',
    suitable_crowd VARCHAR(100) DEFAULT '',
    cook_step TEXT,
    image VARCHAR(255) DEFAULT '',
    ingre_list VARCHAR(500) DEFAULT '',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_recipe_name ON recipe(recipe_name);
CREATE INDEX IF NOT EXISTS idx_flavor ON recipe(flavor);
CREATE INDEX IF NOT EXISTS idx_cook_type ON recipe(cook_type);

-- 4. 食谱食材关联表
CREATE TABLE IF NOT EXISTS recipe_ingredient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    weight DECIMAL(10,2) DEFAULT 0,
    unit VARCHAR(10) DEFAULT 'g'
);

-- 创建唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_recipe_ingredient ON recipe_ingredient(recipe_id, ingredient_id);

-- 5. 饮食记录表
CREATE TABLE IF NOT EXISTS diet_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    food_name VARCHAR(100) NOT NULL,
    food_type VARCHAR(20) DEFAULT '',
    meal_time VARCHAR(20) DEFAULT '',
    weight DECIMAL(10,2) DEFAULT 0,
    unit VARCHAR(10) DEFAULT 'g',
    calorie DECIMAL(10,2) DEFAULT 0,
    protein DECIMAL(10,2) DEFAULT 0,
    carb DECIMAL(10,2) DEFAULT 0,
    fat DECIMAL(10,2) DEFAULT 0,
    recipe_id INTEGER DEFAULT 0,
    image VARCHAR(255) DEFAULT '',
    notes TEXT,
    create_date DATE NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_id_diet ON diet_record(user_id);
CREATE INDEX IF NOT EXISTS idx_create_date ON diet_record(create_date);
CREATE INDEX IF NOT EXISTS idx_meal_time ON diet_record(meal_time);

-- 6. 用户食材表
CREATE TABLE IF NOT EXISTS user_ingredient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    weight DECIMAL(10,2) DEFAULT 0,
    unit VARCHAR(10) DEFAULT 'g',
    expiry_date DATE DEFAULT NULL,
    storage_location VARCHAR(50) DEFAULT '',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_user_ingredient ON user_ingredient(user_id, ingredient_id);

-- 7. 热点美食表
CREATE TABLE IF NOT EXISTS hot_food (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_name VARCHAR(100) NOT NULL,
    ingre_list VARCHAR(500) DEFAULT '',
    link VARCHAR(255) NOT NULL,
    hot_score INTEGER DEFAULT 0,
    source VARCHAR(50) DEFAULT '小红书',
    tags TEXT,
    image VARCHAR(255) DEFAULT '',
    cook_type VARCHAR(20) DEFAULT '',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_hot_score ON hot_food(hot_score);
CREATE INDEX IF NOT EXISTS idx_source ON hot_food(source);

-- 8. 手帐信息表
CREATE TABLE IF NOT EXISTS hand_account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    image VARCHAR(255) DEFAULT '',
    is_public TINYINT DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_id_hand ON hand_account(user_id);
CREATE INDEX IF NOT EXISTS idx_is_public ON hand_account(is_public);
CREATE INDEX IF NOT EXISTS idx_likes_hand ON hand_account(likes);

-- 9. 论坛帖子表
CREATE TABLE IF NOT EXISTS forum_post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    image VARCHAR(255) DEFAULT '',
    category VARCHAR(30) DEFAULT '',
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    is_top TINYINT DEFAULT 0,
    status TINYINT DEFAULT 1,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_id_forum ON forum_post(user_id);
CREATE INDEX IF NOT EXISTS idx_category ON forum_post(category);
CREATE INDEX IF NOT EXISTS idx_views ON forum_post(views);
CREATE INDEX IF NOT EXISTS idx_likes_forum ON forum_post(likes);
CREATE INDEX IF NOT EXISTS idx_status ON forum_post(status);

-- 10. 论坛评论表
CREATE TABLE IF NOT EXISTS comment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    target_type TINYINT NOT NULL,
    target_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    parent_id INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    status TINYINT DEFAULT 1,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_target ON comment(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_user_id_comment ON comment(user_id);
CREATE INDEX IF NOT EXISTS idx_parent_id ON comment(parent_id);
CREATE INDEX IF NOT EXISTS idx_status_comment ON comment(status);

-- 11. 用户收藏表
CREATE TABLE IF NOT EXISTS user_collection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recipe_id INTEGER DEFAULT NULL,
    post_id INTEGER DEFAULT NULL,
    hand_account_id INTEGER DEFAULT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_id ON user_collection(user_id);
CREATE INDEX IF NOT EXISTS idx_recipe_id ON user_collection(recipe_id);
CREATE INDEX IF NOT EXISTS idx_post_id ON user_collection(post_id);
CREATE INDEX IF NOT EXISTS idx_hand_account_id ON user_collection(hand_account_id);

-- 12. 用户点赞表
CREATE TABLE IF NOT EXISTS user_like (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    hot_food_id INTEGER DEFAULT NULL,
    post_id INTEGER DEFAULT NULL,
    comment_id INTEGER DEFAULT NULL,
    hand_account_id INTEGER DEFAULT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_id ON user_like(user_id);
CREATE INDEX IF NOT EXISTS idx_hot_food_id ON user_like(hot_food_id);
CREATE INDEX IF NOT EXISTS idx_post_id ON user_like(post_id);
CREATE INDEX IF NOT EXISTS idx_comment_id ON user_like(comment_id);
CREATE INDEX IF NOT EXISTS idx_hand_account_id ON user_like(hand_account_id);

-- 13. 饮水记录表
CREATE TABLE IF NOT EXISTS water_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_id_water ON water_record(user_id);
CREATE INDEX IF NOT EXISTS idx_create_time_water ON water_record(create_time);

-- 14. 运动记录表
CREATE TABLE IF NOT EXISTS exercise_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    duration INTEGER NOT NULL,
    calories INTEGER NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_id_exercise ON exercise_record(user_id);
CREATE INDEX IF NOT EXISTS idx_create_time_exercise ON exercise_record(create_time);

-- 15. 健康指数记录表
CREATE TABLE IF NOT EXISTS health_index_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    height REAL NOT NULL,
    weight REAL NOT NULL,
    age INTEGER NOT NULL,
    gender INTEGER NOT NULL,
    bmi REAL NOT NULL,
    bmi_status VARCHAR(20) NOT NULL,
    bmr INTEGER NOT NULL,
    ideal_weight VARCHAR(20) NOT NULL,
    daily_calories INTEGER NOT NULL,
    health_score INTEGER NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_id_health ON health_index_record(user_id);
CREATE INDEX IF NOT EXISTS idx_create_time_health ON health_index_record(create_time);

-- 16. 饮食统计记录表
CREATE TABLE IF NOT EXISTS diet_stat_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    record_date DATE NOT NULL,
    total_calories INTEGER NOT NULL,
    total_protein REAL NOT NULL,
    total_carb REAL NOT NULL,
    total_fat REAL NOT NULL,
    total_water INTEGER NOT NULL,
    total_exercise_duration INTEGER NOT NULL,
    total_exercise_calories INTEGER NOT NULL,
    net_calories INTEGER NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_id_diet_stat ON diet_stat_record(user_id);
CREATE INDEX IF NOT EXISTS idx_record_date_diet_stat ON diet_stat_record(record_date);

-- 17. 用户目标表
CREATE TABLE IF NOT EXISTS user_goal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    daily_calorie_goal INTEGER NOT NULL,
    daily_water_goal INTEGER NOT NULL,
    daily_exercise_goal INTEGER NOT NULL,
    health_goal VARCHAR(50) NOT NULL,
    dietary_preference VARCHAR(50) NOT NULL,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_id_goal ON user_goal(user_id);
