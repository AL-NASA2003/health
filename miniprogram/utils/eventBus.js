// 事件总线 - 用于页面间通信和数据同步
class EventBus {
  constructor() {
    this.events = {};
  }

  /**
   * 订阅事件
   * @param {string} eventName - 事件名称
   * @param {Function} callback - 回调函数
   */
  on(eventName, callback) {
    if (!this.events[eventName]) {
      this.events[eventName] = [];
    }
    this.events[eventName].push(callback);
    return () => this.off(eventName, callback);
  }

  /**
   * 取消订阅
   * @param {string} eventName - 事件名称
   * @param {Function} callback - 回调函数
   */
  off(eventName, callback) {
    if (!this.events[eventName]) return;

    if (callback) {
      const index = this.events[eventName].indexOf(callback);
      if (index !== -1) {
        this.events[eventName].splice(index, 1);
      }
    } else {
      delete this.events[eventName];
    }
  }

  /**
   * 触发事件
   * @param {string} eventName - 事件名称
   * @param {*} data - 事件数据
   */
  emit(eventName, data) {
    if (!this.events[eventName]) return;

    this.events[eventName].forEach(callback => {
      try {
        callback(data);
      } catch (e) {
        console.error(`事件处理错误 [${eventName}]:`, e);
      }
    });
  }

  /**
   * 只订阅一次事件
   * @param {string} eventName - 事件名称
   * @param {Function} callback - 回调函数
   */
  once(eventName, callback) {
    const unsubscribe = this.on(eventName, (data) => {
      unsubscribe();
      callback(data);
    });
  }
}

// 事件名称常量
const EVENTS = {
  // 数据更新事件
  DIET_DATA_UPDATED: 'diet:data:updated',
  WATER_DATA_UPDATED: 'water:data:updated',
  EXERCISE_DATA_UPDATED: 'exercise:data:updated',
  USER_DATA_UPDATED: 'user:data:updated',
  
  // 页面跳转事件
  PAGE_VISIBLE: 'page:visible',
  PAGE_HIDDEN: 'page:hidden',
  
  // 应用状态事件
  APP_READY: 'app:ready',
  LOGIN_SUCCESS: 'login:success',
  LOGOUT: 'logout'
};

// 创建单例
const eventBus = new EventBus();

module.exports = {
  EventBus,
  EVENTS,
  eventBus
};