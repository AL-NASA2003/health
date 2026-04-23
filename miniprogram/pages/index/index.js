const { get, batchRequest } = require('../../utils/request');
const { getUserInfo, setUserInfo } = require('../../utils/storage');
const { loginGuard } = require('../../utils/auth');
const cache = require('../../utils/cache');
const { loadFromCache, navigateTo } = require('../../utils/common');
const app = getApp();

Page({
  data: {
    userInfo: {},
    currentDate: '',
    dietStats: {
      loading: true,
      total: 0,
      calorie: 0,
      protein: 0,
      carb: 0,
      fat: 0
    },
    recommendedRecipes: [],
    hotFoodList: [],
    loading: true,
    skeletonShow: true,
    hasError: false,
    errorMessage: ''
  },

  lastRefreshTime: 0,
  REFRESH_INTERVAL: 30000,
  unsubscribeFunctions: [],

  onLoad(options) {
    console.log('🏠 首页加载');
    
    this.setCurrentDate();
    
    this.setData({ 
      loading: false,
      skeletonShow: false,
      userInfo: {
        id: 1,
        nickname: '测试用户',
        avatar: '',
        daily_calorie: 2000,
        health_goal: '健康生活'
      },
      dietStats: {
        loading: false,
        total: 3,
        calorie: '1250.5',
        protein: '65.2',
        carb: '158.3',
        fat: '42.1'
      },
      recommendedRecipes: [
        { id: 1, recipe_name: '健康沙拉', image: '', calorie: 350, cooking_time: 15, tags: ['低脂', '素食'] },
        { id: 2, recipe_name: '烤鸡胸肉', image: '', calorie: 420, cooking_time: 25, tags: ['高蛋白', '低碳水'] },
        { id: 3, recipe_name: '清蒸鱼', image: '', calorie: 380, cooking_time: 20, tags: ['低脂', '高蛋白'] },
        { id: 4, recipe_name: '蔬菜炒饭', image: '', calorie: 450, cooking_time: 18, tags: ['均衡', '素食'] }
      ],
      hotFoodList: [
        { id: 1, title: '健康饮食的重要性', image: '', likes: 128, source: '健康生活', tags: ['健康', '饮食'] },
        { id: 2, title: '如何科学减脂', image: '', likes: 96, source: '营养专家', tags: ['减脂', '营养'] },
        { id: 3, title: '增肌必备食物', image: '', likes: 85, source: '健身教练', tags: ['增肌', '健身'] }
      ]
    });
    
    this.setupEventListeners();
    
    setTimeout(() => {
      this.loadFromStorageFirst();
      
      setTimeout(() => {
        this.loadAllData();
      }, 300);
    }, 100);
  },

  onShow() {
    console.log('🏠 首页显示');
    const now = Date.now();
    
    // 每次首页显示都强制刷新一下今日饮食（更可靠！）
    console.log('🔄 强制刷新今日饮食统计！');
    this.getTodayDietStats();
    
    this.lastRefreshTime = now;
  },
  
  // 跳转到登录页面（以防万一需要）
  goToLogin() {
    wx.navigateTo({
      url: '/pages/login/login'
    });
  },

  onUnload() {
    this.cleanupEventListeners();
  },

  onHide() {
  },

  setupEventListeners() {
    console.log('📋 设置事件监听器');
    
    const unsubscribe1 = app.eventBus.on(app.EVENTS.DIET_DATA_UPDATED, () => {
      console.log('📡 收到饮食数据更新事件');
      this.getTodayDietStats();
    });
    
    const unsubscribe2 = app.eventBus.on(app.EVENTS.WATER_DATA_UPDATED, () => {
      console.log('📡 收到饮水数据更新事件');
      // 可以在这里添加饮水数据更新逻辑
    });
    
    const unsubscribe3 = app.eventBus.on(app.EVENTS.EXERCISE_DATA_UPDATED, () => {
      console.log('📡 收到运动数据更新事件');
      // 可以在这里添加运动数据更新逻辑
    });
    
    this.unsubscribeFunctions = [unsubscribe1, unsubscribe2, unsubscribe3];
  },

  cleanupEventListeners() {
    console.log('🧹 清理事件监听器');
    this.unsubscribeFunctions.forEach(unsubscribe => {
      if (unsubscribe && typeof unsubscribe === 'function') {
        unsubscribe();
      }
    });
    this.unsubscribeFunctions = [];
  },

  loadFromStorageFirst() {
    const cachedUserInfo = getUserInfo();
    const cachedRecipes = cache.get('home:recipes');
    const cachedHotFood = cache.get('home:hotfood');
    
    const updateData = {};
    
    if (cachedUserInfo) {
      updateData.userInfo = cachedUserInfo;
    }
    
    if (cachedRecipes && cachedRecipes.length > 0) {
      updateData.recommendedRecipes = cachedRecipes;
    }
    
    if (cachedHotFood && cachedHotFood.length > 0) {
      updateData.hotFoodList = cachedHotFood;
    }
    
    updateData.skeletonShow = false;
    
    if (Object.keys(updateData).length > 0) {
      this.setData(updateData);
    }
  },

  loadAllData() {
    console.log('📊 加载所有数据');
    const today = new Date().toISOString().split('T')[0];
    
    const cachedUserInfo = getUserInfo();
    const cachedRecipes = cache.get('home:recipes');
    const cachedHotFood = cache.get('home:hotfood');
    
    // 优化：分批加载，减少并发压力
    this.loadUserAndDiet(today).then(() => {
      setTimeout(() => {
        this.loadRecipesAndHotFood();
      }, 200);
    });
  },

  loadUserAndDiet(today) {
    console.log('👤 加载用户和饮食数据');
    const requests = [
      { url: '/user/info', method: 'GET' },
      { url: '/diet/record', data: { start_date: today, end_date: today }, method: 'GET' }
    ];
    
    return batchRequest(requests)
      .then(([userInfoRes, dietStatsRes]) => {
        const updateData = {};
        
        if (userInfoRes && userInfoRes.data) {
          setUserInfo(userInfoRes.data);
          updateData.userInfo = userInfoRes.data;
        }
        
        if (dietStatsRes && dietStatsRes.data && dietStatsRes.data.list) {
          let calorie = 0, protein = 0, carb = 0, fat = 0;
          dietStatsRes.data.list.forEach(record => {
            calorie += Number(record.calorie) || 0;
            protein += Number(record.protein) || 0;
            carb += Number(record.carb) || 0;
            fat += Number(record.fat) || 0;
          });
          updateData.dietStats = {
            loading: false,
            total: dietStatsRes.data.list.length,
            calorie: calorie.toFixed(1),
            protein: protein.toFixed(1),
            carb: carb.toFixed(1),
            fat: fat.toFixed(1)
          };
        }
        
        if (Object.keys(updateData).length > 0) {
          this.setData(updateData);
        }
      })
      .catch((err) => {
        console.error('❌ 加载用户和饮食数据失败:', err);
      });
  },

  loadRecipesAndHotFood() {
    console.log('🍳 加载食谱和热点美食');
    const requests = [
      { url: '/recipe/list', method: 'GET' },
      { url: '/hotfood/list', method: 'GET' }
    ];
    
    return batchRequest(requests)
      .then(([recipeRes, hotFoodRes]) => {
        const updateData = {};
        
        if (recipeRes && recipeRes.data && recipeRes.data.list) {
          const recipes = recipeRes.data.list.slice(0, 4);
          updateData.recommendedRecipes = recipes;
          cache.set('home:recipes', recipes, cache.CACHE_CONFIG.RECIPE_LIST_EXPIRY);
        }
        
        if (hotFoodRes && hotFoodRes.data && hotFoodRes.data.list) {
          const hotFood = hotFoodRes.data.list.slice(0, 3);
          updateData.hotFoodList = hotFood;
          cache.set('home:hotfood', hotFood, cache.CACHE_CONFIG.HOT_FOOD_EXPIRY);
        }
        
        if (Object.keys(updateData).length > 0) {
          this.setData(updateData);
        }
      })
      .catch((err) => {
        console.error('❌ 加载食谱和热点美食失败:', err);
      });
  },

  refreshData() {
    console.log('🔄 刷新数据');
    get('/user/info', {}, false, true)
      .then((result) => {
        if (result && result.data) {
          setUserInfo(result.data);
          this.setData({ userInfo: result.data });
        }
      })
      .catch(() => {});
    
    this.getTodayDietStats();
  },

  setCurrentDate() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][today.getDay()];
    this.setData({
      currentDate: `${year}-${month}-${day} ${week}`
    });
  },

  getTodayDietStats() {
    console.log('🥗 获取今日饮食统计（强制刷新，不使用缓存）');
    const today = new Date().toISOString().split('T')[0];
    console.log('📅 今天日期：', today);
    
    // 第四个参数设为 false，强制不使用缓存，确保获取最新数据
    get('/diet/record', {
      start_date: today,
      end_date: today
    }, false, false)
      .then((result) => {
        console.log('📊 收到饮食统计响应：', result);
        if (result && result.data && result.data.list) {
          console.log('📋 饮食记录列表：', result.data.list);
          this.processDietStats(result.data.list);
        }
      })
      .catch((err) => {
        console.error('❌ 获取饮食统计失败：', err);
      });
  },

  processDietStats(records) {
    console.log('🔍 开始处理统计，原始记录数：', records.length);
    
    let calorie = 0, protein = 0, carb = 0, fat = 0;
    
    records.forEach((record, index) => {
      console.log(`   [${index}] id=${record.id}, name=${record.food_name}, calorie=${record.calorie}`);
      calorie += Number(record.calorie) || 0;
      protein += Number(record.protein) || 0;
      carb += Number(record.carb) || 0;
      fat += Number(record.fat) || 0;
    });
    
    const newStats = {
      loading: false,
      total: records.length,
      calorie: calorie.toFixed(1),
      protein: protein.toFixed(1),
      carb: carb.toFixed(1),
      fat: fat.toFixed(1)
    };
    
    console.log('📊 计算结果：', newStats);
    console.log('📊 更新前的dietStats：', this.data.dietStats);
    
    this.setData({
      dietStats: newStats
    }, () => {
      console.log('✅ setData回调执行！');
      console.log('✅ 更新后的dietStats：', this.data.dietStats);
    });
  },

  goToUserInfo() {
    navigateTo('/pages/user/user');
  },

  goToUserDetail() {
    navigateTo('/pages/user/edit-profile/edit-profile');
  },

  goToRecords() {
    console.log('首页点击了我的记录');
    wx.switchTab({
      url: '/pages/records/records',
      success: function(res) {
        console.log('首页跳转成功', res);
      },
      fail: function(err) {
        console.log('首页跳转失败', err);
        wx.showToast({
          title: '跳转失败',
          icon: 'none'
        });
      }
    });
  },

  goToDiet() {
    navigateTo('/pages/records/records');
  },

  goToRecipe() {
    navigateTo('/pages/recipe/recipe', 'switch');
  },

  goToIngredient() {
    navigateTo('/pages/ingredient/ingredient');
  },

  goToHotFood() {
    navigateTo('/pages/hotfood/hotfood', 'switch');
  },

  goToForum() {
    navigateTo('/pages/forum/forum');
  },

  goToHandbook() {
    navigateTo('/pages/handbook/handbook');
  },

  goToRecipeDetail(e) {
    const recipeId = e.currentTarget.dataset.id;
    navigateTo(`/pages/recipe-detail/recipe-detail?id=${recipeId}`);
  },

  goToHotFoodDetail(e) {
    const foodId = e.currentTarget.dataset.id;
    navigateTo(`/pages/hotfood/hotfood?id=${foodId}`);
  },

  goToWater() {
    navigateTo('/pages/records/records');
  },

  goToExercise() {
    navigateTo('/pages/records/records');
  },

  goToHealth() {
    navigateTo('/pages/health/health');
  },

  goToRecipeCalendar() {
    navigateTo('/pages/recipe-calendar/recipe-calendar');
  },

  goToAddDiet() {
    navigateTo('/pages/diet/add-diet/add-diet');
  }
});