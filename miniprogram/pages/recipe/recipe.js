const { get, post, del } = require('../../utils/request');
const { getUserInfo } = require('../../utils/storage');
const { loginGuard } = require('../../utils/auth');

Page({
  data: {
    recipeList: [],
    filteredList: [],
    loading: false,
    hasRecommend: false,
    filterTypes: ['全部', '减脂', '增肌', '清淡', '高蛋白', '低碳水', '低脂肪', '素食', '快手菜', '家常菜'],
    filterIndex: 0,
    showStepDialog: false,
    currentRecipe: {},
    cookSteps: [],
    userInfo: null,
    nutritionNeeds: null,
    dailyMealPlan: null,
    collectedRecipes: []
  },

  // 页面加载
  onLoad(options) {
    if (!loginGuard()) return;
    
    // 立即显示默认数据，不等待网络请求
    this.loadMockData();
    
    // 延迟发起网络请求更新数据
    setTimeout(() => {
      this.getUserInfo();
      this.getCollectedRecipes();
      this.getAllRecipe();
    }, 100);
  },

  // 页面显示
  onShow() {
    // 重新获取用户信息，确保获取到最新的健康目标
    this.getUserInfo();
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.getAllRecipe(() => {
      wx.stopPullDownRefresh();
    });
  },

  // 获取用户信息 - 从服务器获取最新数据
  getUserInfo() {
    const localUserInfo = getUserInfo();
    if (localUserInfo) {
      this.setData({ userInfo: localUserInfo });
    }
    
    // 同时从服务器获取最新用户信息 - 不显示loading
    get('/user/info', {}, false)
      .then((result) => {
        if (result && result.data) {
          const { setUserInfo } = require('../../utils/storage');
          setUserInfo(result.data);
          this.setData({ userInfo: result.data });
        }
      })
      .catch((err) => {
        console.error('从服务器获取用户信息失败：', err);
      });
  },

  // 获取收藏的食谱
  getCollectedRecipes() {
    get('/recipe/collection/list', {}, false)
      .then((result) => {
        if (result && result.data && result.data.list) {
          const collectedIds = result.data.list.map(item => item.id);
          this.setData({ collectedRecipes: collectedIds });
        }
      })
      .catch((err) => {
        console.error('获取收藏食谱失败：', err);
      });
  },

  // 获取所有食谱
  getAllRecipe(callback) {
    get('/recipe/list', {}, false)
      .then((result) => {
        if (result && result.data && result.data.list) {
          this.setData({
            recipeList: result.data.list,
            filteredList: result.data.list
          });
        }
        callback && callback();
      })
      .catch((err) => {
        console.error('获取食谱列表失败：', err);
        // 保持默认数据
        callback && callback();
      });
  },

  // 加载模拟数据
  loadMockData() {
    const mockRecipes = [
      {
        id: 1,
        recipe_name: '低脂鸡胸肉沙拉',
        calorie: 280,
        protein: 32,
        carb: 15,
        fat: 8,
        flavor: '清淡',
        cook_step: '1. 鸡胸肉切块，用盐和黑胡椒腌制10分钟\n2. 热锅少油，煎至两面金黄\n3. 生菜、番茄、黄瓜洗净切块\n4. 将所有食材混合，淋上橄榄油和柠檬汁',
        ingre_list: '鸡胸肉200g，生菜100g，番茄1个，黄瓜1根，橄榄油10ml，柠檬汁5ml，盐、黑胡椒适量',
        cook_type: '煎',
        suitable_crowd: '减脂人群',
        image: ''
      },
      {
        id: 2,
        recipe_name: '清蒸鲈鱼',
        calorie: 180,
        protein: 28,
        carb: 5,
        fat: 6,
        flavor: '清淡',
        cook_step: '1. 鲈鱼洗净，划几刀\n2. 放入葱姜蒜，淋上料酒\n3. 大火蒸10-12分钟\n4. 出锅淋上蒸鱼豉油',
        ingre_list: '鲈鱼1条，葱1根，姜5片，蒜2瓣，料酒10ml，蒸鱼豉油15ml',
        cook_type: '蒸',
        suitable_crowd: '所有人群',
        image: ''
      },
      {
        id: 3,
        recipe_name: '燕麦蓝莓粥',
        calorie: 220,
        protein: 8,
        carb: 42,
        fat: 4,
        flavor: '清淡',
        cook_step: '1. 燕麦加水煮开\n2. 小火慢煮15分钟\n3. 加入蓝莓和蜂蜜\n4. 搅拌均匀即可',
        ingre_list: '燕麦50g，蓝莓50g，蜂蜜10g，水300ml',
        cook_type: '煮',
        suitable_crowd: '早餐',
        image: ''
      },
      {
        id: 4,
        recipe_name: '西兰花炒虾仁',
        calorie: 200,
        protein: 25,
        carb: 10,
        fat: 8,
        flavor: '清淡',
        cook_step: '1. 虾仁去壳去虾线\n2. 西兰花切小朵焯水\n3. 热锅少油，先炒虾仁\n4. 加入西兰花翻炒，调味即可',
        ingre_list: '虾仁150g，西兰花200g，蒜末5g，盐、白胡椒适量',
        cook_type: '炒',
        suitable_crowd: '增肌人群',
        image: ''
      },
      {
        id: 5,
        recipe_name: '番茄牛腩',
        calorie: 350,
        protein: 22,
        carb: 18,
        fat: 20,
        flavor: '酸甜',
        cook_step: '1. 牛腩切块焯水\n2. 番茄切块\n3. 热锅炒番茄出汁\n4. 加入牛腩炖煮1小时',
        ingre_list: '牛腩500g，番茄3个，洋葱1个，姜5片，料酒10ml，盐适量',
        cook_type: '炖',
        suitable_crowd: '增肌人群',
        image: ''
      },
      {
        id: 6,
        recipe_name: '蒜蓉菠菜',
        calorie: 80,
        protein: 4,
        carb: 8,
        fat: 4,
        flavor: '清淡',
        cook_step: '1. 菠菜洗净焯水\n2. 蒜切末\n3. 热锅少油爆香蒜\n4. 加入菠菜翻炒调味即可',
        ingre_list: '菠菜300g，蒜末10g，盐适量',
        cook_type: '炒',
        suitable_crowd: '减脂人群',
        image: ''
      }
    ];

    this.setData({
      recipeList: mockRecipes,
      filteredList: mockRecipes,
      loading: false
    });
  },

  // 获取个性化推荐
  getRecommendRecipe() {
    // 检查用户健康目标
    const userInfo = this.data.userInfo || getUserInfo();
    console.log('用户信息：', userInfo);
    if (!userInfo || !userInfo.health_goal) {
      wx.showModal({
        title: '提示',
        content: '请先完善个人健康目标信息',
        confirmText: '去完善',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({
              url: '/pages/user/edit-profile/edit-profile'
            });
          }
        }
      });
      return;
    }

    // 不显示 loading 弹窗，静默更新
    post('/recipe/recommend', {}, false)
      .then((result) => {
        if (result && result.data) {
          this.setData({
            recipeList: result.data.recommend_list || [],
            filteredList: result.data.recommend_list || [],
            hasRecommend: true,
            nutritionNeeds: result.data.nutrition_needs,
            dailyMealPlan: result.data.daily_meal_plan
          });
          wx.showToast({ title: '推荐成功' });
        }
      })
      .catch((err) => {
        console.error('获取推荐食谱失败：', err);
        // 保持默认数据，不做任何处理
      });
  },

  // 筛选食谱
  onFilterChange(e) {
    const index = e.detail.value;
    const filterType = this.data.filterTypes[index];
    let filteredList = [...this.data.recipeList];

    // 根据筛选条件过滤
    switch (filterType) {
      case '减脂':
        filteredList = filteredList.filter(item => item.calorie <= 300);
        break;
      case '增肌':
        filteredList = filteredList.filter(item => item.protein >= 15);
        break;
      case '清淡':
        filteredList = filteredList.filter(item => item.flavor === '清淡');
        break;
      case '高蛋白':
        filteredList = filteredList.filter(item => item.protein >= 20);
        break;
      case '低碳水':
        filteredList = filteredList.filter(item => item.carb <= 20);
        break;
      case '低脂肪':
        filteredList = filteredList.filter(item => item.fat <= 10);
        break;
      case '素食':
        filteredList = filteredList.filter(item => !item.ingre_list.includes('肉') && !item.ingre_list.includes('虾') && !item.ingre_list.includes('鱼'));
        break;
      case '快手菜':
        filteredList = filteredList.filter(item => item.cook_step.split(/[。\n]/).filter(step => step.trim()).length <= 3);
        break;
      case '家常菜':
        filteredList = filteredList.filter(item => item.cook_type === '炒' || item.cook_type === '煮' || item.cook_type === '炖');
        break;
      default:
        filteredList = [...this.data.recipeList];
    }

    this.setData({
      filterIndex: index,
      filteredList
    });
  },

  // 显示烹饪步骤
  showCookStep(e) {
    const item = e.currentTarget.dataset.item;
    // 将步骤文本拆分成数组（假设步骤用换行/数字分隔）
    let steps = item.cook_step.split(/\d+[、.）)）]/).filter(step => step.trim());
    // 如果拆分失败，按句号/换行拆分
    if (steps.length <= 1) {
      steps = item.cook_step.split(/[。\n]/).filter(step => step.trim());
    }

    this.setData({
      showStepDialog: true,
      currentRecipe: item,
      cookSteps: steps
    });
  },

  // 隐藏烹饪步骤弹窗
  hideStepDialog() {
    this.setData({
      showStepDialog: false,
      currentRecipe: {},
      cookSteps: []
    });
  },

  // 收藏食谱
  collectRecipe(e) {
    const recipe = e.currentTarget.dataset.item;
    const recipeId = recipe.id;
    const isCollected = this.data.collectedRecipes.includes(recipeId);

    if (isCollected) {
      // 取消收藏
      del('/recipe/collection', { recipe_id: recipeId })
        .then((result) => {
          if (result && result.code === 200) {
            const newCollectedRecipes = this.data.collectedRecipes.filter(id => id !== recipeId);
            this.setData({ collectedRecipes: newCollectedRecipes });
            wx.showToast({ title: '取消收藏成功' });
          }
        })
        .catch((err) => {
          console.error('取消收藏失败：', err);
          wx.showToast({ title: '取消收藏失败', icon: 'none' });
        });
    } else {
      // 添加收藏
      post('/recipe/collection', { recipe_id: recipeId })
        .then((result) => {
          if (result && result.code === 200) {
            this.setData({ collectedRecipes: [...this.data.collectedRecipes, recipeId] });
            wx.showToast({ title: '收藏成功' });
          }
        })
        .catch((err) => {
          console.error('收藏失败：', err);
          wx.showToast({ title: '收藏失败', icon: 'none' });
        });
    }
  },

  // 分享食谱
  shareRecipe(e) {
    const recipe = e.currentTarget.dataset.item;
    wx.shareAppMessage({
      title: recipe.recipe_name || recipe.name,
      path: `/pages/recipe-detail/recipe-detail?id=${recipe.id}`,
      desc: `推荐食谱：${recipe.recipe_name || recipe.name}，热量${recipe.calorie}大卡`,
      imageUrl: recipe.image || ''
    });
  },

  // 跳转到食谱详情
  goToRecipeDetail(e) {
    const recipe = e.currentTarget.dataset.item;
    wx.navigateTo({
      url: `/pages/recipe-detail/recipe-detail?id=${recipe.id}`
    });
  }
});