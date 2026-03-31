from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from datetime import datetime
from app.models.hot_food import HotFood
from app import db
from loguru import logger
import re
import os
import random
import urllib.parse

class XHSSeleniumCrawler:
    """使用Selenium模拟浏览器操作的小红书爬虫"""
    
    def __init__(self, cookies=None):
        self.driver = None
        self.cookies = cookies or self._load_cookies()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        try:
            self.driver = self._init_driver()
            if self.cookies:
                self._set_cookies()
        except Exception as e:
            logger.error(f"浏览器驱动初始化失败：{str(e)}")
            # 不抛出异常，让上层处理
    
    def _load_cookies(self):
        """从配置文件加载 Cookie"""
        try:
            from app.config import XHS_CONFIG
            cookies_str = XHS_CONFIG.get('cookies', '')
            if cookies_str:
                return json.loads(cookies_str)
            logger.info("未配置 Cookie，使用默认方式爬取")
        except Exception as e:
            logger.warning(f"加载 Cookie 失败：{str(e)}")
        return None
    
    def _init_driver(self):
        """初始化浏览器驱动"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # 随机选择 User-Agent
        user_agent = random.choice(self.user_agents)
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速
        chrome_options.add_argument("--disable-extensions")  # 禁用扩展
        chrome_options.add_argument("--disable-notifications")  # 禁用通知
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 防止被检测为自动化工具
        
        # 设置浏览器语言
        chrome_options.add_argument("--lang=zh-CN")
        
        # 尝试初始化浏览器
        driver = webdriver.Chrome(options=chrome_options)
        # 执行 JavaScript 代码，移除 webdriver 特征
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.implicitly_wait(10)  # 隐式等待
        logger.info(f"浏览器驱动初始化成功，使用 User-Agent: {user_agent}")
        return driver
    
    def _set_cookies(self):
        """设置 Cookie"""
        if not self.driver or not self.cookies:
            return
        
        try:
            # 先访问小红书主页，再设置 Cookie
            self.driver.get("https://www.xiaohongshu.com")
            time.sleep(2)
            
            for cookie in self.cookies:
                self.driver.add_cookie(cookie)
            
            logger.info(f"成功设置 {len(self.cookies)} 个 Cookie")
            # 重新加载页面以应用 Cookie
            self.driver.get("https://www.xiaohongshu.com")
            time.sleep(2)
        except Exception as e:
            logger.warning(f"设置 Cookie 失败：{str(e)}")
    
    def _random_delay(self, min_seconds=1, max_seconds=3):
        """随机延迟，模拟人工操作"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    def _scroll_page(self, scroll_times=5):
        """滚动页面，加载更多内容"""
        for i in range(scroll_times):
            # 随机滚动距离，避免机械滚动
            scroll_distance = random.randint(800, 1200)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
            # 随机延迟
            self._random_delay(1.5, 3.0)
        
        # 滚动到页面底部，确保加载所有内容
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self._random_delay(2, 4)
    
    def _parse_note(self, note):
        """解析单条笔记信息"""
        try:
            # 获取标题
            title_element = note.find_element(By.CSS_SELECTOR, "div[class*='title']")
            title = title_element.text.strip() if title_element else ""
            
            # 获取链接
            link_element = note.find_element(By.CSS_SELECTOR, "a[href*='explore']")
            link = link_element.get_attribute("href") if link_element else ""
            
            # 获取点赞数
            likes = 0
            try:
                likes_element = note.find_element(By.CSS_SELECTOR, "span[class*='like']")
                if likes_element:
                    likes_text = likes_element.text.strip()
                    likes = int(re.sub(r"\D", "", likes_text)) if likes_text else 0
            except Exception:
                pass
            
            # 获取评论数
            comments = 0
            try:
                comments_element = note.find_element(By.CSS_SELECTOR, "span[class*='comment']")
                if comments_element:
                    comments_text = comments_element.text.strip()
                    comments = int(re.sub(r"\D", "", comments_text)) if comments_text else 0
            except Exception:
                pass
            
            # 获取收藏数
            collection = 0
            try:
                collection_element = note.find_element(By.CSS_SELECTOR, "span[class*='collection']")
                if collection_element:
                    collection_text = collection_element.text.strip()
                    collection = int(re.sub(r"\D", "", collection_text)) if collection_text else 0
            except Exception:
                pass
            
            # 获取作者信息
            author = ""
            try:
                author_element = note.find_element(By.CSS_SELECTOR, "div[class*='author']")
                if author_element:
                    author = author_element.text.strip()
            except Exception:
                pass
            
            # 获取标签
            tags = []
            try:
                tag_elements = note.find_elements(By.CSS_SELECTOR, "span[class*='tag']")
                for tag_element in tag_elements:
                    tag_text = tag_element.text.strip()
                    if tag_text and tag_text.startswith('#'):
                        tags.append(tag_text[1:])  # 去除 # 符号
            except Exception:
                pass
            
            # 构造热点美食数据
            if title and link:
                hot_item = {
                    "title": title,
                    "link": link,
                    "likes": likes,
                    "comments": comments,
                    "collection": collection,
                    "author": author,
                    "tags": tags
                }
                logger.info(f"成功解析笔记：{title}")
                return hot_item
        except Exception as e:
            logger.warning(f"解析笔记失败：{str(e)}")
        return None
    
    def search_hot_food(self, keyword="美食", scroll_times=5, max_retries=3):
        """搜索热点美食（带重试机制）"""
        if not self.driver:
            logger.warning("浏览器驱动未初始化，无法执行爬取")
            return []
        
        retries = 0
        while retries < max_retries:
            try:
                # 对关键词进行编码
                encoded_keyword = urllib.parse.quote(keyword)
                # 打开小红书搜索页面
                search_url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_keyword}&source=web_search_result_notes"
                logger.info(f"开始爬取 {keyword} 的热点美食，第 {retries + 1} 次尝试")
                self.driver.get(search_url)
                
                # 等待页面加载
                self._random_delay(3, 5)
                
                # 处理可能的登录弹窗
                try:
                    # 尝试关闭登录弹窗
                    close_button = self.driver.find_element(By.CSS_SELECTOR, ".modal-close")
                    if close_button:
                        close_button.click()
                        self._random_delay(1, 2)
                        logger.info("成功关闭登录弹窗")
                except Exception as e:
                    logger.info(f"没有登录弹窗或关闭失败：{str(e)}")
                
                # 滚动页面，加载更多内容
                self._scroll_page(scroll_times)
                
                # 获取笔记元素 - 使用更通用的选择器
                note_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='note-item']")
                logger.info(f"找到 {len(note_elements)} 条笔记")
                
                hot_items = []
                for note in note_elements[:20]:  # 取前20条
                    hot_item = self._parse_note(note)
                    if hot_item:
                        hot_items.append(hot_item)
                
                if hot_items:
                    # 按点赞数排序
                    hot_items.sort(key=lambda x: x['likes'], reverse=True)
                    logger.info(f"成功解析 {len(hot_items)} 条笔记，爬取完成")
                    return hot_items
                else:
                    logger.warning("未获取到笔记数据，进行重试")
                    retries += 1
                    self._random_delay(5, 10)  # 重试前等待更长时间
                    
            except Exception as e:
                logger.error(f"搜索美食失败：{str(e)}")
                # 截图保存，方便调试
                try:
                    screenshot_path = f"screenshot_{int(time.time())}.png"
                    self.driver.save_screenshot(screenshot_path)
                    logger.info(f"已保存截图到 {screenshot_path}")
                except Exception:
                    pass
                
                retries += 1
                if retries < max_retries:
                    logger.info(f"第 {retries} 次重试中...")
                    self._random_delay(5, 10)
                else:
                    logger.error("达到最大重试次数，爬取失败")
                    return []
        
        return []
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.warning(f"关闭浏览器失败：{str(e)}")

def crawl_xhs_hot_food():
    """使用Selenium爬取小红书热点美食"""
    crawler = None
    try:
        # 动态导入，避免循环导入
        from app import create_app
        # 禁用调度器，避免重复启动
        import os
        os.environ['DISABLE_SCHEDULER'] = 'True'
        app = create_app()
        
        # 使用应用上下文
        with app.app_context():
            crawler = XHSSeleniumCrawler()
            
            # 搜索热点美食
            hot_items = crawler.search_hot_food("美食", scroll_times=3)
            
            if not hot_items:
                logger.warning("未获取到热点美食数据，保留原有数据")
                # 检查是否已有数据
                existing_count = HotFood.query.count()
                if existing_count > 0:
                    logger.info(f"保留原有{existing_count}条热点美食数据")
                else:
                    # 只有在没有现有数据时才使用模拟数据
                    logger.info("无现有数据，使用模拟数据")
                    mock_hot_foods = [
                        {
                            "food_name": "日式拉面",
                            "ingre_list": "小麦面粉,猪骨汤,叉烧,鸡蛋,葱",
                            "link": "https://www.xiaohongshu.com/explore/12345",
                            "hot_score": 12800,
                            "source": "小红书",
                            "tags": ["美食", "日式", "拉面"],
                            "image": "https://picsum.photos/seed/ramen/300/200"
                        },
                        {
                            "food_name": "泰式冬阴功汤",
                            "ingre_list": "香茅,柠檬叶,辣椒,虾,椰奶",
                            "link": "https://www.xiaohongshu.com/explore/12346",
                            "hot_score": 9500,
                            "source": "小红书",
                            "tags": ["美食", "泰式", "汤"],
                            "image": "https://picsum.photos/seed/tom-yum/300/200"
                        },
                        {
                            "food_name": "意式番茄意面",
                            "ingre_list": "意大利面,番茄,洋葱,大蒜,橄榄油",
                            "link": "https://www.xiaohongshu.com/explore/12347",
                            "hot_score": 8200,
                            "source": "小红书",
                            "tags": ["美食", "意式", "意面"],
                            "image": "https://picsum.photos/seed/pasta/300/200"
                        },
                        {
                            "food_name": "中式红烧肉",
                            "ingre_list": "五花肉,酱油,料酒,冰糖,姜",
                            "link": "https://www.xiaohongshu.com/explore/12348",
                            "hot_score": 15600,
                            "source": "小红书",
                            "tags": ["美食", "中式", "红烧肉"],
                            "image": "https://picsum.photos/seed/braised-pork/300/200"
                        },
                        {
                            "food_name": "韩式烤肉",
                            "ingre_list": "牛肉,韩式辣酱,大蒜,芝麻,生菜",
                            "link": "https://www.xiaohongshu.com/explore/12349",
                            "hot_score": 10300,
                            "source": "小红书",
                            "tags": ["美食", "韩式", "烤肉"],
                            "image": "https://picsum.photos/seed/korean-bbq/300/200"
                        }
                    ]
                    
                    for index, item in enumerate(mock_hot_foods):
                        try:
                            # 创建热点美食记录
                            hot_food = HotFood(
                                food_name=item['food_name'],
                                ingre_list=item['ingre_list'],
                                link=item['link'],
                                hot_score=item['hot_score'],
                                source=item['source'],
                                tags=json.dumps(item['tags']),
                                image=item['image'],
                                create_time=datetime.now()
                            )
                            hot_food.save()
                            
                        except Exception as e:
                            logger.warning(f"解析第{index}个热点美食失败：{str(e)}")
                            continue
                    
                    logger.info(f"小红书热点美食模拟数据加载完成，共{len(mock_hot_foods)}条")
                return
            
            # 清空旧数据
            HotFood.query.delete()
            
            for index, item in enumerate(hot_items):
                try:
                    # 提取标签，如果没有则使用默认标签
                    tags = item.get('tags', [])
                    if not tags:
                        tags = ["美食"]
                    
                    # 创建热点美食记录
                    hot_food = HotFood(
                        food_name=item['title'],
                        ingre_list=item['title'],  # 使用标题作为食材列表（实际需要解析详情页）
                        link=item['link'],
                        hot_score=item['likes'],
                        source="小红书",
                        tags=json.dumps(tags),
                        image="",  # 实际需要解析详情页获取图片
                        create_time=datetime.now()
                    )
                    hot_food.save()
                    logger.info(f"成功保存热点美食：{item['title']}")
                    
                except Exception as e:
                    logger.warning(f"解析第{index}个热点美食失败：{str(e)}")
                    continue
            
            logger.info(f"小红书热点美食爬取完成，共{len(hot_items)}条")
            
    except Exception as e:
        logger.error(f"小红书爬虫执行失败：{str(e)}")
        # 不抛出异常，保留原有数据
        logger.info("保留原有热点美食数据")
        # 检查是否已有数据
        from app import create_app
        # 禁用调度器
        import os
        os.environ['DISABLE_SCHEDULER'] = 'True'
        app = create_app()
        with app.app_context():
            existing_count = HotFood.query.count()
            if existing_count > 0:
                logger.info(f"保留原有{existing_count}条热点美食数据")
            else:
                # 只有在没有现有数据时才使用模拟数据
                logger.info("无现有数据，使用模拟数据")
                mock_hot_foods = [
                    {
                        "food_name": "日式拉面",
                        "ingre_list": "小麦面粉,猪骨汤,叉烧,鸡蛋,葱",
                        "link": "https://www.xiaohongshu.com/explore/12345",
                        "hot_score": 12800,
                        "source": "小红书",
                        "tags": ["美食", "日式", "拉面"],
                        "image": "https://picsum.photos/seed/ramen/300/200"
                    },
                    {
                        "food_name": "泰式冬阴功汤",
                        "ingre_list": "香茅,柠檬叶,辣椒,虾,椰奶",
                        "link": "https://www.xiaohongshu.com/explore/12346",
                        "hot_score": 9500,
                        "source": "小红书",
                        "tags": ["美食", "泰式", "汤"],
                        "image": "https://picsum.photos/seed/tom-yum/300/200"
                    }
                ]
                
                for index, item in enumerate(mock_hot_foods):
                    try:
                        # 创建热点美食记录
                        hot_food = HotFood(
                            food_name=item['food_name'],
                            ingre_list=item['ingre_list'],
                            link=item['link'],
                            hot_score=item['hot_score'],
                            source=item['source'],
                            tags=json.dumps(item['tags']),
                            image=item['image'],
                            create_time=datetime.now()
                        )
                        hot_food.save()
                        
                    except Exception as e:
                        logger.warning(f"解析第{index}个热点美食失败：{str(e)}")
                        continue
                
                logger.info(f"小红书热点美食模拟数据加载完成，共{len(mock_hot_foods)}条")
    finally:
        # 确保关闭浏览器
        if crawler:
            try:
                crawler.close()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.warning(f"关闭浏览器失败：{str(e)}")
