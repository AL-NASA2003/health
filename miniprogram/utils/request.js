// 引入存储工具和缓存工具
const { getToken, clearStorage } = require('./storage');
const cache = require('./cache');

// Token过期标志，防止重复跳转登录页面
let isTokenExpired = false;
// 请求队列，用于限制并发请求数
const requestQueue = [];
// 当前正在执行的请求数
let currentRequests = 0;
// 最大并发请求数限制
const MAX_CONCURRENT_REQUESTS = 12;

// 待处理的请求映射，用于去重相同请求
const pendingRequests = new Map();

// 可缓存的HTTP方法配置
const CACHEABLE_METHODS = ['GET'];
// 缓存配置对象
const CACHE_CONFIG = {
  ENABLE_CACHE: true,              // 是否启用缓存
  DEFAULT_EXPIRY: 30 * 60 * 1000,   // 默认缓存过期时间（30分钟）
  CACHE_KEY_PREFIX: 'req:',          // 缓存键前缀
  MIN_CACHE_DURATION: 5000            // 最小缓存持续时间（5秒）
};

// 请求配置对象
const REQUEST_CONFIG = {
  DEFAULT_TIMEOUT: 5000,             // 默认请求超时时间（5秒）- 开发者工具使用更短的超时
  MAX_RETRIES: 1,                    // 最大重试次数（减少到1次）
  RETRY_DELAY: 500                   // 重试延迟时间（0.5秒）
};

/**
 * 生成请求缓存键
 * @param {string} url - 请求URL
 * @param {string} method - HTTP方法
 * @param {Object} data - 请求数据
 * @returns {string} 缓存键
 */
function getRequestCacheKey(url, method, data) {
  // 将请求参数序列化为字符串
  const params = JSON.stringify({ url, method, data });
  // 使用简单的哈希算法计算哈希值
  let hash = 0;
  for (let i = 0; i < params.length; i++) {
    const char = params.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  // 返回完整的缓存键
  return `${CACHE_CONFIG.CACHE_KEY_PREFIX}${method}:${url}:${Math.abs(hash).toString(16)}`;
}

function executeRequest(url, data, method, showLoading, useCache, retryCount = 0) {
  const token = getToken();
  const BASE_URL = 'http://localhost:5000/api';
  const cacheKey = getRequestCacheKey(url, method, data);

  if (useCache && CACHEABLE_METHODS.includes(method)) {
    const cachedData = cache.get(cacheKey);
    if (cachedData) {
      return Promise.resolve(cachedData);
    }
  }

  if (pendingRequests.has(cacheKey)) {
    return pendingRequests.get(cacheKey);
  }

  const requestPromise = new Promise((resolve, reject) => {
    if (currentRequests >= MAX_CONCURRENT_REQUESTS) {
      requestQueue.push({ cacheKey, resolve, reject, url, data, method, showLoading, useCache });
      return;
    }

    currentRequests++;

    wx.request({
      url: BASE_URL + url,
      data,
      method,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token || ''
      },
      timeout: REQUEST_CONFIG.DEFAULT_TIMEOUT,
      success: (res) => {
        currentRequests--;
        processNextRequest();

        if (showLoading) {
          wx.hideLoading();
        }

        if (res.statusCode === 200) {
          const responseData = res.data || {};
          const { code, msg, data: responseDataObj } = responseData;

          if (code === 0) {
            if (useCache && CACHEABLE_METHODS.includes(method)) {
              cache.set(cacheKey, { code, msg, data: responseDataObj }, CACHE_CONFIG.DEFAULT_EXPIRY);
            }
            resolve({ code, msg, data: responseDataObj });
          } else if (code === 401) {
            if (!isTokenExpired) {
              isTokenExpired = true;
              clearStorage();
              wx.showToast({
                title: '登录已过期',
                icon: 'none',
                duration: 1500
              });
              setTimeout(() => {
                isTokenExpired = false;
                wx.redirectTo({ url: '/pages/login/login' });
              }, 1500);
            }
            reject({ code, msg });
          } else {
            reject({ code, msg: msg || '请求失败' });
          }
        } else {
          // 服务器错误，尝试重试
          if (retryCount < REQUEST_CONFIG.MAX_RETRIES) {
            currentRequests--;
            processNextRequest();
            setTimeout(() => {
              executeRequest(url, data, method, showLoading, useCache, retryCount + 1)
                .then(resolve)
                .catch(reject);
            }, REQUEST_CONFIG.RETRY_DELAY);
          } else {
            currentRequests--;
            processNextRequest();
            if (showLoading) {
              wx.hideLoading();
            }
            reject({ code: res.statusCode, msg: '服务器错误' });
          }
        }
      },
      fail: (err) => {
        // 网络错误，尝试重试
        if (retryCount < REQUEST_CONFIG.MAX_RETRIES) {
          currentRequests--;
          processNextRequest();
          setTimeout(() => {
            executeRequest(url, data, method, showLoading, useCache, retryCount + 1)
              .then(resolve)
              .catch(reject);
          }, REQUEST_CONFIG.RETRY_DELAY);
        } else {
          currentRequests--;
          processNextRequest();
          if (showLoading) {
            wx.hideLoading();
          }
          reject({ code: -1, msg: '网络请求失败' });
        }
      }
    });
  });

  pendingRequests.set(cacheKey, requestPromise);
  requestPromise.finally(() => {
    pendingRequests.delete(cacheKey);
  });

  return requestPromise;
}

function processNextRequest() {
  if (requestQueue.length > 0 && currentRequests < MAX_CONCURRENT_REQUESTS) {
    const requestInfo = requestQueue.shift();
    executeRequest(
      requestInfo.url,
      requestInfo.data,
      requestInfo.method,
      requestInfo.showLoading,
      requestInfo.useCache
    ).then(requestInfo.resolve).catch(requestInfo.reject);
  }
}

function request(url, data = {}, method = 'POST', showLoading = true, useCache = true) {
  if (method === 'GET' && useCache === undefined) {
    useCache = true;
  }

  // 如果有缓存且可以使用，不显示loading
  if (useCache && CACHEABLE_METHODS.includes(method)) {
    const cacheKey = getRequestCacheKey(url, method, data);
    const cachedData = cache.get(cacheKey);
    if (cachedData) {
      // 有缓存，静默更新，不显示loading
      showLoading = false;
    }
  }

  // 只有当确实需要显示loading时才显示
  if (showLoading && currentRequests === 0) {
    wx.showLoading({
      title: '加载中...',
      mask: true
    });
  }

  return executeRequest(url, data, method, showLoading, useCache);
}

function get(url, data = {}, showLoading = true, useCache = true) {
  return request(url, data, 'GET', showLoading, useCache);
}

function post(url, data = {}, showLoading = true, useCache = false) {
  return request(url, data, 'POST', showLoading, useCache);
}

function put(url, data = {}, showLoading = true, useCache = false) {
  return request(url, data, 'PUT', showLoading, useCache);
}

function del(url, data = {}, showLoading = true, useCache = false) {
  return request(url, data, 'DELETE', showLoading, useCache);
}

function batchRequest(requests) {
  return Promise.all(requests.map(req => {
    const { url, data = {}, method = 'GET' } = req;
    return request(url, data, method, false);
  }));
}

function clearRequestCache() {
  try {
    const keys = wx.getStorageInfoSync().keys;
    // 清除所有与请求相关的缓存
    const requestCacheKeys = keys.filter(key => 
      key.startsWith('cache_') || key.startsWith(CACHE_CONFIG.CACHE_KEY_PREFIX)
    );
    requestCacheKeys.forEach(key => {
      try {
        if (key.startsWith('cache_')) {
          cache.remove(key.substring(6)); // 移除 'cache_' 前缀
        } else {
          cache.remove(key);
        }
      } catch (e) {
        console.log('清除单个缓存失败:', key, e);
      }
    });
    console.log('请求缓存清除完成，清除了', requestCacheKeys.length, '个缓存');
  } catch (e) {
    console.error('清除请求缓存失败:', e);
  }
}

module.exports = {
  request,
  get,
  post,
  put,
  del,
  batchRequest,
  clearRequestCache
};