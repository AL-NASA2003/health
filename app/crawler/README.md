# 小红书爬虫使用说明

## 功能特点

基于开源项目 [Python-XHS-CrawlerAndEmoANAL](https://github.com/Zoe-juwubafff/Python-XHS-CrawlerAndEmoANAL.git) 优化，具有以下特点：

1. **自动分页爬取** - 支持多页数据爬取（最多11页，220条）
2. **Cookie管理** - 支持自定义Cookie，提高爬取成功率
3. **智能延迟** - 随机延迟避免被封
4. **数据解析** - 自动解析笔记详情、标签、图片等
5. **热度计算** - 根据点赞、收藏、评论数计算热度值
6. **数据库存储** - 自动保存到MySQL数据库

## 环境要求

- Python 3.8 - 3.9（推荐3.8）
- MySQL 5.7+
- 依赖库：`requests`, `sqlalchemy`, `loguru`

## 安装依赖

```bash
pip install requests sqlalchemy loguru pymysql
```

## 获取Cookie

### 方法一：浏览器开发者工具

1. 打开 Chrome 浏览器
2. 访问 https://www.xiaohongshu.com/
3. 登录你的小红书账号
4. 按 F12 打开开发者工具
5. 切换到 "Network" 标签
6. 刷新页面，找到任意请求
7. 在 "Headers" 中找到 "Cookie"
8. 复制完整的Cookie值

### 方法二：浏览器插件

1. 安装 "EditThisCookie" 或 "Cookie-Editor" 插件
2. 访问小红书并登录
3. 点击插件图标，导出Cookie
4. 复制Cookie值

## 配置参数

在 `app/config.py` 中添加：

```python
# 小红书爬虫配置
XHS_COOKIE = "你的小红书Cookie"
XHS_KEYWORD = "美食"  # 搜索关键词
XHS_MAX_PAGES = 11  # 最大爬取页数
```

## 使用方法

### 方法一：直接运行

```bash
cd c:\Users\luohu\Desktop\health
python -c "from app.crawler.xhs_crawler_v2 import crawl_xhs_hot_food; crawl_xhs_hot_food()"
```

### 方法二：在代码中调用

```python
from app.crawler.xhs_crawler_v2 import crawl_xhs_hot_food

# 使用Cookie爬取
crawl_xhs_hot_food(
    cookie="你的Cookie",
    keyword="美食",
    max_pages=11
)
```

### 方法三：定时任务

在 `app/__init__.py` 中配置：

```python
from app.crawler.xhs_crawler_v2 import crawl_xhs_hot_food

# 启动定时任务（每24小时爬取一次）
scheduler.add_job(crawl_xhs_hot_food, "interval", hours=24)
```

## 常见问题

### 1. 爬取数据为空

**原因：** Cookie无效或过期

**解决方法：**
- 重新获取Cookie
- 使用手机验证码登录后获取Cookie
- 更换网络环境

### 2. 显示"爬取完毕"但数据很少

**原因：** 小红书限制，一个关键词最多220条

**解决方法：**
- 更换关键词
- 等待一段时间后再爬取

### 3. 所有笔记都不允许查看

**原因：** Cookie未正确获取

**解决方法：**
- 使用手机验证码登录
- 更换浏览器重新登录
- 更换网络环境

### 4. 爬取速度慢

**原因：** 避免被封，设置了随机延迟

**解决方法：**
- 可以修改 `time.sleep(random.uniform(1, 3))` 中的延迟时间
- 但不建议设置太短，容易被封

## 数据字段说明

爬取的数据包含以下字段：

- `food_name` - 美食名称（笔记标题）
- `ingre_list` - 食材组成（笔记描述）
- `link` - 小红书链接
- `hot_score` - 热度值（点赞+收藏×2+评论×3）
- `source` - 来源（固定为"小红书"）
- `tags` - 标签列表
- `image` - 图片链接
- `create_time` - 爬取时间

## 注意事项

1. **Cookie有效期** - Cookie会过期，需要定期更新
2. **爬取频率** - 不要频繁爬取，建议24小时一次
3. **数据限制** - 一个关键词最多220条（11页）
4. **网络环境** - 建议使用稳定的网络环境
5. **账号安全** - 不要使用主账号，建议使用小号

## 技术支持

- 开源项目：https://github.com/Zoe-juwubafff/Python-XHS-CrawlerAndEmoANAL.git
- 小红书开放平台：https://open.xiaohongshu.com/

## 免责声明

本爬虫仅用于学习和研究目的，请遵守小红书的使用条款和相关法律法规。不得用于商业用途或侵犯他人隐私。
