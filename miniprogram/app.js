const { checkLogin } = require('./utils/auth');
const cache = require('./utils/cache');

App({
  // 小程序初始化
  onLaunch(options) {
    // 轻量级缓存预热
    cache.warmup();
    
    // 快速检查 token，立即决定跳转
    const token = wx.getStorageSync('token');
    if (token) {
      // 有 token，直接跳转到首页
      wx.switchTab({
        url: '/pages/index/index'
      });
    }
  },

  // 小程序显示
  onShow(options) {
  },

  // 小程序隐藏
  onHide() {
  },

  // 全局数据
  globalData: {
    userInfo: null,
    isLogin: false,
    baseUrl: 'http://localhost:5000/api',
    staticBaseUrl: 'http://localhost:5000'
  },

  // 更新全局用户信息
  updateUserInfo(userInfo) {
    this.globalData.userInfo = userInfo;
    this.globalData.isLogin = true;
  }
});