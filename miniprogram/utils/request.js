const { getToken, clearStorage } = require('./storage');
const cache = require('./cache');

let isTokenExpired = false;
const requestQueue = [];
let currentRequests = 0;
const MAX_CONCURRENT_REQUESTS = 12;

const pendingRequests = new Map();

const CACHEABLE_METHODS = ['GET'];
const CACHE_CONFIG = {
  ENABLE_CACHE: true,
  DEFAULT_EXPIRY: 30 * 60 * 1000, // 延长到30分钟
  CACHE_KEY_PREFIX: 'req:',
  MIN_CACHE_DURATION: 5000
};

const REQUEST_CONFIG = {
  DEFAULT_TIMEOUT: 8000,
  MAX_RETRIES: 2,
  RETRY_DELAY: 1000
};

function getRequestCacheKey(url, method, data) {
  const params = JSON.stringify({ url, method, data });
  let hash = 0;
  for (let i = 0; i < params.length; i++) {
    const char = params.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
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
    const requestCacheKeys = keys.filter(key => key.startsWith(`cache_${CACHE_CONFIG.CACHE_KEY_PREFIX}`));
    requestCacheKeys.forEach(key => cache.remove(key.substring(6))); // 移除 'cache_' 前缀
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