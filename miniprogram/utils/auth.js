const { getToken, getUserInfo } = require('./storage');

/**
 * 检查登录状态
 * @returns {Boolean} 是否已登录
 */
function checkLogin() {
  const token = getToken();
  const userInfo = getUserInfo();
  return !!token && !!userInfo;
}

/**
 * 登录拦截（页面跳转前校验）
 * @param {Object} options 页面参数
 * @returns {Boolean} 是否允许跳转
 */
function loginGuard(options = {}) {
  if (!checkLogin()) {
    wx.showToast({
      title: '请先登录',
      icon: 'none',
      duration: 2000
    });
    // 跳转到登录页
    wx.redirectTo({
      url: '/pages/login/login'
    });
    return false;
  }
  return true;
}

module.exports = {
  checkLogin,
  loginGuard
};