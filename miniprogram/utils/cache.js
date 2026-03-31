const CACHE_CONFIG = {
  DEFAULT_EXPIRY: 5 * 60 * 1000,
  USER_INFO_EXPIRY: 10 * 60 * 1000,
  RECIPE_LIST_EXPIRY: 15 * 60 * 1000,
  HOT_FOOD_EXPIRY: 30 * 60 * 1000,
  INGREDIENT_EXPIRY: 20 * 60 * 1000,
  MAX_CACHE_SIZE: 150,
  PERSISTENT_KEYS: ['userInfo', 'token', 'systemConfig'],
  CLEANUP_INTERVAL: 60 * 1000,
  MIN_EXPIRY: 30 * 1000
};

const memoryCache = new Map();
const cacheStats = { hits: 0, misses: 0, size: 0 };

function generateKey(prefix, params) {
  if (!params) return prefix;
  const paramsStr = JSON.stringify(params);
  let hash = 0;
  for (let i = 0; i < paramsStr.length; i++) {
    const char = paramsStr.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return `${prefix}:${Math.abs(hash).toString(16)}`;
}

function set(key, value, expiry = CACHE_CONFIG.DEFAULT_EXPIRY, persistent = false) {
  const item = {
    value: value,
    expiry: Date.now() + expiry,
    timestamp: Date.now()
  };

  if (memoryCache.size >= CACHE_CONFIG.MAX_CACHE_SIZE) {
    const oldestKey = memoryCache.keys().next().value;
    memoryCache.delete(oldestKey);
  }
  memoryCache.set(key, item);

  if (persistent) {
    try {
      wx.setStorageSync(`cache_${key}`, item);
    } catch (e) {}
  }

  cacheStats.size = memoryCache.size;
}

function get(key) {
  const item = memoryCache.get(key);

  if (item) {
    if (Date.now() > item.expiry) {
      memoryCache.delete(key);
      try {
        wx.removeStorageSync(`cache_${key}`);
      } catch (e) {}
      cacheStats.misses++;
      return null;
    }
    cacheStats.hits++;
    return item.value;
  }

  try {
    const persistentItem = wx.getStorageSync(`cache_${key}`);
    if (persistentItem) {
      if (Date.now() <= persistentItem.expiry) {
        memoryCache.set(key, persistentItem);
        cacheStats.hits++;
        return persistentItem.value;
      } else {
        wx.removeStorageSync(`cache_${key}`);
      }
    }
  } catch (e) {}

  cacheStats.misses++;
  return null;
}

function remove(key) {
  memoryCache.delete(key);
  try {
    wx.removeStorageSync(`cache_${key}`);
  } catch (e) {}
  cacheStats.size = memoryCache.size;
}

function clear() {
  memoryCache.clear();
  try {
    wx.clearStorageSync();
  } catch (e) {}
  cacheStats.size = 0;
  cacheStats.hits = 0;
  cacheStats.misses = 0;
}

function cleanup() {
  const now = Date.now();
  const keysToDelete = [];
  
  // 清理过期缓存
  for (const [key, item] of memoryCache.entries()) {
    if (now > item.expiry) {
      keysToDelete.push(key);
    }
  }
  
  keysToDelete.forEach(key => {
    memoryCache.delete(key);
    try {
      wx.removeStorageSync(`cache_${key}`);
    } catch (e) {}
  });
  
  // 如果缓存仍然超出大小限制，删除最旧的缓存
  if (memoryCache.size > CACHE_CONFIG.MAX_CACHE_SIZE) {
    const entries = Array.from(memoryCache.entries());
    entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
    
    const excess = memoryCache.size - CACHE_CONFIG.MAX_CACHE_SIZE;
    for (let i = 0; i < excess; i++) {
      const key = entries[i][0];
      memoryCache.delete(key);
      try {
        wx.removeStorageSync(`cache_${key}`);
      } catch (e) {}
    }
  }
  
  cacheStats.size = memoryCache.size;
}

// 定期清理缓存
setInterval(cleanup, CACHE_CONFIG.CLEANUP_INTERVAL);

function getStats() {
  const hitRate = cacheStats.hits + cacheStats.misses > 0 
    ? ((cacheStats.hits / (cacheStats.hits + cacheStats.misses)) * 100).toFixed(2)
    : 0;
  
  return {
    size: cacheStats.size,
    hits: cacheStats.hits,
    misses: cacheStats.misses,
    hitRate: hitRate + '%'
  };
}

function preload(key, fetchFn, expiry) {
  if (!get(key)) {
    fetchFn().then(data => {
      set(key, data, expiry, CACHE_CONFIG.PERSISTENT_KEYS.includes(key));
    }).catch(err => {});
  }
}

function warmup() {
  // 轻量级缓存预热，只初始化内存缓存，不进行存储操作
  const warmupKeys = [
    'home:recipes',
    'home:hotfood',
    'hotfood:list',
    'user:info',
    'diet:stats'
  ];
  
  warmupKeys.forEach(key => {
    if (!memoryCache.has(key)) {
      memoryCache.set(key, {
        value: [],
        expiry: Date.now() + CACHE_CONFIG.DEFAULT_EXPIRY,
        timestamp: Date.now()
      });
    }
  });
}

/**
 * 批量设置缓存
 * @param {object} items - 键值对对象
 * @param {number} expiry - 过期时间
 * @param {boolean} persistent - 是否持久化
 */
function batchSet(items, expiry = CACHE_CONFIG.DEFAULT_EXPIRY, persistent = false) {
  Object.entries(items).forEach(([key, value]) => {
    set(key, value, expiry, persistent);
  });
}

/**
 * 批量获取缓存
 * @param {array} keys - 键数组
 * @returns {object} 键值对对象
 */
function batchGet(keys) {
  const result = {};
  keys.forEach(key => {
    result[key] = get(key);
  });
  return result;
}

module.exports = {
  set,
  get,
  remove,
  clear,
  cleanup,
  getStats,
  preload,
  warmup,
  batchSet,
  batchGet,
  generateKey,
  CACHE_CONFIG
};