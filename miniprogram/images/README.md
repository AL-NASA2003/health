# 图标说明

微信小程序 TabBar 需要使用 PNG 格式的图标，尺寸为 81px * 81px。

## 当前状态

已创建 SVG 格式的占位图标文件，需要转换为 PNG 格式。

## 解决方案

### 方案1：使用在线工具转换
1. 访问 https://cloudconvert.com/svg-to-png
2. 上传 `images/` 目录下的 SVG 文件
3. 设置输出尺寸为 81px * 81px
4. 下载转换后的 PNG 文件并替换原文件

### 方案2：使用设计工具
使用以下工具创建 PNG 图标：
- Figma: https://www.figma.com
- Sketch: https://www.sketch.com
- Adobe XD: https://www.adobe.com/products/xd.html
- 在线工具: https://www.canva.com

### 方案3：临时移除 TabBar
如果暂时不需要 TabBar，可以修改 `app.json`，注释掉 `tabBar` 部分。

## 图标说明

| 图标文件 | 用途 | 颜色 |
|---------|------|------|
| home.png | 首页图标 | 灰色 (#999999) |
| home-active.png | 首页选中图标 | 绿色 (#07c160) |
| diet.png | 饮食图标 | 灰色 (#999999) |
| diet-active.png | 饮食选中图标 | 绿色 (#07c160) |
| ingredient.png | 食材图标 | 灰色 (#999999) |
| ingredient-active.png | 食材选中图标 | 绿色 (#07c160) |
| recipe.png | 食谱图标 | 灰色 (#999999) |
| recipe-active.png | 食谱选中图标 | 绿色 (#07c160) |
| hot.png | 热点图标 | 灰色 (#999999) |
| hot-active.png | 热点选中图标 | 绿色 (#07c160) |

## 注意事项

- 图标必须是 PNG 格式
- 推荐尺寸：81px * 81px
- 未选中状态建议使用灰色 (#999999)
- 选中状态建议使用主题色 (#07c160)
- 图标内容简洁明了，易于识别
