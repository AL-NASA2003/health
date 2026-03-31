# AI个性化推荐模块使用说明

## 功能介绍

基于文心大模型4.0的个性化推荐系统，通过计算用户画像与食谱/食材的相似度，实现智能推荐。

## 核心功能

1. **用户画像构建** - 基于用户基本信息和饮食记录
2. **相似度计算** - 使用文心大模型计算文本相似度
3. **智能筛选** - 根据健康目标筛选推荐结果
4. **个性化推荐** - 食谱推荐和食材推荐

## 文件结构

```
app/
├── utils/
│   ├── ernie_api.py          # 文心大模型客户端
│   └── test_ernie.py        # API测试脚本
└── api/
    └── recommend_api.py        # 推荐API接口
```

## 配置说明

在 `app/config.py` 中配置文心大模型API：

```python
# 文心大模型4.0 API配置
ERNIE_API_KEY = "你的文心大模型API_KEY"
ERNIE_SECRET_KEY = "你的文心大模型SECRET_KEY"
ERNIE_ACCESS_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
ERNIE_SEMANTIC_URL = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/similarity"
```

### 获取API密钥

1. 访问 [百度智能云](https://cloud.baidu.com/)
2. 登录账号，进入控制台
3. 创建应用，选择"自然语言处理"
4. 获取 API Key 和 Secret Key

## API接口

### 1. 个性化食谱推荐

**接口：** `POST /api/recommend/recipe`

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应示例：**
```json
{
  "code": 200,
  "msg": "推荐成功",
  "data": {
    "user_profile": "25岁，男，身高175cm，体重65kg，健康目标减脂，饮食偏好清淡，近期常吃鸡胸肉沙拉,清蒸鲈鱼",
    "recommend_list": [
      {
        "recipe_id": 1,
        "recipe_name": "低脂鸡胸肉沙拉",
        "ingre_list": "鸡胸肉,西兰花",
        "cook_step": "1. 鸡胸肉切块腌制\n2. 煎至金黄\n3. 混合蔬菜",
        "calorie": 280,
        "protein": 32,
        "carb": 15,
        "fat": 8,
        "flavor": "清淡",
        "cook_type": "凉拌",
        "suitable_crowd": "减脂人群",
        "similarity": 0.8523
      }
    ],
    "total": 10
  }
}
```

### 2. 个性化食材推荐

**接口：** `POST /api/recommend/ingredient`

**请求头：**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**响应示例：**
```json
{
  "code": 200,
  "msg": "推荐成功",
  "data": {
    "recommend_list": [
      {
        "ingredient_id": 1,
        "ingre_name": "鸡胸肉",
        "calorie": 165,
        "protein": 31,
        "carb": 0,
        "fat": 3.6,
        "category": "肉类",
        "frequency": 5
      }
    ],
    "total": 10
  }
}
```

## 推荐算法

### 用户画像构建

```
用户画像 = 年龄 + 性别 + 身高 + 体重 + 健康目标 + 饮食偏好 + 近期饮食记录
```

### 相似度计算

使用文心大模型计算用户画像与食谱/食材的相似度：
- 分数范围：0-1
- 分数越高，相似度越高
- 推荐结果按相似度降序排列

### 智能筛选

根据用户健康目标进行二次筛选：
- **减脂目标**：热量 ≤ 300大卡
- **增肌目标**：蛋白质 ≥ 15g
- **维持目标**：无特殊限制

## 使用方法

### 方法一：测试API

```bash
cd c:\Users\luohu\Desktop\health
python app/utils/test_ernie.py
```

### 方法二：调用推荐接口

```python
import requests

# 个性化食谱推荐
response = requests.post(
    "http://localhost:5000/api/recommend/recipe",
    headers={"Authorization": "Bearer your_token"},
    json={}
)
result = response.json()

# 个性化食材推荐
response = requests.post(
    "http://localhost:5000/api/recommend/ingredient",
    headers={"Authorization": "Bearer your_token"},
    json={}
)
result = response.json()
```

### 方法三：小程序集成

```javascript
// pages/recipe/recipe.js
import { post } from '../../utils/request';

// 获取个性化推荐
getPersonalizedRecommend() {
  post('/recommend/recipe')
    .then((result) => {
      if (result && result.data) {
        this.setData({
          recommendList: result.data.recommend_list
        });
      }
    })
    .catch((err) => {
      console.error('获取推荐失败：', err);
    });
}
```

## 注意事项

1. **API密钥安全**
   - 不要将密钥提交到代码仓库
   - 使用环境变量或配置文件管理密钥
   - 定期更换密钥

2. **调用频率限制**
   - 文心大模型有调用限制
   - 批量计算时添加延迟（0.1秒）
   - 建议使用缓存减少重复调用

3. **Token管理**
   - 访问令牌有效期为30天
   - 令牌会自动缓存和刷新
   - 提前1小时刷新令牌

4. **数据质量**
   - 用户画像需要足够的历史数据
   - 建议用户使用一段时间后再推荐
   - 可以根据反馈调整推荐算法

## 常见问题

### 1. API调用失败

**原因：** API密钥错误或过期

**解决方法：**
- 检查配置文件中的密钥是否正确
- 重新生成API密钥
- 检查网络连接

### 2. 相似度计算为0

**原因：** API调用失败或返回错误

**解决方法：**
- 检查日志中的错误信息
- 确认API配额是否充足
- 联系百度智能云客服

### 3. 推荐结果不准确

**原因：** 用户数据不足或画像不准确

**解决方法：**
- 引导用户完善个人信息
- 增加饮食记录数量
- 调整相似度阈值

## 性能优化

1. **批量计算**
   - 使用 `ernie_batch_similarity` 批量计算
   - 减少API调用次数

2. **缓存机制**
   - 缓存相似度计算结果
   - 避免重复计算

3. **异步处理**
   - 使用异步任务处理推荐请求
   - 提高响应速度

## 技术支持

- 百度智能云：https://cloud.baidu.com/
- 文心大模型文档：https://ai.baidu.com/ai-doc/ERNIE/
- 开源项目：https://github.com/Zoe-juwubafff/Python-XHS-CrawlerAndEmoANAL.git
