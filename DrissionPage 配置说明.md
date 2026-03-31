# DrissionPage 配置说明

## 安装状态 ✅

- **DrissionPage**: 已安装 (版本 4.1.1.2)
- **Python**: 3.10.2
- **相关依赖**: 已全部安装

## 使用前准备

### 1. 安装 Chrome 浏览器

DrissionPage 需要 Chrome 浏览器支持，请确保已安装：

- **Chrome 浏览器**: 版本 120+（推荐最新版）
- 下载地址：https://www.google.com/chrome/

### 2. 配置说明

DrissionPage 4.x 版本会自动检测 Chrome 浏览器，通常不需要手动配置 ChromeDriver。

### 3. 测试安装

运行以下命令测试 DrissionPage 是否正常工作：

```python
from DrissionPage import ChromiumPage

# 创建页面对象
page = ChromiumPage()

# 访问网页
page.get('https://www.baidu.com')

# 打印标题
print(page.title)

# 关闭页面
page.quit()
```

### 4. 常见问题

#### 问题 1：找不到 Chrome 浏览器
**错误信息**: `SessionNotCreatedException: Message: session not created: Chrome instance not found`

**解决方案**:
1. 安装 Chrome 浏览器
2. 确保 Chrome 安装在默认路径：
   - Windows: `C:\Program Files\Google\Chrome\Application\chrome.exe`
3. 或者指定 Chrome 路径：
```python
from DrissionPage import ChromiumOptions, ChromiumPage

co = ChromiumOptions()
co.set_browser_path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
page = ChromiumPage(co)
```

#### 问题 2：Chrome 版本不匹配
**错误信息**: `Message: This version of ChromeDriver only supports Chrome version XX`

**解决方案**:
1. 更新 Chrome 浏览器到最新版本
2. 或者更新 DrissionPage：`pip install -U DrissionPage`

#### 问题 3：权限问题
**错误信息**: `Access is denied` 或 `Permission denied`

**解决方案**:
1. 以管理员身份运行程序
2. 关闭所有 Chrome 窗口
3. 清理残留进程：
```bash
taskkill /F /IM chrome.exe
```

### 5. 在项目中配置

在 `app/config.py` 中添加以下配置（可选）：

```python
# DrissionPage 配置
DRISSIONPAGE_CONFIG = {
    'browser_path': None,  # Chrome 浏览器路径，None 表示自动检测
    'headless': False,     # 是否无头模式
    'timeout': 30,         # 超时时间（秒）
}
```

### 6. 使用热点美食爬取功能

配置完成后，可以调用爬取接口：

```javascript
// 前端调用示例
wx.request({
  url: 'http://localhost:5000/api/hotfood/crawl',
  method: 'POST',
  header: {
    'Authorization': 'Bearer ' + token
  },
  success: (res) => {
    console.log('爬取成功:', res.data)
  }
})
```

### 7. 注意事项

1. **首次运行**: 首次运行时会启动 Chrome 浏览器，需要扫码登录小红书
2. **登录状态**: 登录状态会保存，后续爬取会自动使用
3. **反爬虫**: 小红书有反爬机制，建议不要频繁爬取
4. **网络环境**: 确保网络畅通，能够访问小红书

### 8. 测试爬虫

运行测试脚本验证爬虫是否工作正常：

```bash
python -c "from app.crawler.xhs_drission_crawler import crawl_xhs_hot_food; crawl_xhs_hot_food()"
```

如果看到类似以下日志，说明爬虫工作正常：
```
页面初始化成功，使用 User-Agent: ...
找到 XX 条笔记
成功解析 XX 条笔记，爬取完成
小红书热点美食爬取完成，共 XX 条
```
