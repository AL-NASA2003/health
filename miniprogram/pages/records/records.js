// 引入请求工具、存储工具、登录守卫和模拟数据工具
const { get, post, put, del, clearRequestCache } = require('../../utils/request');
const { getUserInfo } = require('../../utils/storage');
const { loginGuard } = require('../../utils/auth');
const { loadMockData } = require('../../utils/mockData');

/**
 * 记录页面 - 包含饮食记录、饮水记录和运动记录功能
 */
Page({
  data: {
    currentTab: 'diet', // 当前标签页：diet饮食、water饮水、exercise运动
    currentDate: '',
    // ===== 饮食记录相关数据 =====
    totalCalories: 0,           // 今日摄入总热量
    dietList: [],               // 饮食记录列表
    loading: true,              // 加载状态
    searchKey: '',              // 搜索关键词
    searchSuggest: [],          // 搜索建议列表
    showAddDialog: false,       // 是否显示添加对话框
    isEdit: false,              // 是否为编辑模式
    editRecordId: null,         // 编辑的记录ID
    foodTypes: ['饮品', '菜式', '主食', '水果', '零食'],  // 食物类型列表
    mealTimes: ['早餐', '午餐', '晚餐', '加餐'],          // 用餐时间列表
    formData: {                 // 表单数据
      foodName: '',
      foodTypeIndex: 1,
      mealTimeIndex: 0,
      weight: '',
      ingredientId: ''
    },
    // ===== 饮水记录相关数据 =====
    waterRecords: [],           // 饮水记录列表
    totalWater: 0,              // 今日总饮水量
    dailyTarget: 2000,          // 每日饮水目标(ml)
    currentAmount: 0,           // 当前饮水量
    progressPercent: 0,         // 进度百分比
    remainingAmount: 2000,      // 剩余饮水量
    customAmount: '',           // 自定义饮水量
    // ===== 运动记录相关数据 =====
    exerciseRecords: [],         // 运动记录列表
    totalExerciseCalories: 0,    // 运动消耗总热量
    totalExerciseDuration: 0,    // 运动总时长
    todayCalories: 0,            // 今日运动消耗热量
    todayDuration: 0,            // 今日运动时长
    todayCount: 0,               // 今日运动次数
    exerciseTypes: [             // 运动类型列表
      { id: 1, name: '跑步', icon: '🏃', calories: 600, color: 'linear-gradient(135deg, #ff6b6b, #ee5a24)' },
      { id: 2, name: '快走', icon: '🚶', calories: 300, color: 'linear-gradient(135deg, #4ecdc4, #44a08d)' },
      { id: 3, name: '游泳', icon: '🏊', calories: 500, color: 'linear-gradient(135deg, #667eea, #764ba2)' },
      { id: 4, name: '骑行', icon: '🚴', calories: 450, color: 'linear-gradient(135deg, #f093fb, #f5576c)' },
      { id: 5, name: '跳绳', icon: '🏋️', calories: 700, color: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
      { id: 6, name: '瑜伽', icon: '🧘', calories: 250, color: 'linear-gradient(135deg, #fa709a, #fee140)' },
      { id: 7, name: '健身', icon: '💪', calories: 400, color: 'linear-gradient(135deg, #a18cd1, #fbc2eb)' },
      { id: 8, name: '篮球', icon: '🏀', calories: 550, color: 'linear-gradient(135deg, #ff9a9e, #fecfef)' }
    ],
    customName: '',              // 自定义运动名称
    customDuration: '',          // 自定义运动时长
    customCalories: ''           // 自定义运动消耗热量
  },

  /**
   * 页面加载时执行
   * @param {Object} options - 页面参数
   */
  onLoad(options) {
    // 登录检查
    if (!loginGuard()) return;
    // 初始化日期显示
    this.initDate();
    // 设置当前日期
    this.setCurrentDate();
    // 加载所有记录
    this.loadAllRecords();
  },

  /**
   * 页面显示时执行
   */
  onShow() {
    // 每次页面显示时刷新记录
    this.loadAllRecords();
  },

  /**
   * 初始化日期显示（中文格式）
   */
  initDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const currentDate = `${year}年${month}月${day}日`;
    this.setData({ currentDate });
  },

  /**
   * 设置当前日期（带星期）
   */
  setCurrentDate() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][today.getDay()];
    this.setData({
      currentDateForHeader: `${year}-${month}-${day} ${week}`
    });
  },

  goBack() {
    console.log('点击了返回按钮');
    wx.switchTab({
      url: '/pages/index/index',
      success: function(res) {
        console.log('返回首页成功', res);
      },
      fail: function(err) {
        console.log('返回首页失败', err);
      }
    });
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ currentTab: tab });
  },

  loadAllRecords() {
    // 加载饮食记录
    this.getDietList();
    
    // 加载饮水记录
    this.getWaterList();
    
    // 加载运动记录
    this.getExerciseList();
  },

  getWaterList() {
    const today = new Date().toISOString().split('T')[0];
    get('/water/record', { date: today }, false)
      .then((result) => {
        if (result && result.data && result.data.list) {
          const waterRecords = result.data.list.map(item => ({
            id: item.id,
            amount: item.amount,
            time: item.create_time.split(' ')[1]
          }));
          const totalWater = waterRecords.reduce((sum, item) => sum + item.amount, 0);
          
          this.setData({
            waterRecords: waterRecords,
            totalWater: totalWater,
            currentAmount: totalWater
          });
          
          this.updateWaterProgress();
        }
      })
      .catch((err) => {
        console.error('获取饮水记录失败：', err);
        // 加载本地存储作为备用
        const waterData = wx.getStorageSync(`water_${today}`);
        const waterRecords = waterData?.records || [];
        const totalWater = waterData?.totalAmount || 0;
        
        this.setData({
          waterRecords: waterRecords,
          totalWater: totalWater,
          currentAmount: totalWater
        });
        
        this.updateWaterProgress();
      });
  },

  getExerciseList() {
    const today = new Date().toISOString().split('T')[0];
    get('/exercise/record', { date: today }, false)
      .then((result) => {
        if (result && result.data && result.data.list) {
          const exerciseRecords = result.data.list.map(item => ({
            id: item.id,
            name: item.name,
            icon: '⚡',
            color: 'linear-gradient(135deg, #a8edea, #fed6e3)',
            duration: item.duration,
            caloriesPerHour: Math.round(item.calories / (item.duration / 60)),
            totalCalories: item.calories,
            time: item.create_time.split(' ')[1]
          }));
          
          let totalExerciseCalories = 0;
          let totalExerciseDuration = 0;
          exerciseRecords.forEach(record => {
            totalExerciseCalories += record.totalCalories || 0;
            totalExerciseDuration += record.duration || 0;
          });
          
          this.setData({
            exerciseRecords: exerciseRecords,
            totalExerciseCalories: totalExerciseCalories,
            totalExerciseDuration: totalExerciseDuration
          });
          
          this.updateExerciseStats();
        }
      })
      .catch((err) => {
        console.error('获取运动记录失败：', err);
        // 加载本地存储作为备用
        const exerciseData = wx.getStorageSync(`exercise_${today}`);
        const exerciseRecords = exerciseData?.records || [];
        
        let totalExerciseCalories = 0;
        let totalExerciseDuration = 0;
        exerciseRecords.forEach(record => {
          totalExerciseCalories += record.totalCalories || 0;
          totalExerciseDuration += record.duration || 0;
        });
        
        this.setData({
          exerciseRecords: exerciseRecords,
          totalExerciseCalories: totalExerciseCalories,
          totalExerciseDuration: totalExerciseDuration
        });
        
        this.updateExerciseStats();
      });
  },

  // ========== 饮食记录相关函数 ==========
  calculateTotalCalories(dietList) {
    let total = 0;
    dietList.forEach(item => {
      total += item.calorie || 0;
    });
    this.setData({ totalCalories: total });
  },

  getDietList() {
    const today = new Date().toISOString().split('T')[0];
    console.log('获取饮食记录，日期:', today);
    get('/diet/record', { start_date: today, end_date: today }, false)
      .then((result) => {
        console.log('获取饮食记录结果:', result);
        if (result && result.data && result.data.list) {
          const dietList = result.data.list;
          console.log('饮食记录列表:', dietList);
          this.calculateTotalCalories(dietList);
          this.setData({
            dietList,
            loading: false
          });
        } else {
          console.log('无饮食记录数据');
          this.setData({
            dietList: [],
            loading: false
          });
        }
      })
      .catch((err) => {
        console.error('获取饮食记录失败：', err);
        this.loadMockData();
      });
  },

  loadMockData() {
    const mockData = loadMockData('dietRecord').map(item => ({
      id: item.id,
      food_name: item.ingredient_id === 1 ? '番茄' : '鸡蛋',
      food_type: '菜式',
      meal_time: item.meal_type,
      weight: item.weight,
      calorie: item.ingredient_id === 1 ? 30 : 155,
      protein: item.ingredient_id === 1 ? 1.8 : 13,
      carb: item.ingredient_id === 1 ? 7.8 : 1.1,
      fat: item.ingredient_id === 1 ? 0.4 : 11,
      create_time: new Date(item.create_time).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }));

    this.calculateTotalCalories(mockData);
    this.setData({
      dietList: mockData,
      loading: false
    });
  },

  onSearchInput(e) {
    const value = e.detail.value;
    this.setData({ searchKey: value });
    
    if (value) {
      get('/ingredient/search', { keyword: value })
        .then((result) => {
          this.setData({
            searchSuggest: result.data.list || []
          });
        })
        .catch((err) => {
          console.error('搜索食材失败：', err);
        });
    } else {
      this.setData({ searchSuggest: [] });
    }
  },

  selectIngredient(e) {
    const item = e.currentTarget.dataset.item;
    this.setData({
      searchKey: item.ingre_name,
      searchSuggest: [],
      'formData.foodName': item.ingre_name,
      'formData.ingredientId': item.id
    });
  },

  searchDiet() {
    const { searchKey } = this.data;
    if (!searchKey) {
      this.getDietList();
      return;
    }
    
    const filteredList = this.data.dietList.filter(item => 
      item.food_name.includes(searchKey)
    );
    
    this.setData({
      dietList: filteredList,
      loading: false
    });
  },

  showAddDialog() {
    this.setData({ showAddDialog: true });
  },

  showEditDialog(e) {
    const item = e.currentTarget.dataset.item;
    const foodTypeIndex = this.data.foodTypes.indexOf(item.food_type);
    const mealTimeIndex = this.data.mealTimes.indexOf(item.meal_time);
    
    this.setData({
      showAddDialog: true,
      isEdit: true,
      editRecordId: item.id,
      formData: {
        foodName: item.food_name,
        foodTypeIndex: foodTypeIndex >= 0 ? foodTypeIndex : 1,
        mealTimeIndex: mealTimeIndex >= 0 ? mealTimeIndex : 0,
        weight: item.weight.toString(),
        ingredientId: item.ingredient_id || ''
      }
    });
  },

  hideAddDialog() {
    this.setData({ 
      showAddDialog: false,
      isEdit: false,
      editRecordId: null,
      formData: {
        foodName: '',
        foodTypeIndex: 1,
        mealTimeIndex: 0,
        weight: '',
        ingredientId: ''
      }
    });
  },

  onFormInput(e) {
    const key = e.currentTarget.dataset.key;
    const value = e.detail.value;
    this.setData({
      [`formData.${key}`]: value
    });
  },

  onFoodTypeChange(e) {
    this.setData({
      'formData.foodTypeIndex': e.detail.value
    });
  },

  onMealTimeChange(e) {
    this.setData({
      'formData.mealTimeIndex': e.detail.value
    });
  },

  submitDietRecord() {
    const { formData, foodTypes, mealTimes, isEdit, editRecordId } = this.data;
    
    if (!formData.foodName) {
      wx.showToast({ title: '请输入食材名称', icon: 'none' });
      return;
    }
    
    if (!formData.weight) {
      wx.showToast({ title: '请输入食用量', icon: 'none' });
      return;
    }
    
    const weightRegex = /^\d+(\.\d+)?$/;
    if (!weightRegex.test(formData.weight)) {
      wx.showToast({ title: '请输入有效的数字', icon: 'none' });
      return;
    }
    
    const weight = Number(formData.weight);
    if (weight <= 0 || weight > 10000) {
      wx.showToast({ title: '请输入0-10000之间的食用量', icon: 'none' });
      return;
    }
    
    const params = {
      food_name: formData.foodName,
      food_type: foodTypes[formData.foodTypeIndex],
      meal_time: mealTimes[formData.mealTimeIndex],
      weight: weight
    };
    
    if (formData.ingredientId) {
      params.ingredient_id = formData.ingredientId;
    }
    
    // 先在前端显示，提升用户体验
    if (isEdit && editRecordId) {
      // 编辑模式：更新前端数据
      const updatedList = this.data.dietList.map(item => {
        if (item.id === editRecordId) {
          return { ...item, ...params, calorie: params.weight * 1.1 };
        }
        return item;
      });
      this.calculateTotalCalories(updatedList);
      this.setData({ dietList: updatedList });
      this.hideAddDialog();
      wx.showToast({ title: '更新成功' });
      
      // 异步写入后端，不刷新页面
      put(`/diet/record/${editRecordId}`, params, false, false)
        .then((result) => {
          clearRequestCache(); // 清除缓存
        })
        .catch((err) => {
          console.error('更新饮食记录失败：', err);
          wx.showToast({ title: '网络同步失败', icon: 'none' });
        });
    } else {
      // 新增模式：先在前端显示
      const now = new Date();
      const newRecord = {
        id: Date.now(),
        ...params,
        calorie: params.weight * 1.1,
        protein: params.weight * 0.02,
        carb: params.weight * 0.03,
        fat: params.weight * 0.01,
        create_time: `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
      };
      
      const updatedList = [newRecord, ...this.data.dietList];
      this.calculateTotalCalories(updatedList);
      this.setData({ dietList: updatedList });
      this.hideAddDialog();
      wx.showToast({ title: '添加成功' });
      
      // 异步写入后端，不刷新页面
      post('/diet/record', params, false, false)
        .then((result) => {
          clearRequestCache(); // 清除缓存
        })
        .catch((err) => {
          console.error('添加饮食记录失败：', err);
          wx.showToast({ title: '网络同步失败', icon: 'none' });
        });
    }
  },

  deleteDietRecord(e) {
    const id = e.currentTarget.dataset.id;
    
    wx.showModal({
      title: '提示',
      content: '确定要删除这条记录吗？',
      success: (res) => {
        if (res.confirm) {
          // 先在前端删除，提升用户体验
          const updatedList = this.data.dietList.filter(item => item.id !== id);
          this.calculateTotalCalories(updatedList);
          this.setData({ dietList: updatedList });
          wx.showToast({ title: '删除成功' });
          
          // 异步调用后端删除
          del(`/diet/record/${id}`, {}, false, false)
            .then((result) => {
              clearRequestCache(); // 清除缓存
            })
            .catch((err) => {
              console.error('删除记录失败：', err);
              // 如果后端删除失败，恢复数据
              this.loadAllRecords();
              wx.showToast({ title: '网络同步失败', icon: 'none' });
            });
        }
      }
    });
  },

  // ========== 饮水记录相关函数 ==========
  updateWaterProgress() {
    const percent = Math.min((this.data.currentAmount / this.data.dailyTarget) * 100, 100);
    const remaining = Math.max(this.data.dailyTarget - this.data.currentAmount, 0);
    
    this.setData({
      progressPercent: percent.toFixed(0),
      remainingAmount: remaining
    });
  },

  saveWaterData() {
    const today = new Date().toISOString().split('T')[0];
    const data = {
      records: this.data.waterRecords,
      totalAmount: this.data.currentAmount
    };
    wx.setStorageSync(`water_${today}`, data);
  },

  addWater(e) {
    const amount = parseInt(e.currentTarget.dataset.amount);
    this.addWaterAmount(amount);
  },

  onCustomAmountInput(e) {
    this.setData({
      customAmount: e.detail.value
    });
  },

  addCustomWater() {
    const amount = parseInt(this.data.customAmount);
    
    if (!amount || amount <= 0) {
      wx.showToast({
        title: '请输入有效的水量',
        icon: 'none'
      });
      return;
    }
    
    this.addWaterAmount(amount);
    this.setData({ customAmount: '' });
  },

  addWaterAmount(amount) {
    // 先在前端显示，提升用户体验
    const now = new Date();
    const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    
    const newRecord = {
      id: Date.now(),
      amount: amount,
      time: time
    };
    
    const newRecords = [newRecord, ...this.data.waterRecords];
    const newTotal = this.data.currentAmount + amount;
    
    this.setData({
      waterRecords: newRecords,
      currentAmount: newTotal,
      totalWater: newTotal
    });
    
    this.updateWaterProgress();
    
    wx.showToast({
      title: `已添加 ${amount}ml`,
      icon: 'success'
    });
    
    // 检查是否完成目标
    if (newTotal >= this.data.dailyTarget && 
        this.data.currentAmount < this.data.dailyTarget) {
      setTimeout(() => {
        wx.showModal({
          title: '恭喜！',
          content: '您已完成今日饮水目标！',
          showCancel: false
        });
      }, 1000);
    }
    
    // 异步写入后端，不刷新页面
    post('/water/record', { amount: amount }, false, false)
      .then((result) => {
        clearRequestCache(); // 清除缓存
      })
      .catch((err) => {
        console.error('添加饮水记录失败：', err);
        wx.showToast({ title: '网络同步失败', icon: 'none' });
      });
  },

  deleteWaterRecord(e) {
    const index = e.currentTarget.dataset.index;
    const record = this.data.waterRecords[index];
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除这条 ${record.amount}ml 的记录吗？`,
      success: (res) => {
        if (res.confirm) {
          // 先在前端删除，提升用户体验
          const newRecords = [...this.data.waterRecords];
          newRecords.splice(index, 1);
          const newTotal = Math.max(0, this.data.currentAmount - record.amount);
          
          this.setData({
            waterRecords: newRecords,
            currentAmount: newTotal,
            totalWater: newTotal
          });
          
          this.updateWaterProgress();
          wx.showToast({ title: '删除成功', icon: 'success' });
          
          // 如果有ID，异步调用后端删除
          if (record.id) {
            del(`/water/record/${record.id}`, {}, false, false)
              .then((result) => {
                clearRequestCache(); // 清除缓存
              })
              .catch((err) => {
                console.error('删除饮水记录失败：', err);
                // 如果后端删除失败，恢复数据
                this.loadAllRecords();
                wx.showToast({ title: '网络同步失败', icon: 'none' });
              });
          }
        }
      }
    });
  },

  // ========== 运动记录相关函数 ==========
  updateExerciseStats() {
    let totalCalories = 0;
    let totalDuration = 0;
    
    this.data.exerciseRecords.forEach(record => {
      totalCalories += record.totalCalories;
      totalDuration += record.duration;
    });
    
    this.setData({
      todayCalories: totalCalories,
      todayDuration: totalDuration,
      todayCount: this.data.exerciseRecords.length
    });
  },

  addExercise(e) {
    const exerciseType = e.currentTarget.dataset.type;
    
    wx.showModal({
      title: `添加${exerciseType.name}`,
      editable: true,
      placeholderText: '请输入运动时长(分钟)',
      success: (res) => {
        if (res.confirm) {
          const duration = parseInt(res.content);
          if (!duration || duration <= 0) {
            wx.showToast({
              title: '请输入有效的时长',
              icon: 'none'
            });
            return;
          }
          
          this.addExerciseRecord(exerciseType, duration);
        }
      }
    });
  },

  onCustomNameInput(e) {
    this.setData({ customName: e.detail.value });
  },

  onCustomDurationInput(e) {
    this.setData({ customDuration: e.detail.value });
  },

  onCustomCaloriesInput(e) {
    this.setData({ customCalories: e.detail.value });
  },

  addCustomExercise() {
    const { customName, customDuration, customCalories } = this.data;
    
    if (!customName.trim()) {
      wx.showToast({
        title: '请输入运动名称',
        icon: 'none'
      });
      return;
    }
    
    const duration = parseInt(customDuration);
    if (!duration || duration <= 0) {
      wx.showToast({
        title: '请输入有效的时长',
        icon: 'none'
      });
      return;
    }
    
    const calories = parseInt(customCalories);
    if (!calories || calories <= 0) {
      wx.showToast({
        title: '请输入有效的热量消耗',
        icon: 'none'
      });
      return;
    }
    
    const customType = {
      name: customName,
      icon: '⚡',
      calories: calories,
      color: 'linear-gradient(135deg, #a8edea, #fed6e3)'
    };
    
    this.addExerciseRecord(customType, duration);
    
    this.setData({
      customName: '',
      customDuration: '',
      customCalories: ''
    });
  },

  addExerciseRecord(exerciseType, duration) {
    const totalCalories = Math.round((exerciseType.calories / 60) * duration);
    
    // 先在前端显示，提升用户体验
    const now = new Date();
    const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    
    const newRecord = {
      id: Date.now(),
      name: exerciseType.name,
      icon: exerciseType.icon,
      color: exerciseType.color,
      duration: duration,
      caloriesPerHour: exerciseType.calories,
      totalCalories: totalCalories,
      time: time
    };
    
    const newRecords = [newRecord, ...this.data.exerciseRecords];
    
    this.setData({
      exerciseRecords: newRecords,
      totalExerciseCalories: this.data.totalExerciseCalories + totalCalories,
      totalExerciseDuration: this.data.totalExerciseDuration + duration
    });
    
    this.updateExerciseStats();
    
    wx.showToast({
      title: `已记录 ${exerciseType.name} ${duration}分钟`,
      icon: 'success'
    });
    
    // 异步写入后端，不刷新页面
    post('/exercise/record', { 
      name: exerciseType.name, 
      duration: duration, 
      calories: totalCalories 
    }, false, false)
      .then((result) => {
        clearRequestCache(); // 清除缓存
      })
      .catch((err) => {
        console.error('添加运动记录失败：', err);
        wx.showToast({ title: '网络同步失败', icon: 'none' });
      });
  },

  saveExerciseData() {
    const today = new Date().toISOString().split('T')[0];
    const data = {
      records: this.data.exerciseRecords
    };
    wx.setStorageSync(`exercise_${today}`, data);
  },

  deleteExerciseRecord(e) {
    const index = e.currentTarget.dataset.index;
    const record = this.data.exerciseRecords[index];
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除这条 ${record.name} 记录吗？`,
      success: (res) => {
        if (res.confirm) {
          // 先在前端删除，提升用户体验
          const newRecords = [...this.data.exerciseRecords];
          newRecords.splice(index, 1);
          
          this.setData({
            exerciseRecords: newRecords,
            totalExerciseCalories: this.data.totalExerciseCalories - record.totalCalories,
            totalExerciseDuration: this.data.totalExerciseDuration - record.duration
          });
          
          this.updateExerciseStats();
          wx.showToast({ title: '删除成功', icon: 'success' });
          
          // 如果有ID，异步调用后端删除
          if (record.id) {
            del(`/exercise/record/${record.id}`, {}, false, false)
              .then((result) => {
                clearRequestCache(); // 清除缓存
              })
              .catch((err) => {
                console.error('删除运动记录失败：', err);
                // 如果后端删除失败，恢复数据
                this.loadAllRecords();
                wx.showToast({ title: '网络同步失败', icon: 'none' });
              });
          }
        }
      }
    });
  }
});
