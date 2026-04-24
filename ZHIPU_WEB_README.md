# 智谱AI网页版爬虫 使用说明

## 功能概述

当智谱AI API调用失败时，可以使用网页版爬虫通过浏览器自动化的方式来生成菜谱和图像。

## 快速开始

### 1. 启动网页版爬虫

在项目根目录下运行：

```bash
python start_zhipu_web.py
```

这个脚本会：
- 自动打开浏览器
- 访问智谱AI网站 (https://chatglm.cn)
- 提示您完成登录
- 测试菜谱和图像生成功能

### 2. 登录智谱AI

在打开的浏览器中：
1. 访问 https://chatglm.cn
2. 使用手机扫码或账号密码登录
3. 登录成功后，在命令行中按回车键继续

### 3. 测试功能

登录成功后，可以选择：
- 测试菜谱生成
- 测试图像生成
- 保持浏览器运行并退出

## 在后端启动时使用

启动后端服务时，会自动尝试初始化网页版爬虫：

```bash
python run.py
```

## API 接口说明

### 获取状态
```
GET /api/zhipu/status
```

响应：
```json
{
  "code": 0,
  "data": {
    "available": true,
    "locked": false,
    "url": "https://www.zhipuai.cn/zh"
  }
}
```

### 启动登录
```
POST /api/zhipu/login
```

响应：
```json
{
  "code": 0,
  "data": {
    "message": "浏览器已启动，请在浏览器中完成登录后调用/check-login",
    "action": "login"
  }
}
```

### 检查登录状态
```
GET /api/zhipu/check-login
```

响应：
```json
{
  "code": 0,
  "data": {
    "logged_in": true,
    "message": "已登录"
  }
}
```

### 生成菜谱
```
POST /api/zhipu/generate-recipe
```

请求参数：
```json
{
  "user_info": {
    "health_goal": "减脂",
    "dietary_preference": "清淡",
    "calorie_target": 1800
  },
  "ingredients": ["鸡胸肉", "西兰花", "胡萝卜"],
  "preference": "少油少盐"
}
```

响应：
```json
{
  "code": 0,
  "data": {
    "recipe": {
      "name": "时蔬炒鸡胸肉",
      "description": "低脂高蛋白，适合减脂增肌",
      "ingredients": ["鸡胸肉", "西兰花", "胡萝卜", "蒜末", "橄榄油"],
      "steps": [...],
      "nutrition": {
        "calorie": 350,
        "protein": 35,
        "carb": 15,
        "fat": 8
      },
      "difficulty": "简单",
      "time": "20分钟",
      "health_score": 85
    },
    "source": "zhipu_web"
  }
}
```

### 生成图像
```
POST /api/zhipu/generate-image
```

请求参数：
```json
{
  "prompt": "健康美味的水果沙拉",
  "style": "food",
  "size": "1024x1024"
}
```

响应：
```json
{
  "code": 0,
  "data": {
    "success": true,
    "image_url": "https://...",
    "source": "zhipu_web",
    "model": "web_image_generator",
    "prompt": "健康美味的水果沙拉"
  }
}
```

## 前端使用示例

### 在小程序中使用

```javascript
const { zhipuWebService } = require('../../utils/zhipu-web');

// 检查状态
const status = await zhipuWebService.getStatus();

// 启动登录
await zhipuWebService.startLogin();

// 检查登录
const isLoggedIn = await zhipuWebService.checkLogin();

// 生成菜谱
const recipe = await zhipuWebService.generateRecipe(
  { health_goal: '减脂', dietary_preference: '清淡' },
  ['鸡胸肉', '西兰花'],
  '少油少盐'
);

// 生成图像
const image = await zhipuWebService.generateImage(
  '健康美味的水果沙拉',
  'food',
  '1024x1024'
);
```

## 注意事项

1. **浏览器兼容性**：建议使用 Chrome 或 Edge 浏览器
2. **登录状态保持**：第一次登录后，用户数据会被保存，下次启动会自动恢复
3. **并发控制**：同一时间只能有一个用户使用网页版爬虫
4. **备用方案**：如果网页爬虫不可用，会自动使用备用的模拟数据

## 故障排查

### 浏览器无法启动

确保已安装 Chrome 或 Edge 浏览器，检查浏览器驱动是否可用。

### 登录后无法识别状态

手动在浏览器中访问 https://chatglm.cn 并刷新页面，确保已登录成功。

### 生成响应超时

智谱AI响应时间可能较长，可以耐心等待或使用备用方案。

## 技术架构

- **浏览器自动化**：使用 DrissionPage 驱动浏览器
- **会话管理**：保存用户配置，避免重复登录
- **线程安全**：使用锁机制防止并发访问
- **降级策略**：失败时自动使用备用数据

## 文件结构

```
health/
├── app/
│   ├── crawler/
│   │   └── zhipu_ai_web_crawler.py    # 网页爬虫核心
│   └── api/
│       └── zhipu_web_api.py            # API 接口
├── miniprogram/
│   └── utils/
│       └── zhipu-web.js                # 前端工具
├── start_zhipu_web.py                  # 启动脚本
└── ZHIPU_WEB_README.md                 # 本文档
```
