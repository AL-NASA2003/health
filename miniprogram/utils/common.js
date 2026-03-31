// 公共工具函数

/**
 * 格式化日期
 * @param {Date} date - 日期对象
 * @param {string} format - 格式化类型: 'date', 'datetime', 'time', 'yearMonthDay'
 * @returns {string} 格式化后的日期字符串
 */
function formatDate(date, format = 'date') {
  const now = date || new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hour = String(now.getHours()).padStart(2, '0');
  const minute = String(now.getMinutes()).padStart(2, '0');
  const second = String(now.getSeconds()).padStart(2, '0');

  switch (format) {
    case 'datetime':
      return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
    case 'time':
      return `${hour}:${minute}`;
    case 'yearMonthDay':
      return `${year}年${month}月${day}日`;
    default:
      return `${year}-${month}-${day}`;
  }
}

/**
 * 验证数字输入
 * @param {string|number} value - 输入值
 * @param {object} options - 验证选项
 * @returns {object} 验证结果
 */
function validateNumber(value, options = {}) {
  const { min = 0, max = 10000, required = true } = options;
  
  if (required && !value) {
    return { valid: false, message: '请输入数值' };
  }
  
  const num = Number(value);
  if (isNaN(num)) {
    return { valid: false, message: '请输入有效的数字' };
  }
  
  if (num < min || num > max) {
    return { valid: false, message: `请输入${min}-${max}之间的数值` };
  }
  
  return { valid: true };
}

/**
 * 验证表单字段
 * @param {object} formData - 表单数据
 * @param {object} rules - 验证规则
 * @returns {object} 验证结果
 */
function validateForm(formData, rules) {
  for (const [key, rule] of Object.entries(rules)) {
    const value = formData[key];
    
    if (rule.required && !value) {
      return { valid: false, message: rule.message || `请输入${key}` };
    }
    
    if (rule.type === 'number') {
      const numberValidation = validateNumber(value, rule);
      if (!numberValidation.valid) {
        return numberValidation;
      }
    }
    
    if (rule.minLength && value.length < rule.minLength) {
      return { valid: false, message: `最少需要${rule.minLength}个字符` };
    }
    
    if (rule.maxLength && value.length > rule.maxLength) {
      return { valid: false, message: `最多只能${rule.maxLength}个字符` };
    }
  }
  
  return { valid: true };
}

/**
 * 显示Toast消息
 * @param {string} title - 消息内容
 * @param {string} icon - 图标类型
 * @param {number} duration - 持续时间
 */
function showToast(title, icon = 'none', duration = 1500) {
  wx.showToast({
    title,
    icon,
    duration
  });
}

/**
 * 显示确认对话框
 * @param {string} title - 标题
 * @param {string} content - 内容
 * @returns {Promise<boolean>} 是否确认
 */
function showConfirm(title, content) {
  return new Promise((resolve) => {
    wx.showModal({
      title,
      content,
      success: (res) => {
        resolve(res.confirm);
      },
      fail: () => {
        resolve(false);
      }
    });
  });
}

/**
 * 计算数组总和
 * @param {array} array - 数组
 * @param {string} key - 要计算的属性名
 * @returns {number} 总和
 */
function calculateSum(array, key) {
  return array.reduce((sum, item) => sum + (item[key] || 0), 0);
}

/**
 * 节流函数
 * @param {function} func - 要执行的函数
 * @param {number} wait - 等待时间
 * @returns {function} 节流后的函数
 */
function throttle(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * 防抖函数
 * @param {function} func - 要执行的函数
 * @param {number} wait - 等待时间
 * @returns {function} 防抖后的函数
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * 从缓存加载数据
 * @param {string} cacheKey - 缓存键
 * @param {Function} callback - 回调函数
 */
function loadFromCache(cacheKey, callback) {
  const cache = require('./cache');
  const cachedData = cache.get(cacheKey);
  if (cachedData) {
    callback && callback(cachedData);
    return true;
  }
  return false;
}

/**
 * 导航到页面
 * @param {string} url - 页面路径
 * @param {string} type - 导航类型: 'navigate', 'switch', 'redirect'
 */
function navigateTo(url, type = 'navigate') {
  switch (type) {
    case 'switch':
      wx.switchTab({ url });
      break;
    case 'redirect':
      wx.redirectTo({ url });
      break;
    default:
      wx.navigateTo({ url });
  }
}

module.exports = {
  formatDate,
  validateNumber,
  validateForm,
  showToast,
  showConfirm,
  calculateSum,
  throttle,
  debounce,
  loadFromCache,
  navigateTo
};
