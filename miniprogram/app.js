const { checkLogin } = require('./utils/auth');
const cache = require('./utils/cache');
const { eventBus, EVENTS } = require('./utils/eventBus');

App({
  // 小程序初始化
  onLaunch(options) {
    console.log('🚀 小程序启动');
    
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
    console.log('📱 小程序显示');
    eventBus.emit(EVENTS.PAGE_VISIBLE, { time: Date.now() });
  },

  // 小程序隐藏
  onHide() {
    console.log('📱 小程序隐藏');
    eventBus.emit(EVENTS.PAGE_HIDDEN, { time: Date.now() });
  },

  // 全局数据
  globalData: {
    userInfo: null,
    isLogin: false,
    baseUrl: 'http://localhost:5000/api',
    staticBaseUrl: 'http://localhost:5000',
    // 数据同步相关
    dataChanged: {
      diet: false,      // 饮食数据变更
      water: false,     // 饮水数据变更
      exercise: false   // 运动数据变更
    }
  },

  // 更新全局用户信息
  updateUserInfo(userInfo) {
    this.globalData.userInfo = userInfo;
    this.globalData.isLogin = true;
    eventBus.emit(EVENTS.USER_DATA_UPDATED, userInfo);
  },

  // 标记数据已变更（增强版：同时使用事件总线）
  markDataChanged(type, data = null) {
    if (this.globalData.dataChanged.hasOwnProperty(type)) {
      this.globalData.dataChanged[type] = true;
    }
    
    // 使用事件总线触发事件
    const eventMap = {
      'diet': EVENTS.DIET_DATA_UPDATED,
      'water': EVENTS.WATER_DATA_UPDATED,
      'exercise': EVENTS.EXERCISE_DATA_UPDATED
    };
    
    if (eventMap[type]) {
      console.log(`📡 触发数据更新事件: ${type}`, data);
      eventBus.emit(eventMap[type], data);
    }
  },

  // 检查并重置数据变更标志
  checkAndResetDataChanged(type) {
    if (this.globalData.dataChanged.hasOwnProperty(type)) {
      const changed = this.globalData.dataChanged[type];
      this.globalData.dataChanged[type] = false;
      return changed;
    }
    return false;
  },

  // 暴露事件总线
  eventBus,
  EVENTS
});