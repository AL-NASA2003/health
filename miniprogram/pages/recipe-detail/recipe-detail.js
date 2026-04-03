const { get, post } = require('../../utils/request');
const { loginGuard } = require('../../utils/auth');
const cache = require('../../utils/cache');

Page({
  data: {
    recipe: null,
    loading: true,
    activeTab: 'steps' // steps 或 video
  },

  // 页面加载
  onLoad(options) {
    if (!loginGuard()) return;
    const recipeId = options.id;
    if (recipeId) {
      this.getRecipeDetail(recipeId);
    }
  },

  // 获取食谱详情 - 优化版本：有缓存立即显示
  getRecipeDetail(recipeId) {
    // 先检查缓存
    const cacheKey = `req:GET:/recipe/detail/${recipeId}:0`;
    const cachedData = cache.get(cacheKey);
    
    if (cachedData && cachedData.data) {
      // 有缓存，立即显示
      this.setData({
        recipe: cachedData.data,
        loading: false
      });
    } else {
      // 没有缓存，显示加载状态
      this.setData({ loading: true });
    }
    
    // 静默请求最新数据
    get(`/recipe/detail/${recipeId}`, {}, cachedData ? false : true)
      .then((result) => {
        if (result && result.data) {
          this.setData({
            recipe: result.data,
            loading: false
          });
        } else {
          // 如果没有数据，隐藏加载状态
          this.setData({ loading: false });
        }
      })
      .catch((err) => {
        console.error('获取食谱详情失败：', err);
        // 隐藏加载状态
        this.setData({ loading: false });
        if (!cachedData) {
          wx.showToast({ title: '获取食谱详情失败', icon: 'none' });
        }
      });
  },

  // 切换标签
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ activeTab: tab });
    
    // 如果切换到视频标签且没有视频URL，跳转到小红书搜索
    if (tab === 'video' && !this.data.recipe.video_url) {
      const recipeName = this.data.recipe.recipe_name || '';
      if (recipeName) {
        // 跳转到webview页面搜索小红书
        wx.navigateTo({
          url: `/pages/webview/webview?search=${encodeURIComponent(recipeName + ' 食谱 教程')}`
        });
      }
    }
  },

  // 收藏食谱
  collectRecipe() {
    const { recipe } = this.data;
    if (!recipe) return;
    
    post('/collection/add', {
      type: 'recipe',
      target_id: recipe.id
    })
      .then(() => {
        wx.showToast({ title: '收藏成功' });
        // 更新本地数据
        this.setData({
          'recipe.is_collected': true
        });
      })
      .catch((err) => {
        console.error('收藏失败：', err);
        wx.showToast({ title: '收藏失败', icon: 'none' });
      });
  },

  // 取消收藏食谱
  uncollectRecipe() {
    const { recipe } = this.data;
    if (!recipe) return;
    
    post('/collection/remove', {
      type: 'recipe',
      target_id: recipe.id
    })
      .then(() => {
        wx.showToast({ title: '取消收藏成功' });
        // 更新本地数据
        this.setData({
          'recipe.is_collected': false
        });
      })
      .catch((err) => {
        console.error('取消收藏失败：', err);
        wx.showToast({ title: '取消收藏失败', icon: 'none' });
      });
  }
});
