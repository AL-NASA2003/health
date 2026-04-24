// 智谱AI网页版集成工具
const { post, get } = require('../../utils/request');

/**
 * 智谱AI网页版服务类
 * 提供通过网页版智谱AI生成菜谱和图像的功能
 */
class ZhipuWebService {
  constructor() {
    this.status = {
      available: false,
      loggedIn: false,
      locked: false
    };
  }

  /**
   * 获取网页爬虫状态
   */
  async getStatus() {
    try {
      const result = await get('/zhipu/status', {}, false);
      if (result && result.data) {
        this.status = {
          available: result.data.available,
          loggedIn: false, // 需要单独检查
          locked: result.data.locked
        };
        return this.status;
      }
    } catch (e) {
      console.error('获取状态失败：', e);
    }
    return { available: false, loggedIn: false, locked: false };
  }

  /**
   * 启动浏览器并提示登录
   */
  async startLogin() {
    try {
      const result = await post('/zhipu/login', {}, false);
      if (result && result.code === 200) {
        wx.showModal({
          title: '提示',
          content: '浏览器已启动，请在浏览器中完成智谱AI登录',
          showCancel: false,
          confirmText: '我知道了'
        });
        return result.data;
      }
    } catch (e) {
      console.error('启动登录失败：', e);
      wx.showToast({ title: '启动失败', icon: 'none' });
    }
    return null;
  }

  /**
   * 检查登录状态
   */
  async checkLogin() {
    try {
      const result = await get('/zhipu/check-login', {}, false);
      if (result && result.code === 200) {
        this.status.loggedIn = result.data.logged_in;
        return result.data.logged_in;
      }
    } catch (e) {
      console.error('检查登录失败：', e);
    }
    return false;
  }

  /**
   * 通过网页版生成个性化菜谱
   */
  async generateRecipe(userInfo, ingredients = [], preference = '') {
    try {
      wx.showLoading({ title: '正在生成...' });
      
      const result = await post('/zhipu/generate-recipe', {
        user_info: userInfo,
        ingredients: ingredients,
        preference: preference
      }, false);
      
      wx.hideLoading();
      
      if (result && result.code === 200) {
        const { recipe, source } = result.data;
        
        if (source === 'zhipu_web') {
          wx.showToast({ title: '生成成功', icon: 'success' });
        } else {
          wx.showToast({ title: '使用备用方案', icon: 'none' });
        }
        
        return recipe;
      } else if (result && result.code === 403) {
        wx.showModal({
          title: '需要登录',
          content: '请先启动浏览器并登录智谱AI网页版',
          confirmText: '去登录',
          success: (res) => {
            if (res.confirm) {
              this.startLogin();
            }
          }
        });
      }
    } catch (e) {
      wx.hideLoading();
      console.error('生成菜谱失败：', e);
      wx.showToast({ title: '生成失败', icon: 'none' });
    }
    return null;
  }

  /**
   * 通过网页版生成图像
   */
  async generateImage(prompt, style = 'food', size = '1024x1024') {
    try {
      wx.showLoading({ title: '正在生成...' });
      
      const result = await post('/zhipu/generate-image', {
        prompt: prompt,
        style: style,
        size: size
      }, false);
      
      wx.hideLoading();
      
      if (result && result.code === 200) {
        return result.data;
      } else if (result && result.code === 403) {
        wx.showModal({
          title: '需要登录',
          content: '请先启动浏览器并登录智谱AI网页版',
          confirmText: '去登录',
          success: (res) => {
            if (res.confirm) {
              this.startLogin();
            }
          }
        });
      }
    } catch (e) {
      wx.hideLoading();
      console.error('生成图像失败：', e);
    }
    return null;
  }
}

// 创建单例
const zhipuWebService = new ZhipuWebService();

module.exports = {
  ZhipuWebService,
  zhipuWebService
};
