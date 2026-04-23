import time
import json
from datetime import datetime
from app.models.hot_food import HotFood
from app import db
from loguru import logger
import re
import random
import urllib.parse
import pandas as pd
import os
from app.utils.data_processor import process_food_data

# 尝试导入DrissionPage，如果失败则使用模拟数据
DrissionPage_available = False
try:
    from DrissionPage import ChromiumPage
    DrissionPage_available = True
    logger.info("DrissionPage模块导入成功")
except ImportError:
    logger.warning("DrissionPage模块未安装，将使用模拟数据")

class XHSDrissionCrawler:
    """使用DrissionPage的小红书爬虫"""
    
    def __init__(self, cookies=None, force_login=False):
        self.page = None
        self.cookies = cookies or self._load_cookies()
        self.force_login = force_login
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15.7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15.7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        if DrissionPage_available:
            try:
                logger.info(f"初始化浏览器...")
                self.page = self._init_page()
                logger.info(f"浏览器已启动！")
                if self.cookies:
                    self._set_cookies()
                elif self.force_login:
                    # 强制登录
                    logger.info("强制登录中...")
                    if not self.login():
                        logger.error("登录失败，无法继续爬取")
                else:
                    # 不强制登录，但先访问主页
                    logger.info("访问小红书主页...")
                    self.page.get("https://www.xiaohongshu.com")
            except Exception as e:
                logger.error(f"页面初始化失败：{str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                # 不抛出异常，让上层处理
        else:
            logger.warning("DrissionPage不可用，跳过页面初始化")
    
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
    
    def _init_page(self):
        """初始化DrissionPage"""
        # 随机选择 User-Agent
        user_agent = random.choice(self.user_agents)
        # 创建页面对象
        page = ChromiumPage()
        # 设置User-Agent
        page.set.user_agent(user_agent)
        # 设置页面加载超时时间
        page.set.timeouts(page_load=15)
        logger.info(f"页面初始化成功，使用 User-Agent: {user_agent}")
        return page
    
    def login(self):
        """网页扫码登录"""
        if not self.page:
            logger.error("页面未初始化，无法执行登录")
            return False
        
        try:
            # 访问小红书登录页面
            self.page.get("https://www.xiaohongshu.com")
            logger.info("请在浏览器中扫码登录小红书")
            
            # 等待用户扫码登录
            # 检查是否登录成功
            for i in range(60):  # 等待60秒
                time.sleep(1)
                # 检查是否登录成功（通过检查页面是否包含用户信息）
                try:
                    # 尝试获取用户头像或用户名
                    user_element = self.page.ele('.user-avatar', timeout=0)
                    if user_element:
                        logger.info("登录成功")
                        # 保存登录状态
                        self.cookies = self.page.cookies.all()
                        return True
                except Exception:
                    pass
                
                # 检查是否有登录弹窗
                try:
                    # 尝试关闭登录弹窗
                    close_button = self.page.ele('.modal-close', timeout=0)
                    if close_button:
                        close_button.click()
                        logger.info("关闭登录弹窗")
                except Exception:
                    pass
            
            logger.error("登录超时")
            return False
        except Exception as e:
            logger.error(f"登录失败：{str(e)}")
            return False
    
    def _set_cookies(self):
        """设置 Cookie"""
        if not self.page or not self.cookies:
            return
        
        try:
            # 先访问小红书主页，再设置 Cookie
            self.page.get("https://www.xiaohongshu.com")
            time.sleep(2)
            
            for cookie in self.cookies:
                self.page.cookies.add(cookie)
            
            logger.info(f"成功设置 {len(self.cookies)} 个 Cookie")
            # 重新加载页面以应用 Cookie
            self.page.get("https://www.xiaohongshu.com")
            time.sleep(2)
        except Exception as e:
            logger.warning(f"设置 Cookie 失败：{str(e)}")
    
    def _random_delay(self, min_seconds=0.5, max_seconds=1.5):
        """随机延迟，模拟人工操作"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    def _scroll_page(self, scroll_times=3):
        """滚动页面，加载更多内容"""
        for i in range(scroll_times):
            # 随机滚动距离，避免机械滚动
            scroll_distance = random.randint(1000, 1500)
            self.page.scroll.down(scroll_distance)
            # 随机延迟
            self._random_delay(0.8, 1.5)
        
        # 滚动到页面底部，确保加载所有内容
        self.page.scroll.to_bottom()
        self._random_delay(1, 2)
    
    def _parse_note(self, note):
        """解析单条笔记信息"""
        try:
            # 等待元素加载
            self._random_delay(0.2, 0.5)
            
            # 获取标题
            title_element = note.ele('.title', timeout=2)
            title = title_element.text if title_element else ""
            
            # 获取链接
            link_element = note.ele('tag:a', timeout=2)
            link = link_element.link if link_element else ""
            
            # 获取点赞数
            likes = 0
            try:
                likes_element = note.ele('.like-wrapper', timeout=1)
                if likes_element:
                    likes_text = likes_element.text
                    likes = int(re.sub(r"\D", "", likes_text)) if likes_text else 0
            except Exception:
                pass
            
            # 获取评论数
            comments = 0
            try:
                comments_element = note.ele('.comment-wrapper', timeout=1)
                if comments_element:
                    comments_text = comments_element.text
                    comments = int(re.sub(r"\D", "", comments_text)) if comments_text else 0
            except Exception:
                pass
            
            # 获取收藏数
            collection = 0
            try:
                collection_element = note.ele('.collect-wrapper', timeout=1)
                if collection_element:
                    collection_text = collection_element.text
                    collection = int(re.sub(r"\D", "", collection_text)) if collection_text else 0
            except Exception:
                pass
            
            # 获取作者信息
            author = ""
            try:
                author_element = note.ele('.author', timeout=1)
                if author_element:
                    author = author_element.text
            except Exception:
                pass
            
            # 获取作者链接
            author_link = ""
            try:
                author_link_element = note.ele('.author-wrapper tag:a', timeout=1)
                if author_link_element:
                    author_link = author_link_element.link
            except Exception:
                pass
            
            # 获取作者头像
            author_avatar = ""
            try:
                author_avatar_element = note.ele('.author-avatar tag:img', timeout=1)
                if author_avatar_element:
                    author_avatar = author_avatar_element.attr('src')
            except Exception:
                pass
            
            # 获取帖子图片
            images = []
            try:
                image_elements = note.eles('.img tag:img', timeout=1)
                for img_element in image_elements:
                    img_src = img_element.attr('src')
                    if img_src:
                        images.append(img_src)
            except Exception:
                pass
            
            # 获取标签
            tags = []
            try:
                tag_elements = note.eles('.tag', timeout=1)
                for tag_element in tag_elements:
                    tag_text = tag_element.text
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
                    "author_link": author_link,
                    "author_avatar": author_avatar,
                    "tags": tags,
                    "images": images,
                    "comments_list": [],  # 预留评论列表字段
                    "image_description": "",  # 预留图片描述字段
                    "food_type": "其他",  # 预留食物分类字段
                    "cuisine": "",  # 预留菜系字段
                    "ingredients": [],  # 预留食材字段
                    "nutrition": None  # 预留营养信息字段
                }
                
                # 使用GLM-4.6V-Flash识别图片内容
                if images:
                    try:
                        from app.utils.zhipuai_client import get_zhipuai_client
                        client = get_zhipuai_client()
                        
                        # 使用第一张图片进行识别
                        image_url = images[0]
                        logger.info(f"开始使用GLM-4.6V-Flash识别图片：{image_url[:50]}...")
                        
                        analysis_result = client.analyze_food_image(image_url=image_url)
                        
                        if analysis_result:
                            hot_item["image_description"] = analysis_result.get("food_name", title)
                            hot_item["food_type"] = analysis_result.get("food_type", "其他")
                            hot_item["cuisine"] = analysis_result.get("cuisine", "")
                            hot_item["ingredients"] = analysis_result.get("ingredients", [])
                            hot_item["nutrition"] = analysis_result.get("nutrition_estimate", None)
                            
                            logger.info(f"图片识别成功：{analysis_result.get('food_name')} ({analysis_result.get('food_type')})")
                    except Exception as e:
                        logger.warning(f"图片识别失败：{str(e)}")
                
                logger.info(f"成功解析笔记：{title}")
                return hot_item
        except Exception as e:
            logger.warning(f"解析笔记失败：{str(e)}")
        return None
    
    def _parse_comments(self, note_link, max_comments=50):
        """爬取帖子评论内容"""
        if not self.page:
            logger.warning("页面未初始化，无法执行爬取")
            return []
        
        comments = []
        try:
            # 打开帖子链接
            self.page.get(note_link)
            self._random_delay(3, 5)
            
            # 滚动加载评论
            for i in range(5):
                self.page.scroll.down(1000)
                self._random_delay(1, 2)
            
            # 获取评论元素
            comment_elements = self.page.eles('.comment-item')
            logger.info(f"找到 {len(comment_elements)} 条评论")
            
            # 解析评论
            for comment in comment_elements[:max_comments]:
                try:
                    # 获取评论内容
                    content_element = comment.ele('.comment-content', timeout=0)
                    content = content_element.text if content_element else ""
                    
                    # 获取评论者
                    author_element = comment.ele('.comment-author', timeout=0)
                    author = author_element.text if author_element else ""
                    
                    # 获取评论时间
                    time_element = comment.ele('.comment-time', timeout=0)
                    comment_time = time_element.text if time_element else ""
                    
                    # 获取点赞数
                    likes = 0
                    try:
                        likes_element = comment.ele('.comment-like', timeout=0)
                        if likes_element:
                            likes_text = likes_element.text
                            likes = int(re.sub(r"\D", "", likes_text)) if likes_text else 0
                    except Exception:
                        pass
                    
                    if content:
                        comments.append({
                            "author": author,
                            "content": content,
                            "time": comment_time,
                            "likes": likes
                        })
                except Exception as e:
                    logger.warning(f"解析评论失败：{str(e)}")
                    continue
            
            logger.info(f"成功解析 {len(comments)} 条评论")
        except Exception as e:
            logger.error(f"爬取评论失败：{str(e)}")
        
        return comments
    
    def search_hot_food(self, keyword="美食", scroll_times=8, max_retries=2, max_items=200, crawl_comments=False):
        """搜索热点美食（带重试机制）"""
        if not DrissionPage_available:
            logger.warning("DrissionPage不可用，返回空列表")
            return []
        
        if not self.page:
            logger.warning("页面未初始化，无法执行爬取")
            return []
        
        retries = 0
        while retries < max_retries:
            try:
                # 对关键词进行编码
                encoded_keyword = urllib.parse.quote(keyword)
                # 打开小红书搜索页面
                search_url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_keyword}&source=web_search_result_notes"
                logger.info(f"开始爬取 {keyword} 的热点美食，第 {retries + 1} 次尝试")
                self.page.get(search_url)
                
                # 等待页面加载
                self._random_delay(1.5, 2.5)
                
                # 处理可能的登录弹窗
                try:
                    # 尝试关闭登录弹窗
                    close_button = self.page.ele('.modal-close', timeout=2)
                    if close_button:
                        close_button.click()
                        self._random_delay(1, 2)
                        logger.info("成功关闭登录弹窗")
                except Exception as e:
                    logger.info(f"没有登录弹窗或关闭失败：{str(e)}")
                
                # 滚动页面，加载更多内容
                self._scroll_page(scroll_times)
                
                # 获取笔记元素
                note_elements = self.page.eles('.note-item', timeout=5)
                logger.info(f"找到 {len(note_elements)} 条笔记")
                
                hot_items = []
                for note in note_elements[:max_items]:  # 取前max_items条
                    try:
                        hot_item = self._parse_note(note)
                        if hot_item:
                            # 爬取评论（可选，为了提高效率，默认不爬取）
                            if crawl_comments and hot_item.get('link'):
                                try:
                                    # 保存当前页面
                                    current_url = self.page.url
                                    comments = self._parse_comments(hot_item['link'])
                                    hot_item['comments_list'] = comments
                                    logger.info(f"成功爬取 {len(comments)} 条评论")
                                    # 返回到搜索页面
                                    self.page.get(current_url)
                                    self._random_delay(2, 3)
                                except Exception as e:
                                    logger.warning(f"爬取评论失败：{str(e)}")
                                    # 返回到搜索页面
                                    try:
                                        self.page.get(search_url)
                                        self._random_delay(2, 3)
                                    except Exception:
                                        pass
                            hot_items.append(hot_item)
                    except Exception as e:
                        logger.warning(f"处理笔记失败：{str(e)}")
                        continue
                
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
                    self.page.save_screenshot(screenshot_path)
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
    
    def search_by_ingredients(self, ingredients, scroll_times=10, max_retries=3, max_items=100):
        """根据食材搜索小红书菜谱"""
        if not DrissionPage_available:
            logger.warning("DrissionPage不可用，返回空列表")
            return []
        
        if not self.page:
            logger.warning("页面未初始化，无法执行爬取")
            return []
        
        if not ingredients:
            logger.warning("食材列表为空，返回空列表")
            return []
        
        # 构建搜索关键词
        keyword = f"{'+'.join(ingredients)} 菜谱"
        logger.info(f"根据食材搜索菜谱：{keyword}")
        
        # 调用搜索方法
        return self.search_hot_food(keyword, scroll_times, max_retries, max_items, crawl_comments=False)
    
    def save_to_excel(self, hot_items, keyword="美食"):
        """保存爬取结果到Excel"""
        if not hot_items:
            logger.warning("无数据可保存")
            return
        
        try:
            # 构造数据列表
            data = []
            for item in hot_items:
                data.append([
                    item['title'],
                    item['author'],
                    item['link'],
                    item['author_link'],
                    item['author_avatar'],
                    item['likes'],
                    item['comments'],
                    item['collection'],
                    ','.join(item['tags'])
                ])
            
            # 创建DataFrame
            df = pd.DataFrame(data, columns=[
                '标题', '作者', '笔记链接', '作者主页', '作者头像', '点赞数', '评论数', '收藏数', '标签'
            ])
            
            # 按点赞数降序排序
            df = df.sort_values(by='点赞数', ascending=False)
            
            # 保存到Excel
            excel_path = f"xhs_{keyword}_{int(time.time())}.xlsx"
            df.to_excel(excel_path, index=False)
            logger.info(f"数据已保存到 {excel_path}")
            return excel_path
        except Exception as e:
            logger.error(f"保存到Excel失败：{str(e)}")
            return None
    
    def close(self):
        """关闭页面"""
        if self.page:
            try:
                self.page.close()
                logger.info("页面已关闭")
            except Exception as e:
                logger.warning(f"关闭页面失败：{str(e)}")

def manage_crawl_files():
    """管理爬取文件，保留最新2个，删除其余"""
    try:
        # 获取所有爬取文件
        files = []
        for file in os.listdir('.'):
            if file.startswith('xhs_') and file.endswith('.xlsx'):
                files.append((file, os.path.getmtime(file)))
        
        # 按修改时间排序
        files.sort(key=lambda x: x[1], reverse=True)
        
        # 保留最新2个文件，删除其余
        if len(files) > 2:
            for file, _ in files[2:]:
                try:
                    os.remove(file)
                    logger.info(f"删除旧文件：{file}")
                except Exception as e:
                    logger.warning(f"删除文件失败：{str(e)}")
    except Exception as e:
        logger.error(f"管理爬取文件失败：{str(e)}")

def crawl_xhs_hot_food(force_login=False, manual=False):
    """使用DrissionPage爬取小红书热点美食
    
    Args:
        force_login: 是否强制登录
        manual: 是否手动爬取
    """
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
            # 检查DrissionPage是否可用
            if not DrissionPage_available:
                logger.warning("DrissionPage不可用，使用模拟数据")
                # 使用模拟数据
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
                
                # 清空旧数据
                HotFood.query.delete()
                
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
                            description=item.get('desc', item['ingre_list']),
                            comments=item.get('comments', 0),
                            collection=item.get('collection', 0),
                            create_time=datetime.now()
                        )
                        hot_food.save()
                        
                    except Exception as e:
                        logger.warning(f"解析第{index}个热点美食失败：{str(e)}")
                        continue
                
                logger.info(f"小红书热点美食模拟数据加载完成，共{len(mock_hot_foods)}条")
                return
            
            # 初始化爬虫
            crawler = XHSDrissionCrawler(force_login=force_login)
            
            # 检查是否登录，如果没有登录则尝试登录（仅在force_login=True时）
            if not crawler.cookies:
                if force_login:
                    logger.info("未检测到登录状态，强制登录")
                    if not crawler.login():
                        logger.error("登录失败，使用模拟数据")
                        # 登录失败时使用模拟数据
                        hot_items = []
                    else:
                        # 登录成功，继续爬取
                        hot_items = crawler.search_hot_food("美食", scroll_times=8, max_items=200, crawl_comments=False)
                else:
                    logger.info("未检测到登录状态，尝试直接爬取")
                    # 尝试直接爬取（不强制登录）
                    hot_items = crawler.search_hot_food("美食", scroll_times=8, max_items=200, crawl_comments=False)
            else:
                # 已登录，直接爬取
                hot_items = crawler.search_hot_food("美食", scroll_times=8, max_items=200, crawl_comments=False)
            
            # 保存到Excel，区分自动和手动爬取
            if hot_items:
                if manual:
                    excel_path = crawler.save_to_excel(hot_items, "美食_manual")
                else:
                    excel_path = crawler.save_to_excel(hot_items, "美食_auto")
                
                # 管理爬取文件
                manage_crawl_files()
            else:
                logger.warning("未获取到热点美食数据，使用模拟数据")
                # 使用模拟数据
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
                
                # 清空旧数据
                HotFood.query.delete()
                
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
                            description=item.get('desc', item['ingre_list']),
                            comments=item.get('comments', 0),
                            collection=item.get('collection', 0),
                            create_time=datetime.now()
                        )
                        hot_food.save()
                        
                    except Exception as e:
                        logger.warning(f"解析第{index}个热点美食失败：{str(e)}")
                        continue
                
                logger.info(f"小红书热点美食模拟数据加载完成，共{len(mock_hot_foods)}条")
                return
            
            # 处理爬取到的热点美食数据
            if hot_items:
                # 调用数据处理器
                processed_items, statistics = process_food_data(hot_items)
                logger.info(f"数据处理完成，统计信息：{statistics}")
                
                # 保存原始数据到真实数据库
                HotFood.query.delete()
                
                for index, item in enumerate(processed_items):
                    try:
                        # 提取标签，如果没有则使用默认标签
                        tags = item.get('tags', [])
                        if not tags:
                            tags = ["美食"]
                        
                        # 提取图片，优先使用第一张图片
                        image = ""
                        if item.get('images') and len(item['images']) > 0:
                            image = item['images'][0]
                        elif item.get('author_avatar'):
                            image = item['author_avatar']
                        
                        # 准备图片识别结果的 JSON 字段
                        ingredients_json = json.dumps(item.get('ingredients', []), ensure_ascii=False)
                        nutrition_json = json.dumps(item.get('nutrition', {}), ensure_ascii=False) if item.get('nutrition') else ""
                        
                        # 创建热点美食记录
                        hot_food = HotFood(
                            food_name=item.get('image_description', item.get('title', '其他')),  # 使用AI识别的名称
                            ingre_list=item['title'],
                            link=item['link'],
                            hot_score=item.get('hotness_score', item.get('likes', 0)),
                            source="小红书",
                            tags=json.dumps(tags),
                            image=image,
                            description=item.get('image_description', item['title']),
                            comments=item.get('comments', 0),
                            collection=item.get('collection', 0),
                            create_time=datetime.now(),
                            image_description=item.get('image_description', ''),
                            food_type=item.get('food_type', '其他'),
                            cuisine=item.get('cuisine', ''),
                            ingredients=ingredients_json,
                            nutrition=nutrition_json,
                            is_healthy=item.get('is_healthy', True),
                            health_rating=item.get('health_rating', 3)
                        )
                        hot_food.save()
                        logger.info(f"✅ 成功保存热点美食：{item['title']} (分类：{item.get('food_type', '其他')})")
                        
                    except Exception as e:
                        logger.warning(f"解析第{index}个热点美食失败：{str(e)}")
                        continue
                
                logger.info(f"✅ 原始数据已保存到真实数据库，共{len(processed_items)}条")
                logger.info(f"菜品分布：{statistics.get('food_distribution', {})}")
                logger.info(f"热门关键词：{statistics.get('top_keywords', {})}")
                
                # AI筛选并同步到本地数据库
                logger.info("🤖 开始AI筛选和数据同步...")
                try:
                    from app.dual_db import DataSynchronizer
                    DataSynchronizer.sync_hot_foods_to_local()
                    logger.info("✅ AI筛选和数据同步完成！")
                except ImportError as e:
                    logger.warning(f"⚠️  未找到同步模块，跳过同步: {e}")
                except Exception as e:
                    logger.warning(f"⚠️  数据同步失败: {e}")
            
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
                            description=item.get('desc', item['ingre_list']),
                            comments=item.get('comments', 0),
                            collection=item.get('collection', 0),
                            create_time=datetime.now()
                        )
                        hot_food.save()
                        
                    except Exception as e:
                        logger.warning(f"解析第{index}个热点美食失败：{str(e)}")
                        continue
                
                logger.info(f"小红书热点美食模拟数据加载完成，共{len(mock_hot_foods)}条")
    finally:
        # 确保关闭页面
        if crawler:
            try:
                crawler.close()
                logger.info("页面已关闭")
            except Exception as e:
                logger.warning(f"关闭页面失败：{str(e)}")
