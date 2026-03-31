/**
 * 本地缓存工具
 * 用户信息、Token等数据存储
 */

/**
 * 存储数据到本地
 * @param {string} key 键名
 * @param {any} data 数据
 */
function setStorage(key, data) {
  try {
    wx.setStorageSync(key, data);
    return true;
  } catch (e) {
    console.error('存储数据失败:', e);
    return false;
  }
}

/**
 * 从本地获取数据
 * @param {string} key 键名
 * @param {any} defaultValue 默认值
 */
function getStorage(key, defaultValue = null) {
  try {
    const value = wx.getStorageSync(key);
    return value !== undefined && value !== null ? value : defaultValue;
  } catch (e) {
    console.error('获取数据失败:', e);
    return defaultValue;
  }
}

/**
 * 从本地移除数据
 * @param {string} key 键名
 */
function removeStorage(key) {
  try {
    wx.removeStorageSync(key);
    return true;
  } catch (e) {
    console.error('移除数据失败:', e);
    return false;
  }
}

/**
 * 清空本地所有数据
 */
function clearStorage() {
  try {
    wx.clearStorageSync();
    return true;
  } catch (e) {
    console.error('清空数据失败:', e);
    return false;
  }
}

/**
 * 存储用户信息
 * @param {Object} userInfo 用户信息
 */
function setUserInfo(userInfo) {
  return setStorage('userInfo', userInfo);
}

/**
 * 获取用户信息
 */
function getUserInfo() {
  return getStorage('userInfo', null);
}

/**
 * 存储Token
 * @param {string} token Token字符串
 */
function setToken(token) {
  return setStorage('token', token);
}

/**
 * 获取Token
 */
function getToken() {
  return getStorage('token', '');
}

/**
 * 存储搜索历史
 * @param {string} keyword 搜索关键词
 */
function addSearchHistory(keyword) {
  let history = getStorage('searchHistory', []);
  // 去重
  history = history.filter(item => item !== keyword);
  // 添加到开头
  history.unshift(keyword);
  // 最多保存10条
  if (history.length > 10) {
    history = history.slice(0, 10);
  }
  return setStorage('searchHistory', history);
}

/**
 * 获取搜索历史
 */
function getSearchHistory() {
  return getStorage('searchHistory', []);
}

/**
 * 清空搜索历史
 */
function clearSearchHistory() {
  return removeStorage('searchHistory');
}

/**
 * 存储收藏列表
 * @param {Array} favorites 收藏列表
 */
function setFavorites(favorites) {
  return setStorage('favorites', favorites);
}

/**
 * 获取收藏列表
 */
function getFavorites() {
  return getStorage('favorites', []);
}

/**
 * 添加收藏
 * @param {Object} item 收藏项
 */
function addFavorite(item) {
  const favorites = getFavorites();
  // 检查是否已存在
  const exists = favorites.some(fav => fav.id === item.id);
  if (!exists) {
    favorites.unshift(item);
    return setFavorites(favorites);
  }
  return true;
}

/**
 * 移除收藏
 * @param {string|number} id 收藏项ID
 */
function removeFavorite(id) {
  let favorites = getFavorites();
  favorites = favorites.filter(item => item.id !== id);
  return setFavorites(favorites);
}

/**
 * 检查是否已收藏
 * @param {string|number} id 收藏项ID
 */
function isFavorite(id) {
  const favorites = getFavorites();
  return favorites.some(item => item.id === id);
}

module.exports = {
  setStorage,
  getStorage,
  removeStorage,
  clearStorage,
  setUserInfo,
  getUserInfo,
  setToken,
  getToken,
  addSearchHistory,
  getSearchHistory,
  clearSearchHistory,
  setFavorites,
  getFavorites,
  addFavorite,
  removeFavorite,
  isFavorite
};
