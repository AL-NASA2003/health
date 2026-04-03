const { get, batchRequest } = require('../../utils/request');
const { getUserInfo, setUserInfo } = require('../../utils/storage');
const { loginGuard } = require('../../utils/auth');
const cache = require('../../utils/cache');
const { loadFromCache, navigateTo } = require('../../utils/common');

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
    skeletonShow: true
  },

  lastRefreshTime: 0,
  REFRESH_INTERVAL: 30000,

  onLoad(options) {
    // 不强制登录验证，首页可以查看
    this.setCurrentDate();
    
    // 立即显示默认数据，快速展示内容 - 不等待任何请求
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
    
    // 延迟加载缓存和网络数据，避免阻塞页面显示
    setTimeout(() => {
      // 尝试从缓存加载数据
      this.loadFromStorageFirst();
      
      // 同时发起网络请求更新数据
      this.loadAllData();
    }, 100);
  },

  onShow() {
    const now = Date.now();
    if (now - this.lastRefreshTime > this.REFRESH_INTERVAL) {
      // 延长刷新间隔，避免频繁请求
      this.refreshData();
      this.lastRefreshTime = now;
    }
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
    
    // 立即关闭骨架屏，显示内容
    updateData.skeletonShow = false;
    
    if (Object.keys(updateData).length > 0) {
      this.setData(updateData);
    }
  },

  loadAllData() {
    const today = new Date().toISOString().split('T')[0];
    
    // 优先从缓存加载数据
    const cachedUserInfo = getUserInfo();
    const cachedRecipes = cache.get('home:recipes');
    const cachedHotFood = cache.get('home:hotfood');
    
    // 异步请求最新数据 - 不显示loading
    const requests = [
      { url: '/user/info', method: 'GET' },
      { url: '/diet/record', data: { start_date: today, end_date: today }, method: 'GET' },
      { url: '/recipe/list', method: 'GET' },
      { url: '/hotfood/list', method: 'GET' }
    ];
    
    batchRequest(requests)
      .then(([userInfoRes, dietStatsRes, recipeRes, hotFoodRes]) => {
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
        
        // 获取饮水和运动记录数据
        this.getTodayWaterAndExerciseStats();
      })
      .catch(() => {
        // 保持默认数据，不做任何处理
        // 获取饮水和运动记录数据
        this.getTodayWaterAndExerciseStats();
      });
  },

  refreshData() {
    get('/user/info', {}, false, true)
      .then((result) => {
        if (result && result.data) {
          setUserInfo(result.data);
          this.setData({ userInfo: result.data });
        }
      })
      .catch(() => {});
    
    this.getTodayDietStats();
    this.getTodayWaterAndExerciseStats();
  },

  getTodayWaterAndExerciseStats() {
    const today = new Date().toISOString().split('T')[0];
    
    // 获取饮水记录
    const waterData = wx.getStorageSync(`water_${today}`);
    const totalWater = waterData?.totalAmount || 0;
    
    // 获取运动记录
    const exerciseData = wx.getStorageSync(`exercise_${today}`);
    const exerciseRecords = exerciseData?.records || [];
    
    // 计算运动总时间
    let totalExerciseDuration = 0;
    exerciseRecords.forEach(record => {
      totalExerciseDuration += record.duration || 0;
    });
    
    // 更新数据
    this.setData({
      waterAmount: totalWater,
      exerciseDuration: totalExerciseDuration
    });
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

  loadMockRecipes() {
    this.setData({
      recommendedRecipes: [
        {
          id: 1,
          recipe_name: '健康沙拉',
          image: '',
          calorie: 350,
          cooking_time: 15,
          tags: ['低脂', '素食']
        },
        {
          id: 2,
          recipe_name: '烤鸡胸肉',
          image: '',
          calorie: 420,
          cooking_time: 25,
          tags: ['高蛋白', '低碳水']
        },
        {
          id: 3,
          recipe_name: '清蒸鱼',
          image: '',
          calorie: 380,
          cooking_time: 20,
          tags: ['低脂', '高蛋白']
        },
        {
          id: 4,
          recipe_name: '蔬菜炒饭',
          image: '',
          calorie: 450,
          cooking_time: 18,
          tags: ['均衡', '素食']
        }
      ]
    });
  },

  loadMockHotFood() {
    this.setData({
      hotFoodList: [
        {
          id: 1,
          title: '健康饮食的重要性',
          image: '',
          likes: 128,
          source: '健康生活',
          tags: ['健康', '饮食']
        },
        {
          id: 2,
          title: '如何科学减脂',
          image: '',
          likes: 96,
          source: '营养专家',
          tags: ['减脂', '营养']
        },
        {
          id: 3,
          title: '增肌必备食物',
          image: '',
          likes: 85,
          source: '健身教练',
          tags: ['增肌', '健身']
        }
      ]
    });
  },

  getTodayDietStats() {
    const today = new Date().toISOString().split('T')[0];
    
    get('/diet/record', {
      start_date: today,
      end_date: today
    }, false, true)
      .then((result) => {
        if (result && result.data && result.data.list) {
          this.processDietStats(result.data.list);
        }
      })
      .catch(() => {
        // 保持默认数据
      });
  },

  processDietStats(records) {
    let calorie = 0, protein = 0, carb = 0, fat = 0;
    
    records.forEach(record => {
      calorie += Number(record.calorie) || 0;
      protein += Number(record.protein) || 0;
      carb += Number(record.carb) || 0;
      fat += Number(record.fat) || 0;
    });
    
    this.setData({
      dietStats: {
        loading: false,
        total: records.length,
        calorie: calorie.toFixed(1),
        protein: protein.toFixed(1),
        carb: carb.toFixed(1),
        fat: fat.toFixed(1)
      }
    });
  },

  loadMockStats() {
    this.setData({
      dietStats: {
        loading: false,
        total: 3,
        calorie: '1250.5',
        protein: '65.2',
        carb: '158.3',
        fat: '42.1'
      }
    });
  },

  loadFallbackData() {
    this.loadMockStats();
    this.loadMockRecipes();
    this.loadMockHotFood();
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