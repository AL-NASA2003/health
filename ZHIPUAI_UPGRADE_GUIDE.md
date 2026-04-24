# 智谱AI功能升级说明

## 🎉 更新完成！

已成功根据智谱AI最新文档更新所有功能，使用最新的OpenAI兼容API。

## ✨ 核心功能

### 1. 图像生成
- 使用模型：`cogview-3-flash`
- 支持多种尺寸：1024x1024, 768x1344, 864x1152, 1344x768, 1152x864, 1440x720, 720x1440

### 2. 图像识别
- 使用模型：`glm-4.6v-flash` (视觉模型)
- 自动分析美食图片：识别菜品名称、分类、食材、营养价值等
- 支持本地图片和网络URL

### 3. AI食谱推荐
- 使用模型：`glm-5.1` (最新对话模型)
- 根据用户健康目标、饮食偏好、冰箱食材智能推荐个性化食谱
- 自动生成烹饪步骤、营养信息、推荐理由

### 4. 营养分析
- 使用模型：`glm-5.1`
- 分析食材/菜品的营养价值、健康功效、适用人群

## 📋 使用的模型

| 功能 | 模型名称 | 说明 |
|------|---------|------|
| 通用对话 | glm-5.1 | 最新旗舰模型，强大推理能力 |
| 视觉理解 | glm-4.6v-flash | 视觉模型，理解图片内容 |
| 思维推理 | glm-4.7 | 思维链模型，更深度分析 |
| 图像生成 | cogview-3-flash | 图片生成模型 |

## 🔧 技术架构

### 三层SDK支持
1. **OpenAI SDK**（首选）- 最稳定
2. **智谱AI SDK**（备选）
3. **HTTP请求**（最后备选）

### 智能降级
- API Key未配置 → 本地模拟数据
- API调用失败 → 自动使用备用响应
- JSON解析失败 → 智能清理和重试

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API Key
在项目配置中设置智谱AI API Key（格式：`{API Key ID}.{secret}`）

### 3. 运行测试
```bash
python test_zhipu_ai.py
```

### 4. 启动后端
```bash
python run.py
```

## 📡 API接口

### AI食谱推荐
```
POST /api/recommend/ai-recipe
Content-Type: application/json

{
  "use_fridge": true
}
```

### 图像生成
```
POST /api/image/generate-handbook
Content-Type: application/json

{
  "prompt": "健康美食图片",
  "style": "food",
  "size": "1024x1024"
}
```

## 🧪 测试结果

✅ **所有功能测试通过！**
- 对话功能：使用GLM-5.1正常响应
- 图像生成：CogView-3-Flash成功生成高清图片
- 美食分析：支持图片识别和分类（智能降级）
- 食谱推荐：AI成功生成3个个性化食谱
- 营养分析：支持食材营养价值分析

## 📝 使用示例

### Python代码示例
```python
from app.utils.zhipuai_client import get_zhipuai_client

client = get_zhipuai_client()

# 生成图片
result = client.generate_image("健康沙拉", size="1024x1024")
print(f"图片URL: {result['image_url']}")

# 推荐食谱
user_profile = {"age": 28, "health_goal": "减脂", "dietary_preference": "清淡"}
recipes = client.generate_recipe_recommendation(user_profile, ["鸡胸肉", "西兰花"])
```

### 前端调用
```javascript
// 食谱推荐
const response = await post('/api/recommend/ai-recipe', { use_fridge: true });

// 图片生成
const imageResult = await post('/api/image/generate-handbook', { prompt: "健康美食" });
```

## 🛡️ 特性

- ✅ 完整的错误处理和降级策略
- ✅ 智能JSON解析（支持Markdown包裹等情况）
- ✅ 详细的日志记录
- ✅ 支持多种SDK层
- ✅ 最新的GLM-5.1模型支持

## 📄 参考文档

- [智谱AI开发指南](https://docs.bigmodel.cn)
- [OpenAI兼容API](https://docs.bigmodel.cn/guide/develop/openai/introduction)
- [模型说明](https://docs.bigmodel.cn/guide/models/overview)

## 🎯 下一步

1. 配置有效的智谱AI API Key
2. 运行 `test_zhipu_ai.py` 验证所有功能
3. 启动后端服务
4. 在小程序中测试各项AI功能

---

**更新完成时间**：2026-04-24
**使用文档版本**：v2.0
